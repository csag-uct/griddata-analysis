# griddata-analysis
several functions to batch-process gridded data to derive time series statistics

## what's here:
Repo contains a set of (crudely cobbled together) functions to be used for batch processing of gridded datasets to derive slightly more "complicated" statistics

v1.0
created by P.Wolski
February 2017

## files:
onset.py
Calculating rainy season onset, cessation and duration, using percentile treshold. Also calculates mean and max consecutive dry days during the rainy season.
Reads first month of climatological year either as a single value for entire domain, or as a gridded file (defined on the same grid as the input data)
Returns nc file with annual data for the requested parameter.
At this stage - returns onle parameter per file
  
trend.py
copied from another repo: trends-analysis
contains functions:
get_linear()
get_TheilSen()
get_quantreg()

All functions give only analytical pval
No correction for autocorrelation

changesignif.py
Calculates significance of difference between two time periods. Data read from two files. Significance calculated from t-test.

 
