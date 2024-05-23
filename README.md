# LLM + 10-K

Leveraging Large Language Models (LLMs) to extract, summarize, financial
information out of 10-K filings derived from the
[SEC EDGAR database](https://www.sec.gov/edgar/search-and-access).

Form 10-K filings are financial reports annually submitted by publicly
reporting companies in the U.S., where crucial information regarding the
corporation's financial status, numbers, and risks are disclosed. They are
notoriously long, with some reaching over 50,000 words of text, making it
tedious to manually derive meaningful insights out from them. Alternatively,
LLMs, with their ability to perform information retrieval and summarization,
can be used to automate this process and thus reduce the overhead needed to
parse through them by hand.

## Features

- Retrieve, compile, and visualize key metrics (e.g. net sales, gross margin)
  across a timespan
  - Ability to customize metrics that the LLM retrieves from 10-K filings
- Compare key metrics across three different companies/tickers
- Generate summaries of important sections of a particular Form 10-K

## Tech Stack

Below is a list of libraries/tools I've used heavily in this project:

- [`edgartools`](https://github.com/dgunning/edgartools): One of the most
  polished and well-featured libraries for retrieving 10-K filings from SEC EDGAR
  that I've encountered. Ability to extract raw text from each filing with
  ease.

- [`gemini-1.5-flash-latest`](https://ai.google.dev/gemini-api): The LLM API of
  choice for this project. It supports a very generous input context window (up
  to 1 million tokens), which is ideal for supporting such a large document as
  Form 10-K. Additionally, it is capable of generating responses in JSON format,
  making it especially easier to work with the retrieved data for visualization.

- [`streamlit`](https://github.com/streamlit/streamlit): Used for the UI
  frontend for displaying visualizations, showing user options, input for calling
  the LLM API, etc. I used Streamlit Community Cloud to host this project site.

