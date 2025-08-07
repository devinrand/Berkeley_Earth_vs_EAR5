import xarray as xr
import yaml
import os
from pathlib import Path
import scipy.io as sio


def load_config():
    """Load the configuration file."""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    config_path = project_root / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_berkeley_earth(variable='tavg'):
    """Load Berkeley Earth data from path in config."""
    config = load_config()
    file_path = os.path.expanduser(config['data'][variable]['berkeley_earth_file'])
    return xr.open_dataset(file_path)

def load_era5():
    """Load ERA5 data from path in config."""
    config = load_config()
    file_path = os.path.expanduser(config['ERA5_monthly_folder'])    
    return xr.open_mfdataset(f"{file_path}/*.nc").load()

def load_processed_berkeley_earth(variable='tavg'):
    """Load processed Berkeley Earth data."""
    config = load_config()
    file_path = os.path.expanduser(config['processed'][variable]['berkeley_earth_file'])
    return xr.open_dataset(file_path)

def load_processed_era5(variable='tavg'):
    """Load processed ERA5 data."""
    config = load_config()
    file_path = os.path.expanduser(config['processed'][variable]['era5_file'])
    return xr.open_dataset(file_path)

def load_elevation_data():
    """Load elevation data from path in config."""
    config = load_config()
    file_path = os.path.expanduser(config['elevation_file'])
    return xr.open_dataset(file_path)

def load_station_density_data():
    config = load_config()
    file_path = os.path.expanduser(config['station_density_file'])
    return xr.open_dataset(file_path)

def load_processed_elevation_data():
    """Load processed elevation data."""
    config = load_config()
    file_path = os.path.expanduser(config['elevation_processed'])
    return xr.open_dataset(file_path)

def load_processed_station_density_data():
    """Load processed station density data."""
    config = load_config()
    file_path = os.path.expanduser(config['station_density_processed'])
    return xr.open_dataset(file_path)