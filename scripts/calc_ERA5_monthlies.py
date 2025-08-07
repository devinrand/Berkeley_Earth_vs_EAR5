import xarray as xr
import yaml
from pathlib import Path
import pandas as pd
import numpy as np
import sys
# Dynamically determine the project root directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))  # Add project root to sys.path
from src.data_loading.simple_loader import load_config


def calc_era5_monthlies(years):
    # load monthly netcdf hourly ERA5 data and save in monthly output netcdf files
    config = load_config()

    # path to load hourly data
    path = Path(config['ERA5_hourly_folder'])
    
    # loop through each month of each year, calculate monthly TAVG, TMAX, and TMIN
    for year in years:
        year_path = path / str(year)
        months = [f for f in year_path.iterdir() if f.is_dir()]
        months.sort(key=lambda x: x.name)
        for month in months:
            file = [f for f in month.iterdir() if f.suffix == '.nc']
            ds = xr.open_dataset(file[0])

            month_avg = xr.Dataset()

            # Add latitude and longitude as coordinates
            month_avg = month_avg.assign_coords({
                "latitude": ds.latitude,
                "longitude": ds.longitude,
            })

            # Calculate the mean time
            time_value = pd.to_datetime(ds.valid_time.mean(dim='valid_time').values)

            # Assign time as a coordinate
            month_avg = month_avg.assign_coords({"time": [time_value]})

            # Calculate TAVG. Dimensions are time, latitude and longitude.
            month_avg['TAVG'] = xr.DataArray(
                ds['t2m'].mean(dim='valid_time', keep_attrs=True).expand_dims('time'),
                dims=('time', 'latitude', 'longitude')
            )

            # Calculate TMAX and TMIN. Dimensions are time, latitude and longitude
            daily_max = ds['t2m'].groupby('valid_time.day').max()
            daily_min = ds['t2m'].groupby('valid_time.day').min()

            month_avg['TMAX'] = xr.DataArray(
                daily_max.mean(dim='day', keep_attrs=True).expand_dims('time'),
                dims=('time', 'latitude', 'longitude')
            )

            month_avg['TMIN'] = xr.DataArray(
                daily_min.mean(dim='day', keep_attrs=True).expand_dims('time'),
                dims=('time', 'latitude', 'longitude')
            )

            # Save monthly averages to netcdf file
            savepath = Path(config['ERA5_monthly_folder'])
            savepath.mkdir(parents=True, exist_ok=True)
            month_avg.to_netcdf(savepath / f"monthly_avg_{year}_{month.name}.nc", mode='w')
            print(f"Saved ERA5 Raw Monthly {year} - {month}")


# Run from command line
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Convert command-line arguments to a range of years
        start_year = int(sys.argv[1])
        end_year = int(sys.argv[2]) if len(sys.argv) > 2 else start_year
        years = range(start_year, end_year + 1)
    else:
        # Default range of years
        years = range(1940, 2026)
    main(years)