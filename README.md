# Generic Real Estate Consulting Project

## Dependencies

Install Python dependencies with:

```
pip install -r requirements.txt
```

## Style Requirements

Confirm that all code contains docstrings and follows PEP8 guidlines by running

`scripts/repo-linter.py` 

This checks the jupyter notebooks too. 

This is run as a Github Action and the output can be checked on Github by clicking the tick/cross left of the commit hash.

## Overview

### Data that can not be Downloaded in Python

To get the shapefile of postcode in Victoria, go to https://datashare.maps.vic.gov.au/search?md=46bba391-0d67-5bd7-b0bb-bb37945c5c4a , then click 'Add to Order' and 'Proceed to Order Configuration'.  After entering order configuration, choose 'Geographicals for GDA 94' for Projection and 'ESRI Shapefile' for Format. Then click 'Proceed to my Cart' and 'Proceed to my Details'. Tick 'Continue as a guest' and enter your e-mail address. After Agreeing on the term of use, click 'Confirm'. Download the zip file from e-mail, open it and put folder ll_gda94 to data/raw

### Data Processing

`scripts/DataScraping.py` - used to scrape Realestate.com.au data into `data/raw/realestate.csv`

`notebooks/preprocessing.py` - reads scraped data and outputs saves preprocessed data into `data/curated/realestate_coor.csv`

`scripts/OpenRouteService.py` - reads`data/curated/realestate_coor.csv` and wrote `data/curated/realestate_with_closest_distance_duration`

`notebooks/popu_incomepredict.py` - downloads historical population/incomes and estimates future population/incomes

`notebooks/historical_data.ipynb` - preprocesses historical rental prices by suburb

### Modelling / Analysis

`notebooks/summary_notebook.ipynb` - for an overview

Notebooks for specific questions:
* `notebooks/question-*-analysis.ipynb` - requires `scripts/engineer-metrics.py`
* `models/question-*-modelling.ipynb` - requires `scripts/engineer-metrics.py`
* `notebooks/Q3.ipynb` - requires `scripts/dataforQ3.py`

## Notes on Running Code

`scripts/DataScraping.py` will require API keys to run, they can be found from the developer options tab when searching www.realestate.com.au

`scripts/OpenRouteService*.py` will require an Open Route Service server to run - ours has been shutdown as of 13/10/22

The easiest way to get an Open Route Service server would be to ask Lachlan.

## LaTeX Plots

To get LaTeX plots you will need to set the following in your `matplotlibrc` file 

```
font.family: serif
text.usetex: True
```

Note that these were not set within the repo as it requires a working latex installation - which most people don't have.

