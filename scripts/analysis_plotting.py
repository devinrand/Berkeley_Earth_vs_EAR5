import gstools as gs
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def seasonal_weighted_by_year(da, season):
    """Month-length–weighted seasonal means per year for one season."""
    sel = da.where(da['time.season'] == season, drop=True)
    w = sel.time.dt.days_in_month  # weights

    # Year labeling: for DJF, count December toward the NEXT year
    yr = xr.where(sel.time.dt.month == 12, sel.time.dt.year + 1, sel.time.dt.year) \
         if season == "DJF" else sel.time.dt.year

    # weighted mean within each season-year: sum(da*w)/sum(w)
    num = (sel * w).groupby(yr).sum(dim="time")
    den = w.groupby(yr).sum()
    out = num / den
    out = out.rename({"group": "year"}) if "group" in out.dims else out  # xarray may name it "group"
    out = out.assign_coords(year=out["year"])  # ensure coord exists for clarity
    return out



def map_plots(ds1,ds2,title1,title2):
    # compare summer tavg temperatures
    plt.figure(figsize=(18, 6))
    ax1 = plt.subplot(1, 3, 1, projection=ccrs.PlateCarree())
    ds1.plot(ax=ax1, transform=ccrs.PlateCarree(),vmin=-5)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title(title1)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(1, 3, 2, projection=ccrs.PlateCarree())
    ds2.plot(ax=ax1, transform=ccrs.PlateCarree(),vmin=-5)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title(title2)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(1, 3, 3, projection=ccrs.PlateCarree())
    (ds1-ds2).plot(ax=ax1, transform=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title('Difference')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 


def variogram(lats,lons,temps):
    """Calculate variograms using gstools"""
    bc,gamma = gs.vario_estimate(
        (lons, lats), temps,
        mesh_type="structured",
        latlon=True,
        geo_scale=np.degrees(1.0),
        bin_no=30,
        max_dist=5,
        sampling_size=1000
    )
    fit_model = gs.Stable(dim=2)
    fit_model.fit_variogram(bc,gamma,nugget=False)
    return fit_model, bc, gamma


def plot_variogram(lats,lons,be,era5,ax1):
    fit_model, bc, gamma = variogram(lats,lons,be)
    er_model, er_bc, er_gamma = variogram(lats,lons,era5)
    fit_model.plot(ax=ax1,color='blue',x_max=max(bc))
    ax1.scatter(bc,gamma,color='blue')
    er_model.plot(ax=ax1,color='red',x_max=max(er_bc))
    ax1.scatter(er_bc,er_gamma,color='red')


def map_plots_v2(ds1,ds2,title1,title2,lats,lons):
    # calculate temporal mean
    ds1_mean = ds1.mean(dim='year')
    ds2_mean = ds2.mean(dim='year')
    
    ds1_time_mean = ds1.mean(dim=['latitude','longitude'])
    ds2_time_mean = ds2.mean(dim=['latitude','longitude'])

    # compare summer tavg temperatures
    plt.figure(figsize=(18, 6))
    ax1 = plt.subplot(2, 3, 1, projection=ccrs.PlateCarree())
    ds1_mean.plot(ax=ax1, transform=ccrs.PlateCarree(),vmin=-5)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title(title1)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(2, 3, 2, projection=ccrs.PlateCarree())
    ds2_mean.plot(ax=ax1, transform=ccrs.PlateCarree(),vmin=-5)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title(title2)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(2, 3, 3, projection=ccrs.PlateCarree())
    (ds1_mean-ds2_mean).plot(ax=ax1, transform=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent([-10, 40, 35, 70], crs=ccrs.PlateCarree())
    ax1.set_title('Difference')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(2,3,4)
    fit_model, bc, gamma = variogram(lats,lons,ds1_mean)
    er_model, er_bc, er_gamma = variogram(lats,lons,ds2_mean)
    fit_model.plot(ax=ax1,color='blue',x_max=max(bc))
    ax1.scatter(bc,gamma,color='blue')
    er_model.plot(ax=ax1,color='red',x_max=max(er_bc))
    ax1.scatter(er_bc,er_gamma,color='red')

    ax1 = plt.subplot(2,3,5)
    ds1_time_mean.plot(ax=ax1, color='blue')
    ds2_time_mean.plot(ax=ax1, color='red')
    ax1.set_title('')

    ax1 = plt.subplot(2,3,6)
    diff = ds1 - ds2
    # remove 0's from diff
    diff = diff.where(diff != 0, drop=True)

    diff.plot.hist(bins=100, ax=ax1)
    mean = diff.mean().item()
    std = diff.std().item()
    #ax1.text(-3, 15000, f'Mean: {mean:.2f}')
    #ax1.text(-3, 10000, f'std: {std:.2f}')
    ax1.set_title(f'mean: {mean:.2f}, std: {std:.2f}')


def plot_average(TAVG,TMAX,TMIN,vec):
    """
    TAVG, TMAX, TMIN are temperature dataset objects
    vec is the spatial extent of the map plots
    """
    weights = TAVG.be_slice.areal_weight.fillna(0)
    BE_avg = TAVG.be_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    ER_avg = TAVG.era5_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    BE_avg_max = TMAX.be_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    ER_avg_max = TMAX.era5_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    BE_avg_min = TMIN.be_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    ER_avg_min = TMIN.era5_slice.temperature.weighted(weights).mean(dim=['latitude','longitude'])
    cmap = 'RdBu_r'
    vec = [-10, 40, 35, 70]
    plt.figure(figsize=(18,6))
    ax1 = plt.subplot(3,3,1)
    BE_avg.plot(ax=ax1,label='Berkeley Earth')
    ER_avg.plot(ax=ax1, label='ERA5')
    plt.legend()
    plt.title('TAVG')

    ax1 = plt.subplot(3,3,2)
    BE_avg_max.plot(ax=ax1,label='Berkeley Earth')
    ER_avg_max.plot(ax=ax1, label='ERA5')
    plt.legend()
    plt.title('TMAX')

    ax1 = plt.subplot(3,3,3)
    BE_avg_min.plot(ax=ax1,label='Berkeley Earth')
    ER_avg_min.plot(ax=ax1, label='ERA5')
    plt.legend()
    plt.title('TMIN')

    ax1 = plt.subplot(3,3,4,projection=ccrs.PlateCarree())
    pcm1 = (TAVG.be_slice.temperature.mean(dim='time')-TAVG.era5_slice.temperature.mean(dim='time')).plot(ax=ax1, transform=ccrs.PlateCarree(),add_colorbar=False, vmin=-2,vmax=2,cmap=cmap)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent(vec, crs=ccrs.PlateCarree())
    ax1.set_aspect('auto')
    ax1.set_title('')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(3,3,5,projection=ccrs.PlateCarree())
    (TMAX.be_slice.temperature.mean(dim='time')-TMAX.era5_slice.temperature.mean(dim='time')).plot(ax=ax1, transform=ccrs.PlateCarree(),add_colorbar=False, vmin=-2,vmax=2,cmap=cmap)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent(vec, crs=ccrs.PlateCarree())
    ax1.set_aspect('auto')
    ax1.set_title('')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    ax1 = plt.subplot(3,3,6,projection=ccrs.PlateCarree())
    (TMIN.be_slice.temperature.mean(dim='time')-TMIN.era5_slice.temperature.mean(dim='time')).plot(ax=ax1, transform=ccrs.PlateCarree(), vmin=-2,vmax=2,add_colorbar=False,cmap=cmap)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax1.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
    ax1.set_extent(vec, crs=ccrs.PlateCarree())
    ax1.set_aspect('auto')
    ax1.set_title('')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude') 

    diff_tavg = TAVG.be_slice.temperature - TAVG.era5_slice.temperature
    diff_tmax = TMAX.be_slice.temperature - TMAX.era5_slice.temperature
    diff_tmin = TMIN.be_slice.temperature - TMIN.era5_slice.temperature

    # plot histograms of differences
    ax1 = plt.subplot(3,3,7)
    diff_tavg.plot.hist(bins=100, ax=ax1)
    mean = diff_tavg.mean().item()
    std = diff_tavg.std().item()
    ax1.set_title(f'mean: {mean:.2f}, std: {std:.2f}')

    ax1 = plt.subplot(3,3,8)
    diff_tmax.plot.hist(bins=100, ax=ax1)
    mean = diff_tmax.mean().item()
    std = diff_tmax.std().item()
    ax1.set_title(f'mean: {mean:.2f}, std: {std:.2f}')

    ax1 = plt.subplot(3,3,9)
    diff_tmin.plot.hist(bins=100, ax=ax1)
    mean = diff_tmin.mean().item()
    std = diff_tmin.std().item()
    ax1.set_title(f'mean: {mean:.2f}, std: {std:.2f}')