import streamlit as st
from edgar import set_identity

from constants import COMPANY_NAME, EMAIL, TICKERS
from generate import get_company_financials
from ui import display_financial_data, display_summarizer, setup_sidebar
from utils import get_10k_filing_texts

st.set_page_config(page_title="LLM + 10-K", page_icon="📈", layout="wide")
set_identity(f"{COMPANY_NAME} {EMAIL}")  # for downloading filings from EDGAR


def main():
    """Entry point for the Streamlit application."""
    # display sidebar and extract selected options/settings from it
    options = setup_sidebar(TICKERS)
    ticker = options["ticker"]
    mode = options["mode"]

    filings = get_10k_filing_texts(ticker)

    # title in main content area
    st.header(
        (
            f"{ticker}'s Numbers Over Time"
            if mode == "Analyze"
            else f"{ticker} 10-K Filings Summarizer"
        ),
        divider="rainbow",
    )

    # change main content based on selected mode
    if options["mode"] == "Analyze":
        # fetch 10-K filings and extract financial data points
        items = [i.strip() for i in options["fin_items"].strip().split("\n")]
        financials = get_company_financials(
            filings, cache=(not options["reset_findata_cache"]), items=items
        )
        if options["reset_findata_cache"]:
            st.cache_data.clear()
        # display financial data
        display_financial_data(financials, ticker, table=(options["view"] == "Table"))
    else:
        # display summarizer
        display_summarizer(filings)


if __name__ == "__main__":
    main()
