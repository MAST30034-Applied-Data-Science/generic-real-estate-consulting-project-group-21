# Generic Real Estate Consulting Project


## Style Requirements

Confirm that all code contains docstrings and follows PEP8 guidlines by running

`scripts/repo-linter.py` 

This checks the jupyter notebooks too. 

This is run as a Github Action and the output can be checked on Github by clicking the tick/cross left of the commit hash.

## Overview

### Data Processing

`scripts/DataScraping.py` - used to scrape Realestate.com.au data into `data/raw/realestate.csv`

`notebooks/preprocessing.py` - reads scraped data and outputs saves preprocessed data into `data/curated/realestate_coor.csv`

`scripts/OpenRouteService.py` - reads`data/curated/realestate_coor.csv` and wrote `data/curated/realestate_with_closest_distance_duration`

`notebooks/popu_incomepredict.py` - downloads historical population/incomes and estimates future population/incomes

`notebooks/historical_data.ipynb` - preprocesses historical rental prices by suburb

### Modelling / Analysis

`notebooks/summary_notebook.ipynb` - for an overview

Notebooks for specific questions:
`notebooks/question-*-analysis.ipynb` - requires `scripts/engineer-metrics.py`
`notebooks/question-*-modelling.ipynb` - requires `scripts/engineer-metrics.py`
`notebooks/Q3.ipynb` - requires `scripts/dataforQ3.py`

## Notes on Running Code

`scripts/DataScraping.py` will require API keys to run, they can be found from the developer options tab when searching [www.realestate.com.au]

`scripts/OpenRouteService*.py` will require an Open Route Service server to run - ours has been shutdown as of 13/10/22

The most easiest way to get an Open Route Service server would be to ask Lachlan.

## LaTeX Plots

To get LaTeX plots you will need to set the following in your `matplotlibrc` file 

```
font.family: serif
text.usetex: True
```

Note that these were not set within the repo as it requires a working latex installation - which most people don't have.

See [matplotlib - Text rendering with LaTeX](https://matplotlib.org/stable/tutorials/text/usetex.html) for details.

