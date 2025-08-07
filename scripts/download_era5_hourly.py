import cdsapi
import os
import numpy as np
# run API to download ERA5 hourly data and save in specified folder 
# for different months. 

master_path = "/main/ERA5/Downloads/Hourly-t2m/"
#years = ["2024","2025"]
#months = ["01","02","03","04","05","06","07","08", "09", "10", "11", "12"]
years = np.arange(2014,2026).astype(str)
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

def download_era5_hourly(years, months, var = ["2m_temperature"]):
    for year in years:
        for month in months:
            # create target directory for each month
            target = f"{master_path}{year}/{month}/"
            month_folder = os.path.dirname(target)
            
            # create target folder if it does not exist
            if os.path.exists(month_folder):
                # remove all .nc files from month_folder
                for file in os.listdir(month_folder):
                    if file.endswith(".nc"):
                        os.remove(os.path.join(month_folder,file))
            else:
                # create the month folder if it does not exist
                os.makedirs(month_folder)
                
            target = f"{target}ERA5_t2m_{year}-{month}.nc"
            
            # run the API to download ERA5 hourly data
            dataset = "reanalysis-era5-single-levels"
            request = {
                "product_type": ["reanalysis"],
                "variable": var,
                "year": year,
                "month": month,
                "day": [
                    "01", "02", "03",
                    "04", "05", "06",
                    "07", "08", "09",
                    "10", "11", "12",
                    "13", "14", "15",
                    "16", "17", "18",
                    "19", "20", "21",
                    "22", "23", "24",
                    "25", "26", "27",
                    "28", "29", "30",
                    "31"
                ],
                "time": [
                    "00:00", "01:00", "02:00",
                    "03:00", "04:00", "05:00",
                    "06:00", "07:00", "08:00",
                    "09:00", "10:00", "11:00",
                    "12:00", "13:00", "14:00",
                    "15:00", "16:00", "17:00",
                    "18:00", "19:00", "20:00",
                    "21:00", "22:00", "23:00"
                ],
                "data_format": "netcdf",
                "download_format": "unarchived"
            }

            client = cdsapi.Client()
            client.retrieve(dataset, request, target)
            print(f"Downloaded {target}")

