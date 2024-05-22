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
    st.title(f"{ticker} 10-K Filings Analysis")

    res = get_10k_filing_texts(ticker)
    financials = get_company_financials(res, cache=(not options["reset_cache"]))

    if options["reset_cache"]:
        st.cache_data.clear()

    plot_financial_data(financials, ticker)

    # plot graph
    # graph_data = {}
    # for year in financials:
    #     val = financials[year][chart_option]
    #     graph_data[year] = val
    # graph_data = pd.DataFrame.from_dict(
    #     graph_data, orient="index", columns=np.array([chart_option])
    # )
    # graph_data.index.name = "year"
    # graph_data.reset_index(inplace=True)
    # chart_option_name = CHART_OPTION_INVMAP[chart_option]
    # line = px.line(
    #     graph_data,
    #     x="year",
    #     y=chart_option,
    #     title=f"{ticker} {chart_option_name} Over Time",
    #     labels={chart_option: f"{chart_option_name} (USD)", "year": "Year"},
    #     markers=True,
    # )
    # st.plotly_chart(line, use_container_width=True)

    # tab.line_chart(graph_data)


if __name__ == "__main__":
    main()
