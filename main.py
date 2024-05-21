import streamlit as st
from edgar import set_identity

from generate import get_company_financials
from utils import get_10k_filing_texts

COMPANY_NAME = "Georgia Institute of Technology"
EMAIL = "so@gatech.edu"

TICKERS = ["AMZN", "AAPL", "TSLA"]


def main():
    st.write("Hello World!")
    set_identity(f"{COMPANY_NAME} {EMAIL}")  # for downloading filings from EDGAR

    d = {}
    for t in TICKERS:
        res = get_10k_filing_texts(t)
        d[res.ticker] = get_company_financials(res)

    st.write(d)


if __name__ == "__main__":
    main()
