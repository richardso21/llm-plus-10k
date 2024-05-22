COMPANY_NAME = "Georgia Institute of Technology"
EMAIL = "so@gatech.edu"

TICKERS = ["AMZN", "AAPL", "TSLA"]

MODEL = "gemini-1.5-flash-latest"
PREAMBLE = "You are an AI assistant specializing in financial information retrieval and analysis."
DEFAULT_ITEMS = ["net sales", "gross margin", "total cost of operation"]

MODES = ["Analyze", "Summarize"]
DATA_DISPLAY_MODES = ["Graph", "Table"]

SECTIONS = {
    "Business": "business",
    "Risk": "risk",
    "MD&A": "mda",
    "Financials": "financials",
}

DISCLAIMER = f"_**Note**: All financial data and text generations is derived \
    from 10-K filings derived from the SEC EDGAR database using a LLM \
    (**{MODEL}**). Data points and summarizations may not be 100% accurate, \
    and missing data points indicate that the LLM was unable to retrieve \
    the relevant information from the filing in the relevant year. \
    Refer to the filings for further clarification._"
