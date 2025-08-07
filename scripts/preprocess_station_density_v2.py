import xarray as xr
from pathlib import Path
import numpy as np
import calendar
from xhistogram.xarray import histogram
import sys

# Dynamically determine the project root directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))  # Add project root to sys.path
from src.data_loading.simple_loader import load_processed_berkeley_earth, load_station_density_data, load_config

def preprocess_station_density():
    be = load_processed_berkeley_earth('tavg')
    station_data = load_station_density_data()
    
    # Create bin edges for histogram - need to extend beyond the actual grid points
    # to ensure all data is captured in the bins
    lat_edges = np.concatenate([
        [be.latitude.values[0] - (be.latitude.values[1] - be.latitude.values[0])/2],
        (be.latitude.values[:-1] + be.latitude.values[1:]) / 2,
        [be.latitude.values[-1] + (be.latitude.values[-1] - be.latitude.values[-2])/2]
    ])
    
    lon_edges = np.concatenate([
        [be.longitude.values[0] - (be.longitude.values[1] - be.longitude.values[0])/2],
        (be.longitude.values[:-1] + be.longitude.values[1:]) / 2,
        [be.longitude.values[-1] + (be.longitude.values[-1] - be.longitude.values[-2])/2]
    ])
    
    station_counts_array = np.zeros((len(be.time), len(be.latitude), len(be.longitude)))
    
    for i, time_val in enumerate(be.time):
        year = time_val.dt.year.item()
        month = time_val.dt.month.item()
        time_start = np.datetime64(f'{year}-{month:02d}-01')
        last_day = calendar.monthrange(year, month)[1]
        time_end = np.datetime64(f'{year}-{month:02d}-{last_day:02d}')
        
        time_slice = station_data.sel(time=slice(time_start, time_end))
        stations = time_slice.where(time_slice.occurrence_table==1).dropna('location', how='all').dropna('time', how='all')
        
        station_counts = histogram(
            stations.latitude,
            stations.longitude,
            bins=[lat_edges, lon_edges],
            dim=['location']
        )
        
        # Store the 2D array in the 3D array
        station_counts_array[i, :, :] = station_counts.values
    
    # Create the final dataset using Berkeley Earth coordinates directly
    all_stations = xr.Dataset({
        'station_counts': (['time', 'latitude', 'longitude'], station_counts_array)
    }, coords={
        'latitude': be.latitude,      # Use Berkeley Earth coordinates directly
        'longitude': be.longitude,    # Use Berkeley Earth coordinates directly
        'time': be.time
    })
    
    # Save the processed station density data
    config = load_config()
    save_path = Path(config['station_density_processed'])
    # delete the existing file if it exists
    if save_path.exists():
        save_path.unlink()
    # save the dataset to netcdf
    all_stations.to_netcdf(save_path)

# run from command line
if __name__ == "__main__":
    preprocess_station_density()