from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import logging
from groq import Groq
from textblob import TextBlob
import yfinance as yf
import pandas as pd

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

# ─── Helper Functions ────────────────────────────────────────────────────────

def fetch_stock_symbol(company_name):
    """Resolve a company name or symbol to a valid ticker using yfinance search."""
    common_names = {
        "tesla": "TSLA", "apple": "AAPL", "google": "GOOGL", "alphabet": "GOOGL",
        "amazon": "AMZN", "microsoft": "MSFT", "meta": "META", "facebook": "META",
        "netflix": "NFLX", "nvidia": "NVDA", "amd": "AMD", "intel": "INTC",
        "ibm": "IBM", "oracle": "ORCL", "salesforce": "CRM", "adobe": "ADBE",
        "paypal": "PYPL", "uber": "UBER", "spotify": "SPOT", "airbnb": "ABNB",
        "disney": "DIS", "coca-cola": "KO", "pepsi": "PEP", "walmart": "WMT",
        "nike": "NKE", "boeing": "BA", "jpmorgan": "JPM", "visa": "V",
        "mastercard": "MA", "samsung": "005930.KS", "tata": "TATAMOTORS.NS",
        "reliance": "RELIANCE.NS", "infosys": "INFY", "wipro": "WIPRO.NS",
        "suzlon": "SUZLON.NS",
    }

    name_lower = company_name.strip().lower().rstrip(".")
    for suffix in [" inc", " corp", " ltd", " limited", " llc", " co", " plc", " group"]:
        name_lower = name_lower.replace(suffix, "")
    name_lower = name_lower.strip()

    if name_lower in common_names:
        return common_names[name_lower]

    cleaned = company_name.strip().upper()
    if len(cleaned) <= 6 and cleaned.isalpha() and " " not in cleaned:
        ticker = yf.Ticker(cleaned)
        try:
            hist = ticker.history(period="1d")
            if not hist.empty:
                return cleaned
        except Exception:
            pass

    try:
        results = yf.Search(company_name, max_results=5)
        if hasattr(results, 'quotes') and results.quotes:
            return results.quotes[0].get("symbol", company_name.upper())
    except Exception as e:
        logging.error(f"Error searching for stock symbol: {e}")

    return company_name.upper()

def fetch_current_price(stock_symbol):
    try:
        ticker = yf.Ticker(stock_symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)
        return None
    except Exception as e:
        logging.error(f"Error fetching price for {stock_symbol}: {e}")
        return None

def get_stock_data(stock_symbol, period="5d", interval="5m"):
    try:
        ticker = yf.Ticker(stock_symbol)
        hist = ticker.history(period=period, interval=interval)
        return hist
    except Exception as e:
        logging.error(f"Error fetching stock data for {stock_symbol}: {e}")
        return pd.DataFrame()

def calculate_rsi(stock_data, window=14):
    if stock_data is None or stock_data.empty or len(stock_data) < window + 1:
        return None
    closes = stock_data["Close"]
    delta = closes.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.dropna().iloc[-1] if not rsi.dropna().empty else None
    return round(latest_rsi, 2) if latest_rsi is not None else None

def fetch_news(stock):
    try:
        ticker = yf.Ticker(stock)
        news = ticker.news
        if news:
            headlines = []
            for item in news[:5]:
                content = item.get("content", item)
                title = content.get("title", "")
                provider = content.get("provider", {})
                publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
                if title:
                    headlines.append(f"{title} — {publisher}" if publisher else title)
            return headlines if headlines else ["No recent news found."]
        return ["No recent news found."]
    except Exception as e:
        logging.error(f"Error fetching news for {stock}: {e}")
        return [f"Failed to fetch news: {e}"]

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        return {"compound": round(blob.sentiment.polarity, 4)}
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return {"compound": 0}

def query_llm(stock, rsi, sentiment, news_summary):
    if not client:
        return {"decision": "Unavailable — GROQ_API_KEY not set", "explanation": "Please set your Groq API key in the .env file."}
    rsi_text = f"{rsi:.2f}" if rsi is not None else "Unavailable"
    prompt = f"""
    You are a professional stock market analyst. Analyze the following data and provide a clear recommendation.

    Stock: {stock}
    RSI (14-period): {rsi_text}
    Sentiment Score: {sentiment['compound']}
    Recent News: {news_summary}

    Provide:
    1. A clear recommendation: BUY, SELL, or HOLD
    2. Your reasoning in 3-5 concise bullet points
    3. Key risk factors to consider
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        result = response.choices[0].message.content
        return {"decision": result, "explanation": result}
    except Exception as e:
        logging.error(f"Error querying LLM: {e}")
        return {"decision": "Error contacting AI", "explanation": str(e)}

# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/live-prices", methods=["GET"])
def live_prices():
    symbols = ["TSLA", "AAPL", "GOOGL", "AMZN", "MSFT"]
    prices = {}
    for sym in symbols:
        prices[sym] = fetch_current_price(sym)
    return jsonify(prices)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    user_input = data.get("stock", "")
    
    if not user_input.strip():
        return jsonify({"error": "Please enter a company name or stock symbol."}), 400

    stock_symbol = fetch_stock_symbol(user_input.strip())
    
    # Fetch Data
    stock_data = get_stock_data(stock_symbol)
    rsi = calculate_rsi(stock_data)
    news = fetch_news(stock_symbol)
    news_summary = " ".join(news)
    sentiment = analyze_sentiment(news_summary)
    price = fetch_current_price(stock_symbol)
    
    # Query AI
    llm_response = query_llm(stock_symbol, rsi, sentiment, news_summary)
    
    return jsonify({
        "stock": stock_symbol,
        "price": price,
        "rsi": rsi,
        "sentiment": sentiment,
        "news": news,
        "llm": llm_response
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)