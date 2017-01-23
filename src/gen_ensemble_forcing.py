
''' This script perturbs original forcing and generate and ensemble of forcing
    data

    Usage:
        $ python gen_ensemble_forcing.py config_file
'''

import sys
import numpy as np
import xarray as xr
import os
import pandas as pd
from collections import OrderedDict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from tonic.models.vic.vic import VIC
from tonic.io import read_config, read_configobj
from da_utils import Forcings, perturb_forcings_ensemble


# ============================================================ #
# Process command line arguments
# ============================================================ #
# Read config file
cfg = read_configobj(sys.argv[1])


# ============================================================ #
# Set random generation seed
# ============================================================ #
np.random.seed(cfg['CONTROL']['seed'])


# ============================================================ #
# Prepare perturbed forcing data for each ensemble member
# ============================================================ #

# --- Process config file arguments --- #
start_time = pd.to_datetime(cfg['ENSEMBLE']['start_time'])
end_time = pd.to_datetime(cfg['ENSEMBLE']['end_time'])
orig_forcing_basedir = os.path.join(
                            cfg['CONTROL']['root_dir'],
                            cfg['FORCING']['orig_forcing_nc_basepath'])
output_basedir = os.path.join(cfg['CONTROL']['root_dir'],
                              cfg['OUTPUT']['output_basedir'])
N = cfg['ENSEMBLE']['N']

# --- Process forcing names in the input forcing netCDF file --- #
# Construct forcing variable name dictionary
dict_varnames = {}
dict_varnames['PREC'] = cfg['FORCING']['PREC']

# --- Perturb forcings to generate ensemble (the whole time series is --- #
# --- perturbed together to allow temporal autocorrelation as a whole --- #
# Load in original forcings for all years
start_year = start_time.year
end_year = end_time.year

list_ds = []
for year in range(start_year, end_year+1):
    ds = xr.open_dataset('{}{}.nc'.format(orig_forcing_basedir, year))
    list_ds.append(ds)
ds_all_years = xr.concat(list_ds, 'time')

# Perturb and generate forcing ensemble
class_forcings_orig = Forcings(ds_all_years)
perturb_forcings_ensemble(N, orig_forcing=class_forcings_orig,
                          dict_varnames=dict_varnames,
                          prec_std=cfg['FORCING']['prec_std'],
                          prec_phi=cfg['FORCING']['phi'],
                          out_forcing_basedir=output_basedir)


