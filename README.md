# 🤖 AI Stock Market Agent

An intelligent stock market analysis web application powered by **Flask**, **Groq LLM (LLaMA 3.3 70B)**, **yfinance**, and **TextBlob**. It combines real-time stock data, RSI technical analysis, and news sentiment to deliver AI-driven Buy / Sell / Hold recommendations directly in the browser.

---

## 📸 Preview

> The app runs as a single-page web UI served by Flask. Users enter a company name or ticker symbol and receive a full analysis report in seconds.

---

## 🧠 How It Works

```
User Input (Company Name / Ticker)
         │
         ▼
  Symbol Resolution (yfinance Search + Lookup Map)
         │
         ▼
  ┌──────────────────────────────────────────┐
  │  Data Fetching (yfinance)                │
  │  • 5-day / 5-minute OHLCV history        │
  │  • Current live price                    │
  │  • Latest news headlines (up to 5)       │
  └──────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────┐
  │  Analysis Layer                          │
  │  • RSI (14-period) calculation           │
  │  • TextBlob sentiment scoring on news    │
  └──────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────┐
  │  Groq LLM (LLaMA 3.3 70b-versatile)     │
  │  • Synthesises RSI + sentiment + news    │
  │  • Returns BUY / SELL / HOLD decision    │
  │  • Provides 3–5 bullet reasoning points  │
  │  • Lists key risk factors                │
  └──────────────────────────────────────────┘
         │
         ▼
  JSON Response → Browser UI (HTML/CSS/JS)
```

---

## ✨ Features

- **Smart Symbol Resolution** — Accepts natural-language company names (e.g., "Tesla", "Reliance") and resolves them to the correct ticker. Supports US, NSE (`.NS`), and KSE (`.KS`) markets via a built-in name map and yfinance search fallback.
- **Live Price Sidebar** — Auto-fetches current prices for TSLA, AAPL, GOOGL, AMZN, MSFT on page load via `/api/live-prices`.
- **RSI Technical Indicator** — Calculates the 14-period Relative Strength Index from intraday (5-minute) OHLCV data to gauge overbought/oversold conditions.
- **News Sentiment Analysis** — Fetches up to 5 recent news headlines per stock via yfinance and scores them using TextBlob's polarity model.
- **AI-Powered Recommendation** — Sends structured context (stock, RSI, sentiment score, news) to Groq's `llama-3.3-70b-versatile` model, which returns a BUY / SELL / HOLD decision with detailed bullet-point reasoning and risk factors.
- **Responsive Web UI** — Custom HTML/CSS/JS frontend with no external frontend framework required (served via Flask's `render_template`).
- **Unit Tests** — `test_app.py` covers the `/analyze` endpoint using Python's built-in `unittest` framework.

---

## 🗂️ Project Structure

```
AI-Stock-Market-Agent/
│
├── app.py               # Flask backend — API routes, all analysis logic
├── requirements.txt     # Python dependencies
├── test_app.py          # Unit tests for the Flask app
├── static/              # CSS, JavaScript, and static assets for the frontend
│   └── ...
└── README.md
```

> **Note:** The HTML template (`index.html`) is served by Flask via `render_template` and lives inside a `templates/` directory (standard Flask convention).

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Serves the main web UI |
| `GET`  | `/api/live-prices` | Returns current prices for 5 major stocks as JSON |
| `POST` | `/api/analyze` | Accepts `{"stock": "<name or ticker>"}`, returns full analysis |

### `/api/analyze` Response Schema

```json
{
  "stock":     "TSLA",
  "price":     245.67,
  "rsi":       58.34,
  "sentiment": { "compound": 0.12 },
  "news":      ["Headline 1 — Publisher", "Headline 2 — Publisher"],
  "llm": {
    "decision":    "BUY / SELL / HOLD + reasoning",
    "explanation": "Full LLM response text"
  }
}
```

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask |
| AI / LLM | Groq API — `llama-3.3-70b-versatile` |
| Market Data | yfinance |
| Sentiment | TextBlob |
| Data Wrangling | pandas |
| Config | python-dotenv |
| Testing | Python `unittest` |
| Frontend | HTML, CSS, JavaScript (static files) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip
- A [Groq API key](https://console.groq.com/) (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/Darshan765/AI-Stock-Market-Agent.git
cd AI-Stock-Market-Agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY="your_groq_api_key_here"
```

> The app uses **Groq** (not Google Gemini or Alpha Vantage as mentioned in the old README). Only `GROQ_API_KEY` is required.

### 5. Run the Application

```bash
python app.py
```

The server starts on **http://localhost:5000** by default.

Open your browser and navigate to `http://localhost:5000`.

---

## 🖥️ Usage

1. The sidebar automatically loads live prices for TSLA, AAPL, GOOGL, AMZN, and MSFT.
2. Enter a **company name** (e.g., `Tesla`, `Reliance`, `Apple`) or a **ticker symbol** (e.g., `TSLA`, `AAPL`, `INFY`) in the input field.
3. Click **Analyze Stock**.
4. The app returns:
   - Current stock price
   - RSI value with overbought/oversold context
   - Sentiment score derived from recent news headlines
   - Top 5 news headlines
   - AI-generated BUY / SELL / HOLD recommendation with reasoning

### Supported Exchanges

The built-in name map supports a wide range of stocks including:

- **US markets** — TSLA, AAPL, GOOGL, AMZN, MSFT, META, NFLX, NVDA, AMD, INTC, and more
- **Indian markets (NSE)** — RELIANCE, TATAMOTORS, WIPRO, INFY, SUZLON
- **Korean markets (KSE)** — Samsung (005930.KS)

Any ticker not in the map is resolved automatically via `yfinance.Search`.

---

## 🧪 Running Tests

```bash
python -m unittest test_app.py
```

The test suite uses Flask's built-in test client and verifies that the `/analyze` endpoint returns a `200` status and includes all expected keys (`stock`, `rsi`, `sentiment`, `news_summary`, `llm_decision`, `llm_reasoning`).

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for LLaMA 3.3 70B inference |

---

## 📦 Dependencies

```
flask
requests
yfinance
python-dotenv
groq
textblob
pandas
```

Install all at once with:

```bash
pip install -r requirements.txt
```

---

## ⚠️ Disclaimer

This application is intended **for educational and informational purposes only**. The AI-generated recommendations (BUY / SELL / HOLD) are based on limited technical indicators and news sentiment and should **not** be used as financial advice. Always consult a qualified financial advisor before making investment decisions.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request
