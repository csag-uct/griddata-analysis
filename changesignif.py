# calculates pvalue for difference between past and future period mean values
# based on t-test assuming unequal variances
#
# input: mean and std for past and future stored in separate files, monthly or seasonal
# also number of observations in past and future (lenght of time series from which mean and std were derived)
# and variable name that is stored in the netcdf file
# names of arguments provided by the acoompanying  shell script
#
# output: netcdf file with the pvalue for each time (seasonal or monthly)
# 
# by P.Wolski
# March 2016
#
#

import scipy.stats as st
from netCDF4 import Dataset
import shutil, sys, os
import numpy as np
import numpy.ma as ma

climfile_p=sys.argv[1]
stdfile_p=sys.argv[2]
nobs_p=int(sys.argv[3])
climfile_f=sys.argv[4]
stdfile_f=sys.argv[5]
nobs_f=int(sys.argv[6])
pvalfile=sys.argv[7]
var=sys.argv[8]

#print climfile_p
#print climfile_f
#print stdfile_p
#print stdfile_f

shutil.copyfile(stdfile_f, pvalfile)
nc_clim_p=Dataset(climfile_p, "r", format='NETCDF4')
nc_clim_f=Dataset(climfile_f, "r", format='NETCDF4')
nc_std_p=Dataset(stdfile_p, "r", format='NETCDF4')
nc_std_f=Dataset(stdfile_f, "r", format='NETCDF4')

nc_pval=Dataset(pvalfile, "r+", format='NETCDF4')

mean_p=nc_clim_p.variables[var][:]
mean_f=nc_clim_f.variables[var][:]
std_p=nc_std_p.variables[var][:]
std_f=nc_std_f.variables[var][:]

# the ttest_ind_from_stats behaves weirdly on masked values, so the output has to be masked again
# reads mask from one of the input files. Assumes that all input files are masked in similar way
mask=ma.getmask(mean_p)

try:
    res=st.ttest_ind_from_stats(mean_p, std_p, nobs_p, mean_f, std_f, nobs_f)
    #this applies the mask to output
    outarray=ma.masked_where(mask, np.copy(res.pvalue))
    nc_pval.variables[var][:]=outarray
    nc_pval.close()
except:
    print "something went awry..."
    nc_pval.close()
    os.remove(pvalfile)

