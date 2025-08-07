import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import sys
# Dynamically determine the project root directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))  # Add project root to sys.path
from src.data_loading.simple_loader import load_berkeley_earth, load_era5, load_config

def decimal_year_to_datetime(decimal_years):
    """Convert decimal years to datetime objects."""
    datetimes = []
    for decimal_year in decimal_years: 
        year = int(decimal_year) 
        remainder = decimal_year - year
        days_in_year = 366 if pd.Timestamp(f"{year}-01-01").is_leap_year else 365
        days = int(remainder * days_in_year)
        date = pd.Timestamp(f"{year}-01-01") + pd.Timedelta(days=days)
        datetimes.append(date)
    return np.array(datetimes, dtype='datetime64[ns]')

def preprocess_v2():
    
    # load monthly averages
    print("Processing Berkeley Earth and ERA5 data")
    print("Loading data")
    era5 = load_era5()
    be_tavg = load_berkeley_earth('tavg')
    be_tmin = load_berkeley_earth('tmin')
    be_tmax = load_berkeley_earth('tmax')

    # 1. Convert time to datetime
    print("Converting time to datetime")
    if be_tavg['time'].dtype != 'datetime64[ns]':
        be_tavg['time'] = decimal_year_to_datetime(be_tavg.time)
    if be_tmin['time'].dtype != 'datetime64[ns]':
        be_tmin['time'] = decimal_year_to_datetime(be_tmin.time)
    if be_tmax['time'].dtype != 'datetime64[ns]':
        be_tmax['time'] = decimal_year_to_datetime(be_tmax.time)
    if era5['time'].dtype != 'datetime64[ns]':
        era5['time'] = decimal_year_to_datetime(era5.time)

     # 3. Convert ERA5 longitude to -180 to 180
    print("Converting ERA5 longitude")
    era5 = era5.assign_coords(longitude=(era5.longitude + 180) % 360 - 180)
    era5 = era5.sortby('longitude')

    # 4. Interpolate ERA5 to Berkeley Earth grid
    print("Interpolating ERA5 to BE")
    era5 = era5.interp_like(be_tavg)

    # 5. Apply Berkeley Earth mask to ERA5
    print("Applying BE masking to ERA5")
    era5['TAVG'] = era5.TAVG.where(~np.isnan(be_tavg.temperature))
    era5['TMAX'] = era5.TMAX.where(~np.isnan(be_tmax.temperature))
    era5['TMIN'] = era5.TMIN.where(~np.isnan(be_tmin.temperature))

    # 2. Calculate ERA5 monthly anomalies based on 1951-1980 monthly averages
    print("Calculating ERA5 climatology and monthly anomalies")
    era5['TAVG_clim'] = era5['TAVG'].sel(time=slice('1951-01-01', '1980-12-31')).groupby('time.month').mean('time') # 1950-1980 average
    era5['TMAX_clim'] = era5['TMAX'].sel(time=slice('1951-01-01', '1980-12-31')).groupby('time.month').mean('time') # 1950-1980 average
    era5['TMIN_clim'] = era5['TMIN'].sel(time=slice('1951-01-01', '1980-12-31')).groupby('time.month').mean('time') # 1950-1980 average

    era5['TAVG_temp'] = era5['TAVG'].groupby('time.month') - era5['TAVG_clim'] # anomaly calculation
    era5['TMAX_temp'] = era5['TMAX'].groupby('time.month') - era5['TMAX_clim'] # anomaly calculation
    era5['TMIN_temp'] = era5['TMIN'].groupby('time.month') - era5['TMIN_clim'] # anomaly calculation

    # 6. Create an xarray dataset for each variable
    print("Saving processed netcdf files")
    ERA5_TAVG = xr.Dataset({
        'temperature': era5['TAVG_temp'],
        'climatology': era5['TAVG_clim'],
        'time': era5['time'],
        
        'latitude': era5['latitude'],
        'longitude': era5['longitude']
    })

    ERA5_TMAX = xr.Dataset({
        'temperature': era5['TMAX_temp'],
        'climatology': era5['TMAX_clim'],
        'time': era5['time'],
        'latitude': era5['latitude'],
        'longitude': era5['longitude']
    })

    ERA5_TMIN = xr.Dataset({
        'temperature': era5['TMIN_temp'],
        'climatology': era5['TMIN_clim'],
        'time': era5['time'],
        'latitude': era5['latitude'],
        'longitude': era5['longitude']
    })

    # Create output directories, get filepaths from the config.yaml file
    config = load_config()

    # Paths for Berkeley Earth and ERA5 processed files
    BE_TAVG_path = Path(config['processed']['tavg']['berkeley_earth_file'])
    BE_TMIN_path = Path(config['processed']['tmin']['berkeley_earth_file'])
    BE_TMAX_path = Path(config['processed']['tmax']['berkeley_earth_file'])
    ERA5_TAVG_path = Path(config['processed']['tavg']['era5_file'])
    ERA5_TMIN_path = Path(config['processed']['tmin']['era5_file'])
    ERA5_TMAX_path = Path(config['processed']['tmax']['era5_file'])

    # Create output directories if they don't already exist
    output_BE_TAVG = BE_TAVG_path.parent
    output_BE_TMIN = BE_TMIN_path.parent
    output_BE_TMAX = BE_TMAX_path.parent
    output_ERA5_TAVG = ERA5_TAVG_path.parent
    output_ERA5_TMIN = ERA5_TMIN_path.parent
    output_ERA5_TMAX = ERA5_TMAX_path.parent

    output_BE_TAVG.mkdir(parents=True, exist_ok=True)
    output_BE_TMIN.mkdir(parents=True, exist_ok=True)
    output_BE_TMAX.mkdir(parents=True, exist_ok=True)
    output_ERA5_TAVG.mkdir(parents=True, exist_ok=True)
    output_ERA5_TMIN.mkdir(parents=True, exist_ok=True)
    output_ERA5_TMAX.mkdir(parents=True, exist_ok=True)

    # Write processed data to NetCDF files
    print("Writing processed data to NetCDF files...")
    be_tavg.to_netcdf(BE_TAVG_path)
    print("Saved BE TAVG")
    be_tmin.to_netcdf(BE_TMIN_path)
    print("Saved BE TMIN")
    be_tmax.to_netcdf(BE_TMAX_path)
    print("Saved BE TMAX")
    ERA5_TAVG.to_netcdf(ERA5_TAVG_path)
    print("Saved ERA5 TAVG")
    ERA5_TMIN.to_netcdf(ERA5_TMIN_path)
    print("Saved ERA5 TMIN")
    ERA5_TMAX.to_netcdf(ERA5_TMAX_path)
    print("Saved ERA5 TMAX")

# run from command line
if __name__ == "__main__":
    preprocess_v2()