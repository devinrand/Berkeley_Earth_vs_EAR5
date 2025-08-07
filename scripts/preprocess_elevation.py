import xarray as xr
from pathlib import Path
import os
import sys
# Dynamically determine the project root directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))  # Add project root to sys.path
from src.data_loading.simple_loader import load_processed_berkeley_earth, load_elevation_data, load_config

def preprocess_elevation():
    be = load_processed_berkeley_earth('tavg')
    elevation = load_elevation_data()
    # calculate average elevation for each quarter degree grid cell in the Berkeley Earth data
    coarsen_factor = 6
    elevation_coarse = elevation.coarsen(latitude=coarsen_factor, longitude=coarsen_factor, boundary='trim').mean()
    elevation_coarse_interp = elevation_coarse.interp_like(be)
    # save the processed elevation data
    config = load_config()
    save_path = Path(config['elevation_processed'])
    elevation_coarse_interp.to_netcdf(save_path)

# run from command line
if __name__ == "__main__":
    preprocess_elevation()
