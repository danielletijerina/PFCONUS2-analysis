import numpy as np
from parflow.tools.io import read_pfb

def extract_station_indices_in_parflow_grid(station_stations, Latitude_pf ,Longitude_pf):
    """
    Given a dictionary of station locations, returns the row and column indices within the matrices of latitude and longitudes
    
    :station_stations: dictionary with the station ID as key (not necessary), and the lat and lon of the station stations['ID']=[lat,lon]
    :Latitude_pf: 2D array containing latitude of each grid cell (must match dimensions Longitude_pf)
    :Longitude_pf: 2D array containing longitude of each grid cell (must match dimensions Latitude_pf)
    
    :returns: a dictionary with as many entries as station_stations (same keys) and for each the row and col indices within the 2D lat/lon arrays
    """

    #create a matrix with the same shape as the PF matrix with either the row count or column count
    
    rows_indices = np.tile(np.matrix(np.linspace(0,Latitude_pf.shape[0]-1,Latitude_pf.shape[0])).T, (1,Latitude_pf.shape[1]))
    #0 0 0 ...
    #1 1 1 ...
    #Nx Nx Nx ...

    cols_indices = np.tile(np.matrix(np.linspace(0,Latitude_pf.shape[1]-1,Latitude_pf.shape[1])), (Latitude_pf.shape[0],1))
    #0 1 2 ... ny
    #0 1 2 ... ny

    def distance(lat1, lon1, lat2, lon2):
        #function to compute distance between two lat long points
        p = 0.017453292519943295
        hav = 0.5 - np.cos((lat2-lat1)*p)/2 + np.cos(lat1*p)*np.cos(lat2*p) * (1-np.cos((lon2-lon1)*p)) / 2
        return 12742 * np.arcsin(np.sqrt(hav))

    def closest(lats,lons, lat_point, lon_point,rows_indices,cols_indices):
        #returns the row and column of the closest point
        dist_ = distance(lat_point,lon_point,lats,lons)
        return [rows_indices[dist_ == np.nanmin(dist_)], cols_indices[dist_ == np.nanmin(dist_)]]
        

    #we can actually only consider cells realistically closest to our domain (buffer of buffer_degrees degrees in lat and lon)
    #SET THIS TO BE > THAN THE MAX DISTANCE BETWEEN STATION AND PF GRIDCELL (i.e. 1000m --> transformed to degrees)
    buffer_degrees = 5
    
    dictionary_out = {}

    #loop through stations
    for key in station_stations:
            #get latitude and longitude of current station
            curr_lat = station_stations[key][0]
            curr_lon = station_stations[key][1]

            #to speed up the process, you look only within a "buffer_degree" distance from the station
            mask_subset = np.ones(Latitude_pf.shape)
            mask_subset[Latitude_pf<curr_lat-buffer_degrees] = 0
            mask_subset[Latitude_pf>curr_lat+buffer_degrees] = 0
            mask_subset[Longitude_pf<curr_lon-buffer_degrees] = 0
            mask_subset[Longitude_pf>curr_lon+buffer_degrees] = 0

            #get the lats, lons, rows, cols, of the subset region of pixels within "buffer_degree" from the station
            subset_lats  = Latitude_pf[mask_subset>0]
            subset_lons  = Longitude_pf[mask_subset>0]
            subset_rows  = np.squeeze(np.array(rows_indices[mask_subset>0]))
            subset_cols  = np.squeeze(np.array(cols_indices[mask_subset>0]))

            #find closest cell
            curr_row,curr_col = closest(subset_lats, subset_lons,curr_lat,curr_lon,subset_rows,subset_cols)
            
            found_lat = Latitude_pf[int(curr_row),int(curr_col)]
            found_lon = Longitude_pf[int(curr_row),int(curr_col)]
            print(f'STATION: {key}')
            print(f'Current: {curr_lat} {curr_lon}, Found: {found_lat} {found_lon}')
            print(f'NY, NX: {int(curr_row),int(curr_col)}')
            print(" ")

            dictionary_out[key]=[int(curr_row),int(curr_col)]
    return dictionary_out

