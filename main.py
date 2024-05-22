import streamlit as st
from edgar import set_identity

from constants import COMPANY_NAME, DISCLAIMER, EMAIL, TICKERS
from generate import get_company_financials
from ui import display_financial_data, setup_sidebar
from utils import get_10k_filing_texts

st.set_page_config(page_title="10-K Filing Analysis", page_icon="📈", layout="wide")


def main():
    set_identity(f"{COMPANY_NAME} {EMAIL}")  # for downloading filings from EDGAR

    # extract options/settings from sidebar
    options = setup_sidebar(TICKERS)
    ticker = options["ticker"]
    st.header(f"{ticker}'s Key Numbers Over Time", divider="rainbow")
    st.markdown(DISCLAIMER)

    # fetch 10-K filings and extract financial data points
    res = get_10k_filing_texts(ticker)
    financials = get_company_financials(res, cache=(not options["reset_cache"]))

    if options["reset_cache"]:
        st.cache_data.clear()

    # display financial data
    display_financial_data(financials, ticker, table=(options["view"] == "Table"))


if __name__ == "__main__":
    main()
