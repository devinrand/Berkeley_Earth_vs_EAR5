from pathlib import Path
import sys
import os
# Dynamically determine the project root directory
project_root = Path(os.getcwd()).parent
sys.path.insert(0, str(project_root))
from src.data_loading.simple_loader import load_processed_berkeley_earth, load_processed_era5, load_config



class TemperatureDatasetMetrics:
    
    def __init__(self, variable='tavg'):
        """
        Initialize with a specific temperature variable.

        Variables: 'tavg', 'tmin', 'tmax'
        """
        self.variable = variable
        self.be_data = load_processed_berkeley_earth(variable)
        self.be_data['abs_temp'] = self.be_data.temperature.groupby('time.month')+self.be_data.climatology.rename({'month_number': 'month'})

        self.era5_data = load_processed_era5(variable)
        self.era5_data['abs_temp'] = self.era5_data.temperature.groupby('time.month') + self.era5_data.climatology - 273.15
        
        self.difference= self.be_data.temperature - self.era5_data.temperature
        self.abs_difference = self.be_data.abs_temp - self.era5_data.abs_temp
        
        self.config = load_config()
        
    def slice_data(self, time_slice=('1940-01-01', '2025-01-01'), lat_slice=(-90, 90), lon_slice=(-180, 180), land_only_flag=False):
        """Slice the data based on time, latitude, and longitude."""
        
        if land_only_flag:
            self.be_slice = self.be_data.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice)).where(self.be_data.land_mask)
            self.era5_slice = self.era5_data.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice)).where(self.be_data.land_mask)
            self.difference_slice = self.difference.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice)).where(self.be_data.land_mask)
            self.abs_difference_slice = self.abs_difference.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice)).where(self.be_data.land_mask)
        else:
            self.be_slice = self.be_data.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice))
            self.era5_slice = self.era5_data.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice))
            self.difference_slice = self.difference.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice))
            self.abs_difference_slice = self.abs_difference.sel(time=slice(*time_slice), latitude=slice(*lat_slice), longitude=slice(*lon_slice))

