
# coding: utf-8

# In[282]:

#
# calculates onset for gridded data
#
# P.Wolski
# February 2017
#
#  
# use: onset.py input.nc <climyearstart.nc|climyearstart> onsetpercentile output.nc onset|cessation
#
# returns output.nc of the same lat lon dimensions as input.nc
# input.nc has to have one 3D variable with dimensions: lat,lon,time (not necessarily in this sequence)
# onset calculated as number of days since the beginning of climatological year when accumulated rainfall exceeds onsetpercentile of that year's total
# cessation calculated in an analogous way
# climyearstart can be given as a nc file of the same lat lon as the input file and one variable storing the climyearstart month, or as a single value
#


import numpy as np
from netCDF4 import Dataset, num2date, date2num
import sys, os
import pandas as pd

#to remove duplicate warnings
import warnings
warnings.filterwarnings('ignore')
from matplotlib import pyplot as plt

infile=sys.argv[1]
climyearstart=sys.argv[2]
onsetpercentile=sys.argv[3]
outfile=sys.argv[4]
what=sys.argv[5]
#infile="/work/data/satrain/chirps/chirps_v2.0_1981-2014_p25_saf.nc"
#climyearstart=1
#onsetpercentile=15
#outfile="test.nc"
#what="duration"


# In[247]:

def rainy_season_pars(ts, p1,p2,what):
    from itertools import groupby
    temp=ts.cumsum()
    if what=="onset":
        resdate_onset=np.argmax(temp>p1*temp[-1]/100)
        days=(resdate_onset-ts.index[0]).days
    if what=="cessation":
        resdate_cess=np.argmax(temp>p2*temp[-1]/100)
        days=(resdate_cess-ts.index[0]).days
    if what=="duration":
        resdate_onset=np.argmax(temp>p1*temp[-1]/100)
        resdate_cess=np.argmax(temp>p2*temp[-1]/100)
#        print resdate_onset, resdate_cess
        days=(resdate_cess-resdate_onset).days
    if what=="drydays_max" or what=="drydays_mean":
        resdate_onset=np.argmax(temp>p1*temp[-1]/100)
        resdate_cess=np.argmax(temp>p2*temp[-1]/100)
#        print resdate_onset, resdate_cess
        tempbin=np.copy(ts[resdate_onset:resdate_cess])
#        print "tempbin:"
#        print tempbin
        tempbin[tempbin>1]=1
        tempbin[tempbin<1]=0
        grouped = np.array([(k, sum(1 for i in g)) for k, g in groupby(tempbin)])
#        print grouped
#        print grouped.shape, np.mean(grouped[grouped[:,0]==0,1])
        if what=="drydays_mean":
            days=np.mean(grouped[grouped[:,0]==0,1])
        else:
            days=np.max(grouped[grouped[:,0]==0,1])
#        print days
    return days
    


# In[326]:

# this reads a netCDF file with three dimensions: lon, lat and time, containing one variable
# onset is calculated on the entire scene, save the areas that have NaNs
ncdata=Dataset(infile, "r", format='NETCDF4')
#finding variable name
found=False
for v in ncdata.variables.keys():
    vdata=ncdata.variables[v]
    if v=="lat" or v=="latitude":
        latname=v
        lats=vdata[:]
        nlat=len(lats)
    if v=="lon" or v=="longitude":
        lonname=v
        lons=vdata[:]
        nlon=len(lons)
    if v=="time" or v=="date":
        timename=v
        time=vdata[:]
        dates=num2date(time, vdata.units)
        nts=len(time)
        units=vdata.units
        calendar=vdata.calendar
    if vdata.ndim==3:
        vname=v
        data0=ncdata.variables[v][:]
        found=True
        print vname
if found==False:
    print "no appropriate variable found in the source file"
    sys.exit()

#reorder the input array, so that it is time, latitude, longitude
temp=ncdata.variables[v]
latindx=temp.dimensions.index(latname)
lonindx=temp.dimensions.index(lonname)
timeindx=temp.dimensions.index(timename)
data=np.moveaxis(data0,(timeindx,latindx,lonindx), (0,1,2))

try:
    climyearstart=int(climyearstart)
    print "climyearstart is a single value"
    climyearstart_array=np.ones_like(data[0,:,:])*climyearstart
except:
    print "climyearstart varies through the domain"


nonmasked=data.mask[0,:,:]==False
subdata=data[:,nonmasked]
_df=pd.DataFrame(subdata.reshape(len(dates),-1), index=dates)
firstmonth=6
groupeddata=_df.groupby(pd.DatetimeIndex(_df.index).shift(-firstmonth+1,freq='m').year)

if what=="onset":
    res=groupeddata.agg(rainy_season_pars, 15, 85, "onset")
else:
    print "unknown operation: "+ what
    print "exiting..."
    sys.exit()


if firstmonth>0:
    res=res.iloc[1:-1]

output=np.zeros([res.shape[0],data.shape[1],data.shape[2]], "float32")
output[:]=np.nan
output[:,nonmasked]=res

# In[327]:

#writing netcdf file
ncdataset=Dataset(outfile, "w", format='NETCDF3_CLASSIC')
ncdataset.createDimension('lon', nlon)
ncdataset.createDimension('lat', nlat)
ncdataset.createDimension('time', None)
longitudes = ncdataset.createVariable('lon',np.float32, ('lon',))
latitudes  = ncdataset.createVariable('lat',np.float32, ('lat',))
times  = ncdataset.createVariable('time',np.float32, ('time',))
newdates=pd.date_range(pd.datetime(res.index[0], 12,31), pd.datetime(res.index[-1], 12, 31), freq="A")
print len(newdates), output.shape
times[:]=date2num(newdates.to_pydatetime(), units=units)
times.units=units
times.calendar=calendar

latitudes.long_name = "latitude" ;
latitudes.units = "degrees_north" ;
longitudes.long_name = "longitude" ;
longitudes.units = "degrees_east" ;
longitudes[:]=lons
latitudes[:]=lats

v=ncdataset.createVariable(what,np.float32,('time', 'lat', 'lon',))
v[:,:,:]=output
if what=="onset":
    v.units="days since start of climatological year"
if what=="duration":
    v.units="days"
if what=="":
    v.units=""
    
ncdataset.close()



