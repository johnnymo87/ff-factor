# Fama French Factor Finder

## Background

After reading [The Incredible Shrinking Alpha 2nd edition: How to be a successful investor without picking winners](https://www.amazon.com/gp/product/B08BX5HRLJ) and [Your Complete Guide to Factor-Based Investing: The Way Smart Money Invests Today](https://www.amazon.com/gp/product/B01N7FCW2D) by [Larry Swedroe](https://www.amazon.com/Larry-E-Swedroe/e/B000APJJ8O) and [Andrew Berkin](https://www.amazon.com/Andrew-L-Berkin/e/B01N303388), I decided that I needed a way to find investments with exposure to ["factors"](https://en.wikipedia.org/wiki/Factor_investing). The factors I am searching for are the unique set of factors found in the [Fama French five factor model](https://en.wikipedia.org/wiki/Fama%E2%80%93French_three-factor_model) and the [Carhart four factor model](https://en.wikipedia.org/wiki/Carhart_four-factor_model): (1) market risk, (2) small caps, (3) stocks with a high book-to-market ratio -- i.e. value stocks -- (4) firms with high operating profitability, (5) firms that invest conservatively, and (6) stocks that have been on a winning streak -- i.e. momentum stocks.

This application combines the following data sources:
* Factor return data from [Ken French's data library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
* Investment return data from the Yahoo Finance API
* ETF ticker symbols by market types (`US`, `Developed ex US`, and `Emerging`) scraped from [etfdb.com](https://etfdb.com)

I am looking for ETFs that show returns that are statistically significantly similar to the returns of the factors in the Ken French data library.

Since exactly how I screen ETFs can vary from time to time, this application doesn't do that. All it does is pull all the relevant data into a data frame, `df` at the bottom of `__main__.py`. Catch a debug breakpoint beneath it to play with it.

## Getting started

This application uses [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) and run.


* Build the application's image
  ```sh
  docker-compose build
  ```
* Start the database
  ```sh
  docker-compose up -d db
  ```
* Step into the application development environment
  ```sh
  docker-compose run --rm app bash
  ```
* Once inside, run the application
  ```sh
  python .
  ```

## Developing

#### Debug
* documentation [here](https://docs.python.org/3/library/pdb.html)
* set a breakpoint with `import pdb; pdb.set_trace()`
  * if you're using vim with [a project-specific .vimrc](https://andrew.stwrt.ca/posts/project-specific-vimrc/), you can type this with `<leader>db`
* show where you are with `list`
* continue with `continue`
* quit with `quit`

#### Play with the data frame
```py
df # look at it
df.sort_values(by=['coef'], ascending=False) # sort it
df.head(20) # look at the first twenty rows
```
For ideas about how to further manipulate the data frame, google "pandas cheat sheet".

#### Add a new python package
* Inside the container, use the bash function `pip-install-save` to simultaneously install the python package and update `requirements.txt`. For example, say you wanted to install `pytest-timeout`:
  ```sh
  pip-install-save pytest-timeout
  ```
* This new package will be gone once you exit the container. But since it's still listed in requirements.txt, you can bake it into all future containers by rebuilding the image
  ```sh
  docker-compose build
  ```
