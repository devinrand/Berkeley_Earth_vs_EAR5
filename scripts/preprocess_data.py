
"""
Preprocess Berkeley Earth and ERA5 data for comparison.

This script:
1. Loads raw Berkeley Earth and ERA5 data
2. Converts Berkeley Earth decimal years to datetime
3. Calculates ERA5 anomalies using 1951-1980 baseline
4. Converts ERA5 longitude from 0-360 to -180-180
5. Interpolates ERA5 to Berkeley Earth grid
6. Applies Berkeley Earth land mask to ERA5
7. Saves preprocessed data
"""

import numpy as np
import pandas as pd
import argparse
from pathlib import Path
from src.data_loading.simple_loader import load_berkeley_earth, load_era5


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


def main():
    """Main preprocessing workflow."""
    
    # Create output directories
    output_dir = Path.home() / "Documents" / "temperature-comparison-data" / "processed"
    output_dir_BE = output_dir / "BE"
    output_dir_ERA5 = output_dir / "ERA5"
    output_dir_BE.mkdir(parents=True, exist_ok=True)
    output_dir_ERA5.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Load raw data
    print("Loading raw data...")
    be = load_berkeley_earth()
    era5 = load_era5()
    
    # Rename ERA5 variables to match Berkeley Earth
    era5 = era5.rename({'t2m': 'temperature', 'valid_time': 'time'})

    # 1. Convert Berkeley Earth time to datetime
    print("Converting Berkeley Earth decimal years to datetime...")
    be['time'] = decimal_year_to_datetime(be.time)

    # 2. Calculate ERA5 monthly anomalies based on 1951-1980 monthly averages
    print("Calculating ERA5 anomalies (1951-1980 baseline)...")
    era5['climatology'] = era5['temperature'].sel(
        time=slice('1951-01-01', '1980-12-31')
    ).groupby('time.month').mean('time')
    
    era5['anomalies'] = era5['temperature'].groupby('time.month') - era5['climatology']

    # 3. Convert ERA5 longitude to -180 to 180
    print("Converting ERA5 longitude to -180 to 180...")
    era5 = era5.assign_coords(longitude=(era5.longitude + 180) % 360 - 180)
    era5 = era5.sortby('longitude')

    # 4. Interpolate ERA5 to Berkeley Earth grid
    print("Interpolating ERA5 to Berkeley Earth grid...")
    era5_interp = era5.interp_like(be)

    # 5. Apply Berkeley Earth mask to ERA5
    print("Applying Berkeley Earth land mask to ERA5...")
    era5_interp['temperature'] = era5_interp.temperature.where(~np.isnan(be.temperature))

    # Save processed data
    print("Saving processed data...")
    be_output = output_dir_BE / "berkeley_earth_preprocessed.nc"
    era5_output = output_dir_ERA5 / "era5_preprocessed.nc"
    
    be.to_netcdf(be_output)
    print(f"  Saved: {be_output}")
    
    era5_interp.to_netcdf(era5_output)
    print(f"  Saved: {era5_output}")

    print("\nPreprocessing complete!")


if __name__ == "__main__":
    main()