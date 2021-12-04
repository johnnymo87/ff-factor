# Fama French Factor Finder

## Background

After reading [The Incredible Shrinking Alpha 2nd edition: How to be a successful investor without picking winners](https://www.amazon.com/gp/product/B08BX5HRLJ) and [Your Complete Guide to Factor-Based Investing: The Way Smart Money Invests Today](https://www.amazon.com/gp/product/B01N7FCW2D) by [Larry Swedroe](https://www.amazon.com/Larry-E-Swedroe/e/B000APJJ8O) and [Andrew Berkin](https://www.amazon.com/Andrew-L-Berkin/e/B01N303388), I decided that I needed a way to find investments with exposure to ["factors"](https://en.wikipedia.org/wiki/Factor_investing). The factors I am searching for are the unique set of factors found in the [Fama French five factor model](https://en.wikipedia.org/wiki/Fama%E2%80%93French_three-factor_model) and the [Carhart four factor model](https://en.wikipedia.org/wiki/Carhart_four-factor_model): (1) market risk, (2) small caps, (3) stocks with a high book-to-market ratio -- i.e. value stocks -- (4) firms with high operating profitability, and (5) firms that invest conservatively. These factors are also known market minus risk free, small minus big, high minus low, robust minus weak, conservative minus aggressive respectively. And they get abbreviated as acronyms.

This application combines the following data sources:
* Factor return data from [Ken French's data library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
* Investment metadata and return data from the Yahoo Finance API.
  * With some help on the metadata from the Seeking Alpha API.
* Ticker symbols by market types (`US`, `Developed ex US`, and `Emerging`) found with the help of [Fidelity's ETF screener](https://research2.fidelity.com/pi/etf-screener).
  * I look for ETFs of equity funds that are not leveraged or inverse, are not thematic, and have the country exposure appropriate for their market type.

I am looking for funds that show returns that are statistically significantly similar to the returns of the factors in the Ken French data library.

I try to find the most optimal combination of funds for each market type. My criteria resembles the Sharpe ratio (mean / standard deviation) -- I want maximum exposure to all five factors, and I want my exposure to be divided as equally as possible across all of them. Inspired by [this blog post on how to optimize a portfolio's Sharpe ratio](https://www.kaggle.com/vijipai/lesson-6-sharpe-ratio-based-portfolio-optimization), I employ [scipy's SLSQP optimizer](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html) to do this. I have almost no understanding of the math behind this optimizer. ([An gentle intro for the layman](https://stackoverflow.com/a/43669396/2197402), [a cookbook for the expert](https://docs.mosek.com/modeling-cookbook/intro.html).)

The optimizer can easily get stuck in local optimums, so I run it 100 times, each time with a random sampling of 80% of the data. This seems to mitigate this problem.

## Getting started

This application uses [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) and run.


* Make a `secrets.env` file based on the template `secrets.env.example`
  ```sh
  cp secrets.env.example secrets.env
  ```
* Fill out the `secrets.env` file
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

#### Install a new package

* Add the package name to `requirements.in`. Then, while exec-ed into the container, but not while running the application, run:
  ```sh
  pip-compile --output-file=- > requirements.txt
  ```
  This will write to `requirements.txt`. For more details, see [this stackoverflow](https://stackoverflow.com/a/65666949/2197402).
* This new package will be gone once you exit the container. But since it's still listed in requirements.txt, you can bake it into all future containers by rebuilding the image
  ```sh
  docker-compose build
  ```

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

The world market is roughly divided four-eighths US, three-eighths Developed ex US, and one-eighth Emerging. I intend to do the same with my equity allocation.

#### Developed markets ex US

Ken French's data library [defines Developed market ex US countries](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5developed.html) as, "Australia, Austria, Belgium, Canada, Switzerland, Germany, Denmark, Spain, Finland, France, Great, Greece, Hong Kong, Ireland, Italy, Japan, Netherlands, Norway, New Zealand, Portugal, Sweden, and Singapore".

For the size and value factors, my choice is and [RODM](https://www.hartfordfunds.com/etfs/rodm.html). My data frame contained four choices, but after some manual research I excluded three of them for containing non-Developed countries, and one for being actively managed. Coincidentally, the remaining choice had the best expense ratio and the lowest yield (which is better for non-tax-advantaged accounts).
```py
smb = df[(df.coef >= 0) & (df.factor == 'small_minus_big')]
hml = df[(df.coef >= 0) & (df.factor == 'high_minus_low')]
neg = df[df.coef <= 0]

df[~df.ticker.isin(neg.ticker)][(df.ticker.isin(smb.ticker)) & (df.ticker.isin(hml.ticker))].sort_values(by=['coef_sum', 'ticker', 'factor'])
```
```py
coef  tvalue  pvalue             factor ticker  coef_sum   yield   expense ratio   actively managed  Non-Developed Countries
0.30    2.16    0.03     high_minus_low   RODM      0.94   2.78%        0.29%            False
0.46    2.77    0.01  robust_minus_weak   RODM      0.94   2.78%        0.29%            False
0.18    2.05    0.04    small_minus_big   RODM      0.94   2.78%        0.29%            False
0.23    2.21    0.03     high_minus_low   FNDC      1.23   2.76%        0.39%            False       South Korea (7.12%)
0.57    4.71    0.00  robust_minus_weak   FNDC      1.23   2.76%        0.39%            False       South Korea (7.12%)
0.43    6.94    0.00    small_minus_big   FNDC      1.23   2.76%        0.39%            False       South Korea (7.12%)
0.43    2.82    0.01     high_minus_low   FYLD      1.41   3.72%        0.59%            True        China (9.06%)
0.71    3.97    0.00  robust_minus_weak   FYLD      1.41   3.72%        0.59%            True        China (9.06%)
0.27    2.99    0.00    small_minus_big   FYLD      1.41   3.72%        0.59%            True        China (9.06%)
0.59    2.52    0.01     high_minus_low    FID      1.85   3.81%        0.60%            False       China (4.25%), South Korea (3.46%)
1.01    3.67    0.00  robust_minus_weak    FID      1.85   3.81%        0.60%            False       China (4.25%), South Korea (3.46%)
0.25    1.75    0.08    small_minus_big    FID      1.85   3.81%        0.60%            False       China (4.25%), South Korea (3.46%)
```

For the momentum factor, my choice is [IMOM](https://etfsite.alphaarchitect.com/imom/). It has the strongest momentum score out of any of the funds, and it has good scores in a few other factors too.
```py
df[df.ticker == 'IMOM']
```
```py
coef  tvalue  pvalue                factor ticker
0.63    1.91    0.06     robust_minus_weak   IMOM
0.36    1.84    0.07       small_minus_big   IMOM
0.54    4.23    0.00  winners_minus_losers   IMOM
```

#### Emerging markets

Ken French's data library [defines Emerging market countries](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5emerging.html) as, "Argentina, Brazil, Chile, China, Colombia, Czech Republic, Egypt, Greece, Hungary, India, Indonesia, Malaysia, Mexico, Pakistan, Peru, Philippines, Poland, Qatar, Russia, Saudi Arabia, South Africa, South Korea, Taiwan, Thailand, Turkey, United Arab Emirates."

For the size and value factors, my choice is [EEMS](https://www.ishares.com/us/products/239642/ishares-msci-emerging-markets-smallcap-etf), with a 0.71% expense ratio. It's a "classic" choice since it's the only one that simultaneously exhibits small cap and value tilts at the same time, and it avoids the common problem of having a negative momentum tilt.
```py
smb = df[(df.coef >= 0) & (df.factor == 'small_minus_big')]
hml = df[(df.coef >= 0) & (df.factor == 'high_minus_low')]

df[(df.ticker.isin(smb.ticker)) & (df.ticker.isin(hml.ticker))].sort_values(by=['coef_sum', 'ticker', 'factor'])
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
