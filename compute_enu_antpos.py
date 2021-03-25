# Compute the antenna positions in ENU/ECEF coordinates
# from the UTM system (eastings/northings) in HERA_350.txt

import numpy as np
import hera_mc
import cartopy
from pyuvdata import utils as uvutils
from hera_corr_cm import redis_cm
import json

# Read HERA_350.txt
ants = hera_mc.geo_sysdef.read_antennas()

# Using Cartopy convert UTM to Lat, Lon
latlon = cartopy.crs.Geodetic()

# I don't understand what the following does
geo = hera_mc.geo_handling.Handling()
lat_corr  = geo.lat_corr[geo.hera_zone[1]]

utm = cartopy.crs.UTM(geo.hera_zone[0])

# Convert UTM to Lat/Lon 
# LatLon to ECEF using pyuvdata.utils
#
# Finally convert ECEF to ENU using 
# coordinates of the center of the array (cofa)
# ENU coordinates are wrt center of the array

antpos_ENU = {}

# Extract cminfo from redis for cofa coordinates
cminfo = redis_cm.read_cminfo_from_redis(return_as='dict')
cofa_lat = cminfo['cofa_lat'] * np.pi/180.
cofa_lon = cminfo['cofa_lon'] * np.pi/180.
cofa_alt = cminfo['cofa_alt']

for ant, loc in ants.items():
    
    lon, lat = latlon.transform_point(loc['E'], loc['N'] - lat_corr, utm)

    # Convert the latitute-longitude to ECEF
    ecef = uvutils.XYZ_from_LatLonAlt(lat*np.pi/180, lon*np.pi/180, loc['elevation'])

    # Convert ECEF to ENU
    enu = uvutils.ENU_from_ECEF(ecef, cofa_lat, cofa_lon, cofa_alt)
    antpos_ENU[ant] = enu.tolist()

with open('HERA_350_ENU.json','w') as fp:
    json.dump(antpos_ENU, fp)

