import hashlib
import json
import os
import pickle
import time
from pathlib import Path
from typing import Dict, List

import google.generativeai as genai
import streamlit as st
from tqdm import tqdm

from constants import DEFAULT_ITEMS, MODEL, PREAMBLE
from utils import CompanyFilingTexts

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name=MODEL, system_instruction=PREAMBLE)


Financials = Dict[str, int | None]
CompanyFinancials = Dict[int, Financials]


def get_document_financials(
    document: str,
    items: List[str] = DEFAULT_ITEMS,
) -> Financials:
    """Extract relevant financial information from a given text document.

    The function accepts an optional `items` dictionary containing a list of
    strings describing the financial information to be extracted from the
    document (e.g. ["net sales", "gross margin", "total cost of operation"]).
    The text document should typically be the Financial Statements and
    Supplementary Data section of a company's 10-K form. The function returns
    a dictionary mapping each item to its corresponding value in the document.

    Retrieval is done using one of Google's Gemini LLM models.
    """

    # generate a request string from items
    request_str = ", ".join([f"{item} (`{item.replace(' ', '_')}`)" for item in items])

    fails = 0
    gen_res = None
    while fails < 3 and not gen_res:
        try:
            gen_res = model.generate_content(
                f"## Instructions \n \
                Given the following financial document, in the relevant year, \
                what is the company's: {request_str}? \
                Return each value in US dollars without commas. For example, \
                if the document states a statistic as being $420,000 in millions \
                of dollars, return 420000000000. If you cannot find adequate \
                information for a particular requested value, reply 'N/A' instead. \
                \n\n ## Document \n {document}",
                generation_config={"response_mime_type": "application/json"},
            )  # result should be a JSON string
        except (
            Exception
        ) as e:  # we might've hit the API limit, so wait before trying again
            fails += 1
            if fails >= 3:
                raise e
            print(f"Failed to generate content, retrying in 30 seconds... ({fails}/3)")
            time.sleep(30)

    if not gen_res:
        raise Exception("Failed to generate content")

    json_res = json.loads(gen_res.text)

    # convert all values to integers or None
    for key in json_res:
        json_res[key] = int(json_res[key]) if json_res[key] != "N/A" else None

    return json_res


@st.cache_data
def get_company_financials(
    filings: CompanyFilingTexts,
    items: List[str] = DEFAULT_ITEMS,
    cache: bool = True,
    cache_dir: str = ".cache/",
) -> CompanyFinancials:
    """Retrieve financial information from a company's 10-K filings.

    The function accepts a dictionary of 10-K filings, where the keys are the
    years and the values are the full text of the filings. The function returns
    a dictionary mapping every two years (to stay under the API limit) to a
    dictionary containing the extracted financial information for that year
    retrieved using Google Gemini.

    By default, the function will retrieve the extracted financial
    information from a pickle file in the cache directory. The pickle file
    saves retrieved information for each unique `items` query. Set `cache` to
    `False` to retrieve the information directly from the API instead
    (this will take significantly longer to run).
    """
    save_dict = {}
    # check cache for saved company financials
    cache_full_dir = Path(os.getcwd(), cache_dir)
    pkl_path = Path(
        cache_full_dir,
        f"{filings.ticker}_financials.pkl",
    )
    if cache and Path.exists(pkl_path):
        save_dict = pickle.load(open(pkl_path, "rb"))

    # see if items query is cached
    items_query_hash = hashlib.md5(
        str(sorted(items)).encode()
    ).hexdigest()  # hash() is inconsistent b/w runs, so use hashlib.md5
    if items_query_hash in save_dict:
        return save_dict[items_query_hash]

    res = {}
    years = list(filings.keys())
    for i in tqdm(
        range(0, len(years), 2), desc=f"Extracting Financials from {filings.ticker}"
    ):
        year = years[i]
        text = filings[year]
        res[year] = get_document_financials(f"{text['financials']}", items)

    save_dict[items_query_hash] = res
    # save pickle
    pkl_path.parent.mkdir(exist_ok=True, parents=True)
    with open(pkl_path, "wb") as pf:
        pickle.dump(save_dict, pf)

    return res


# def summarize_document(document: str):
