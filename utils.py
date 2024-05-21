import os
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from edgar import Company
from tqdm import tqdm

FilingTextMap = Dict[str, str]


@dataclass
class CompanyFilingTexts:
    """Dataclass to store downloaded 10-K filings for a company.

    Acts similarly to a dictionary, where the keys are years and the values are
    dictionaries containing the extracted sections from each 10-K filing.
    Has an additional `ticker` attribute to store the company's ticker.
    """

    ticker: str
    filings: Dict[int, FilingTextMap]

    def __getitem__(self, year: int) -> FilingTextMap:
        return self.filings[year]

    def __len__(self) -> int:
        return len(self.filings)

    def keys(self):
        return self.filings.keys()


def extract_10k_sections(text_10k: str) -> FilingTextMap:
    """Clean and extract important sections from a 10-K form.

    Removes irrelevant text like headers, footers, and page numbers. Extracts
    Business, Risk Factors, Management's Discussion and Analysis, and
    Financial Statements sections.
    """
    res = {}

    # source: https://github.com/rsljr/edgarParser/blob/master/parse_10K.py
    def get_section(reg_start: re.Pattern, reg_end: re.Pattern) -> str | None:
        starts = [i.start() for i in reg_start.finditer(text_10k)]
        ends = [i.start() for i in reg_end.finditer(text_10k)]
        if not len(starts) or not len(ends):
            return None
        ranges = []  # find all possible ranges of the section
        for s in starts:
            for e in ends:
                if s < e:
                    ranges.append([s, e])
                    break
        max_range = 0
        max_range_ind = 0
        for i, r in enumerate(ranges):  # argmax of all ranges
            diff = r[1] - r[0]
            if diff > max_range:
                max_range_ind = i
                max_range = diff
        res_start, res_end = ranges[max_range_ind]  # return text from the largest range
        return text_10k[res_start:res_end]

    def clean_text(text: str | None) -> str:
        if not text:
            return ""

        # remove common page headers/footers
        # repeated "PART X" or "ITEM X" headers/footers
        text = re.sub(
            r"^[^\S\r\n]*(PART|ITEM)[^\S\r\n]*\w+[^\S\r\n]*[\.\,\;\:\-\_]*\s*$",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        # page numbers
        text = re.sub(
            r"^[^\S\r\n]*\d+[^\S\r\n]*$",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        # "XXX | YYYY Form 10-K | XX" footers
        text = re.sub(
            r"^.*\|[^\S\r\n]*\d+[^\S\r\n]*Form 10-K[^\S\r\n]*\|.*$",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        # "<PAGE>" markers
        text = re.sub(
            r"^.*<PAGE>.*$",
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        # remove empty lines
        text = re.sub(r"^(?:[\t ]*(?:\r?\n|\r))+", "", text, flags=re.MULTILINE)
        return text

    # scan all beginnings and ends for each section
    item1_start = re.compile(r"item\s*[1][\.\;\:\-\_]*\s*\|*\s*Bus", re.IGNORECASE)
    item1_end = re.compile(
        r"item\s*1a[\.\;\:\-\_]*\s*\|*\s*Risk|item\s*[2][\.\,\;\:\-\_]*\s*\|*\s*(Desc|Prop)",
        re.IGNORECASE,
    )
    item1a_start = re.compile(
        r"(?<!,\s)item\s*1a[\.\;\:\-\_]\s*\|*\s*Risk", re.IGNORECASE
    )
    item1a_end = re.compile(
        r"item\s*[2][\.\,\;\:\-\_]*\s*\|*\s*(Desc|Prop)", re.IGNORECASE
    )
    item7_start = re.compile(r"item\s*[7][\.\;\:\-\_]*\s*\|*\s*Man", re.IGNORECASE)
    item7_end = re.compile(
        r"item\s*[8][\.\,\;\:\-\_]*\s*\|*\s*(Fin|Con)", re.IGNORECASE
    )
    item8_start = re.compile(
        r"item\s*[8][\.\,\;\:\-\_]*\s*\|*\s*(Fin|Con)", re.IGNORECASE
    )
    item8_end = re.compile(r"item\s*[9][\.\;\:\-\_]*\s*\|*\s*Chan", re.IGNORECASE)

    res["business"] = clean_text(get_section(item1_start, item1_end))
    res["risk"] = clean_text(get_section(item1a_start, item1a_end))
    res["mda"] = clean_text(get_section(item7_start, item7_end))
    res["financials"] = clean_text(get_section(item8_start, item8_end))
    return res


def get_10k_filing_texts(
    ticker: str,
    before="2024-01-01",
    after="1995-01-01",
    cache_dir=".cache/",
) -> CompanyFilingTexts:
    """Downloads text contents of 10-K filings from SEC EDGAR.

    Leverages edgartools to return 10-K filings for a given ticker in a
    specified time range (after:before). edgartools assists with some
    preliminary text extraction for us to work with. Downloads are cached into
    `cache_dir`, which defaults to `.cache/`. If `extract_sections` is True,
    segment important sections off each downloaded 10-K filing
    (see `extract_10k_sections`).
    """

    desc = f"{ticker} 10-K Filings from {after} to {before}"
    # check cache for saved 10-K filings
    cache_full_dir = Path(os.getcwd(), cache_dir)
    pkl_path = Path(
        cache_full_dir,
        f"{ticker}_{after}:{before}_10-K.pkl",
    )
    if Path.exists(pkl_path):
        print(f"Fetching cached {desc}")
        return pickle.load(open(pkl_path, "rb"))

    # else, download using edgartools
    company = Company(ticker)
    filings = company.get_filings(form="10-K", filing_date=f"{after}:{before}")

    print(f"Downloading {desc}")

    if not filings:
        raise ValueError(f"No 10-K filings found for {ticker} from {after} to {before}")

    res = {}

    for filing in tqdm(filings, desc="Downloading 10-K Filings"):
        year = int(str(filing.filing_date)[0:4])
        text = filing.text()
        res[year] = extract_10k_sections(text)
        res[year]["full_text"] = text

    # attach ticker to result by calling the dataclass
    res = CompanyFilingTexts(ticker, res)

    # save pickle
    pkl_path.parent.mkdir(
        exist_ok=True, parents=True
    )  # in the case that the cache directory doesn't exist yet
    with open(pkl_path, "wb") as pf:
        pickle.dump(res, pf)

    return res
