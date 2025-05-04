# Finnish Startups 2025
This project explores the Finnish startup ecosystem, focusing on the sample of Finnish startups listed on [statup100](https://startup100.net/companies/).
The goal is to analyze the publicly available data of these startups and gain insights into the startup landscape in Finland.

![Finnish Startups 2025]()

## Installation

Create virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Scraper
If you want to scrape the data yourself, you need to set up the environment variables for the scraper.
Set the `COMPANY_INFO_WEBSITE_URL` env variable to the finnish website that has public company information ;)

### ETL
Scraper will produce a bunch of `.json` files that need to be normalized and cleaned.
Running the `etl.py` will do that for you.
```bash
python etl.py
```

### Analysis Notebooks
The analysis is done with Marimo. You can run Marimo in the root directory:
```bash
marimio edit
```


