import xarray as xr
import yaml
import os
from pathlib import Path

def load_config():
    """Load the configuration file."""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    config_path = project_root / 'config' / 'config.yaml'
    print(config_path)
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_berkeley_earth():
    """Load Berkeley Earth data from path in config."""
    config = load_config()
    
    # Get the file path and expand ~ to home directory
    file_path = os.path.expanduser(config['data']['berkeley_earth_file'])
    
    print(f"Loading Berkeley Earth from: {file_path}")
    ds = xr.open_dataset(file_path)
    
    return ds

def load_era5():
    """Load ERA5 data from path in config."""
    config = load_config()
    
    # Get the file path and expand ~ to home directory
    file_path = os.path.expanduser(config['data']['era5_file'])
    
    print(f"Loading ERA5 from: {file_path}")
    ds = xr.open_dataset(file_path)
    
    return ds

def load_processed_berkeley_earth():
    """Load processed Berkeley Earth data."""
    config = load_config()
    file_path = os.path.expanduser(config['data']['processed']['berkeley_earth_file'])
    print(f"Loading processed Berkeley Earth from: {file_path}")
    ds = xr.open_dataset(file_path)
    return ds

def load_processed_era5():
    """Load processed ERA5 data."""
    config = load_config()
    file_path = os.path.expanduser(config['data']['processed']['era5_file'])
    print(f"Loading processed ERA5 from: {file_path}")
    ds = xr.open_dataset(file_path)
    return ds