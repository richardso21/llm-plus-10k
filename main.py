import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from edgar import set_identity

from constants import COMPANY_NAME, EMAIL, TICKERS
from generate import get_company_financials
from ui import plot_financial_data, setup_sidebar
from utils import get_10k_filing_texts

st.set_page_config(page_title="10-K Filings Analysis", page_icon="📈", layout="wide")


def main():
    set_identity(f"{COMPANY_NAME} {EMAIL}")  # for downloading filings from EDGAR

    options = setup_sidebar(TICKERS)
    ticker = options["ticker"]
    st.title(f"{ticker}'s Key Numbers Over Time")

    res = get_10k_filing_texts(ticker)
    financials = get_company_financials(res, cache=(not options["reset_cache"]))

    if options["reset_cache"]:
        st.cache_data.clear()

    plot_financial_data(financials, ticker)


if __name__ == "__main__":
    main()
