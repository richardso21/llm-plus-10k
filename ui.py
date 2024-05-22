from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from altair import List

from constants import MODEL
from generate import CompanyFinancials


def setup_sidebar(tickers: List[str]) -> Dict[str, str]:
    st.sidebar.title("LLM Analysis of 10-K Filings")
    st.sidebar.markdown("## Display Options")
    res = {}

    comp_option = st.sidebar.selectbox("Select Company", tickers)
    res["ticker"] = comp_option

    st.sidebar.markdown("---")

    res["reset_cache"] = st.sidebar.button(
        "**Reset Cache**",
        type="primary",
        help="Reset LLM response cache of 10-K filings. WARNING: This will take a while.",
    )

    return res


def plot_financial_data(financials: CompanyFinancials, ticker: str) -> None:

    # convert financial data into dataframe
    graph_data = pd.DataFrame.from_dict(financials, orient="index")

    chart_options = sorted(graph_data.columns.tolist())
    chart_option_names = [opt.replace("_", " ").title() for opt in chart_options]

    graph_data.index.name = "year"
    graph_data.reset_index(inplace=True)

    for chart_option, chart_option_name in zip(chart_options, chart_option_names):
        line = px.line(
            graph_data,
            x="year",
            y=chart_option,
            title=f"{ticker} {chart_option_name} Over Time",
            labels={chart_option: f"{chart_option_name} (USD)", "year": "Year"},
            markers=True,
        )
        st.plotly_chart(line, use_container_width=True)

    # disclaimer
    st.markdown(
        f"_Note: All financial data is extracted from 10-K filings derived \
        from the SEC EDGAR database using a LLM ({MODEL}). Data points may \
        not be 100% accurate, refer to the filings for further information \
        and/or clarification._"
    )
