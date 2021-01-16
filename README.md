# Fama French Factor Finder

## Background

After reading [The Incredible Shrinking Alpha 2nd edition: How to be a successful investor without picking winners](https://www.amazon.com/gp/product/B08BX5HRLJ) and [Your Complete Guide to Factor-Based Investing: The Way Smart Money Invests Today](https://www.amazon.com/gp/product/B01N7FCW2D) by [Larry Swedroe](https://www.amazon.com/Larry-E-Swedroe/e/B000APJJ8O) and [Andrew Berkin](https://www.amazon.com/Andrew-L-Berkin/e/B01N303388), I decided that I needed a way to find investments with exposure to ["factors"](https://en.wikipedia.org/wiki/Factor_investing). The factors I am searching for are the unique set of factors found in the [Fama French five factor model](https://en.wikipedia.org/wiki/Fama%E2%80%93French_three-factor_model) and the [Carhart four factor model](https://en.wikipedia.org/wiki/Carhart_four-factor_model): (1) market risk, (2) small caps, (3) stocks with a high book-to-market ratio -- i.e. value stocks -- (4) firms with high operating profitability, (5) firms that invest conservatively, and (6) stocks that have been on a winning streak -- i.e. momentum stocks.

This application combines the following data sources:
* Factor return data from [Ken French's data library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
* Investment return data from the Yahoo Finance API
* ETF ticker symbols by market types (`US`, `Developed ex US`, and `Emerging`) scraped from [etfdb.com](https://etfdb.com) with the following jquery in the browser console:
  ```js
  var tickers = []
  function scrape() {
    JSON.stringify([...$('td[data-th="Symbol"]')].forEach(function(el) { tickers.push(el.textContent) }));
    if ($('li.page-next').length) {
      $('li.page-next').click()
      setTimeout(scrape, 5000);
    }
  }
  scrape()
  // JSON.stringify(tickers)
  ```
  * After manual study, I filter out many scraped tickers for not being equity, not having the correct country composition, or for being thematic and thus not represenative of all sectors.

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


#### Play around with the data frame

Set a break point at the end of `__main__.py`, and run `python .` to catch it. Then play around with the data frame.
```py
import pdb; pdb.set_trace() # set a break point
(Pdb) df # look at the data frame
(Pdb) df.sort_values(by=['coef'], ascending=False) # sort it
(Pdb) df.head(20) # look at the first twenty rows
```
For ideas about how to further manipulate the data frame, google "pandas cheat sheet".

## Conclusions

#### Emerging markets

Ken French's data library [defines Emerging market countries](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5emerging.html) as, "Argentina, Brazil, Chile, China, Colombia, Czech Republic, Egypt, Greece, Hungary, India, Indonesia, Malaysia, Mexico, Pakistan, Peru, Philippines, Poland, Qatar, Russia, Saudi Arabia, South Africa, South Korea, Taiwan, Thailand, Turkey, United Arab Emirates."

For the size and value factors, my choice is [EEMS](https://www.ishares.com/us/products/239642/ishares-msci-emerging-markets-smallcap-etf), with a 0.71% expense ratio. It's a "classic" choice since it's the only one that simultaneously exhibits small cap and value tilts at the same time, and it avoids the common problem of having a negative momentum tilt.
```py
smb = df[(df.coef >= 0) & (df.factor == 'small_minus_big')]
hml = df[(df.coef >= 0) & (df.factor == 'high_minus_low')]

df[(df.ticker.isin(smb.ticker)) & (df.ticker.isin(hml.ticker))]
```
```py
                               coef  tvalue  pvalue                         factor ticker
small_minus_big                0.62    8.07    0.00                small_minus_big   EEMS
high_minus_low                 0.14    1.47    0.14                 high_minus_low   EEMS
conservative_minus_aggressive -0.24   -1.96    0.05  conservative_minus_aggressive   EEMS
winners_minus_losers           0.08    1.34    0.18           winners_minus_losers   EEMS
```

For the momentum factor, my choice is [PIE](https://www.invesco.com/us/financial-products/etfs/product-detail?audienceType=Ria&ticker=PIE), with a 0.90% expense ratio. It is the fund with the strongest momentum tilt.
```py
df[df.ticker == 'PIE']
```
```py
                      coef  tvalue  pvalue                factor ticker
high_minus_low       -0.32   -2.05    0.04        high_minus_low    PIE
winners_minus_losers  0.39    5.22    0.00  winners_minus_losers    PIE
```

#### Pre-Emerging Markets
For the sake of diversity, I'm considering [FM](https://www.ishares.com/us/products/239649/ishares-msci-frontier-100-etf), with a 0.79% expense ratio. It calls itself a ["Frontier" market](https://seekingalpha.com/article/4198945-frontier-markets-diversification-cheap-price) fund, with exposure to even more marginal countries. As the seeking alpha article notes, this market type has relatively low correlation to other market types. This is a positive in its own right, but it means I can't use any of Ken French's data to analyze it for desirable tilts.
