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
    station_counts_array = np.zeros((len(be.time), len(be.latitude)-1, len(be.longitude)-1))

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
            bins=[be.latitude.values, be.longitude.values],
            dim=['location']
        )
        
        # Store the 2D array in the 3D array
        station_counts_array[i, :, :] = station_counts.values

    # Create the final dataset using the histogram's coordinates
    all_stations = xr.Dataset({
        'station_counts': (['time', 'latitude', 'longitude'], station_counts_array)
    }, coords={
        'latitude': station_counts.latitude_bin,  # Use the bin coordinates from histogram
        'longitude': station_counts.longitude_bin,
        'time': be.time
    })

    # rename coordinates latitude_bin and longitude_bin to latitude and longitude
    all_stations = all_stations.swap_dims({'latitude_bin': 'latitude', 'longitude_bin': 'longitude'}) 
    # remove coordinates latitude_bin and longitude_bin
    all_stations = all_stations.reset_coords(['latitude_bin', 'longitude_bin'], drop=True)
    
    # Save the processed station density data
    config = load_config()
    save_path = Path(config['station_density_processed'])
    all_stations.to_netcdf(save_path)

# run from command line
if __name__ == "__main__":
    preprocess_station_density()

