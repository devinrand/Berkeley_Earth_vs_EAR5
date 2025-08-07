
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.calc_ERA5_monthlies import calc_era5_monthlies
from scripts.preprocess_v2 import preprocess_v2
from scripts.download_era5_hourly import download_era5_hourly


# specify years for analysis
#years = ['2024', '2025']
# create list of years from 1940 to 2024
years = [str(year) for year in range(2014, 2025)]


# specify months for analysis
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# download ERA5 hourly data
download_era5_hourly(years, months)


# calculate monthly averages
calc_era5_monthlies(years)

# preprocess monthly averaged data
preprocess_v2()

# calculate metrics



