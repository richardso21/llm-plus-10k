from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st
from altair import List

from constants import DATA_DISPLAY_MODES, MODEL, MODES, SECTIONS
from generate import CompanyFinancials


def setup_sidebar(tickers: List[str]) -> Dict[str, str]:
    """Setup the sidebar with viewing and ticker options.

    Returns a dictionary containing the selected options.
    """
    st.sidebar.title("LLM Analysis of 10-K Filings")
    st.sidebar.markdown("##### _By Richard So_")
    st.sidebar.markdown("## Display Options")
    res = {}

    res["ticker"] = st.sidebar.selectbox("Company/Ticker", tickers)

    mode_option = st.sidebar.radio("Mode", MODES)
    res["mode"] = mode_option

    if mode_option == "Analyze":
        view_option = st.sidebar.radio("Data View", DATA_DISPLAY_MODES)
        res["view"] = view_option
    else:
        res["view"] = None

    if mode_option == "Summarize":
        section_option = st.sidebar.selectbox("Section", SECTIONS.keys())
        if not section_option:
            section_option = "Business"
        res["section"] = SECTIONS[section_option]

    st.sidebar.markdown("---")

    res["reset_cache"] = st.sidebar.button(
        "**Reset Cache/Rerun LLM**",
        type="primary",
        help="WARNING: This will take a (long) while!",
        use_container_width=True,
    )

    return res


def display_financial_data(
    financials: CompanyFinancials, ticker: str, table: bool = False
) -> None:
    """Display financial data as either a graph or a table."""
    # convert financial data into dataframe
    graph_data = pd.DataFrame.from_dict(financials, orient="index")

    chart_options = sorted(graph_data.columns.tolist())
    chart_option_names = [opt.replace("_", " ").title() for opt in chart_options]

    graph_data.index.name = "year"
    graph_data.reset_index(inplace=True)

    if table:  # display as a table instead
        # rename columns
        graph_data.columns = ["Year"] + chart_option_names
        # get rid of commas in year value
        graph_data["Year"] = graph_data["Year"].astype(str)
        st.dataframe(graph_data, use_container_width=True, hide_index=True, height=600)
        return

    for chart_option, chart_option_name in zip(chart_options, chart_option_names):
        line = px.line(
            graph_data,
            x="year",
            y=chart_option,
            title=f"{ticker} {chart_option_name}",
            labels={chart_option: f"{chart_option_name} (USD)", "year": "Year"},
            markers=True,
        )
        st.plotly_chart(line, use_container_width=True)
