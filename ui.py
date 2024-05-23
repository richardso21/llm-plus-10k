from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st
from altair import List

from constants import DATA_DISPLAY_MODES, DISCLAIMER, MODES, SECTIONS
from generate import CompanyFinancials, summarize_filing_document
from utils import CompanyFilingTexts


def setup_sidebar(tickers: List[str]) -> Dict[str, str]:
    """Setup the sidebar layout, including title, notes, settings, etc..

    Includes setup for additional menu options for the "Analysis" mode.
    Returns a dictionary containing all selected options.
    """
    st.sidebar.title("LLM + 10-K")
    st.sidebar.subheader("_Analysis of 10-K Filings with the power of LLM's_")
    st.sidebar.markdown("##### _By Richard So_")

    st.sidebar.markdown("---")

    st.sidebar.markdown("## Display Options")
    res = {}

    res["ticker"] = st.sidebar.selectbox("Company/Ticker", tickers)

    mode_option = st.sidebar.radio("Mode", MODES)
    res["mode"] = mode_option

    # show extra options for "Analyze" mode
    if mode_option == "Analyze":
        # graph or table view
        res["view"] = st.sidebar.radio("Data View", DATA_DISPLAY_MODES)

        # edit financial items for analysis

        # rerun/reset button
        res["reset_findata_cache"] = st.sidebar.button(
            "**Rerun LLM & Reset Data Cache**",
            type="primary",
            help="WARNING: This will take a (long) while!",
            use_container_width=True,
        )
    else:
        res["view"] = None

    st.sidebar.write("#")
    st.sidebar.markdown(DISCLAIMER)

    return res


def display_financial_data(
    financials: CompanyFinancials, ticker: str, table: bool = False
) -> None:
    """Display financial data as either a graph or a table."""
    # convert CompanyFinancials dictionary into dataframe
    graph_data = pd.DataFrame.from_dict(financials, orient="index")

    # sort columns for consistency, and get column title names
    chart_options = sorted(graph_data.columns.tolist())
    chart_option_names = [opt.replace("_", " ").title() for opt in chart_options]

    # turn year index into column for plotly
    graph_data.index.name = "year"
    graph_data.reset_index(inplace=True)

    if table:  # display as a table instead
        # rename df columns
        graph_data.columns = ["Year"] + chart_option_names
        # get rid of commas in year value
        graph_data["Year"] = graph_data["Year"].astype(str)
        # display table
        st.dataframe(graph_data, use_container_width=True, hide_index=True, height=600)
        return

    # display as a graph
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


def display_summarizer(filings: CompanyFilingTexts, stream: bool = True) -> None:
    """Display the summarizer interface for 10-K filings."""
    summarizer_options = st.form(key="summarizer_options")
    c1, c2 = summarizer_options.columns(2)

    section_name = c1.selectbox("Section", ["Business", "Risk", "MD&A", "Financials"])
    if not section_name:
        section_name = "Business"

    year = c2.selectbox("Year", list(filings.keys()))
    if not year:
        year = list(filings.keys())[0]

    c3, c4 = summarizer_options.columns([0.8, 0.2])
    override_instr = c3.text_input("Override Instructions")
    c4.write("####")  # offset the button lower to align with the text input
    submitted = c4.form_submit_button(
        "Summarize",
        help="Summarize the selected section and year of the 10-K filing.",
        use_container_width=True,
    )
    if not submitted:
        return

    section_code = SECTIONS[section_name]
    document = filings[year][section_code]

    if not document:
        # section does not exist for the filing (e.g. no "Risk" section in earlier 10-K filings)
        st.error(f"No {section_name} section found for the filing year of {year}.")
        return

    gen_res = summarize_filing_document(
        document,
        section_name,
        filings.ticker,
        year,
        override_instr=override_instr,
        stream=stream,
    )

    if stream:
        st.write_stream(gen_res)
    else:
        st.write(gen_res)
