import sys
sys.path.append('.')  # Add current directory to path

from src.data_loading.simple_loader import load_berkeley_earth, load_era5

# Test loading
print("Testing data loader...")

# Load Berkeley Earth
be_data = load_berkeley_earth()
print(f"Berkeley Earth shape: {be_data.dims}")
print(f"Variables: {list(be_data.data_vars)}")

print("\n")

# Load ERA5
era5_data = load_era5()
print(f"ERA5 shape: {era5_data.dims}")
print(f"Variables: {list(era5_data.data_vars)}")