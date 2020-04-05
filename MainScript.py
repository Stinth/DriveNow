import pandas as pd
import numpy as np
import os
from dateutil import tz
from datetime import datetime, timedelta
import seaborn

from DataAnalysis import *
from PlotMap import *

###############################################
# Place DriveNow data in the path given below #
###############################################

df = pd.read_csv("Data/DTU-data-til-case_LTMZones1.csv", sep=";")

#####################
# Dataframe Cleanup #
initial_columnname_changes(df)
stringToDatetime(df, ["Reservationstidspunkt", "Start_tidspunkt", "Slut_tidspunkt"])
sort_drop_nans_add_colums(df)

################
# Data cleanup #
# fixing various data problems
fixDataMissing(df)
update_idleTime(df)
# merging trips within a short timespan by the same PersonID
fixMultiTravel(df)
update_idleTime(df)

####################
# Outlier handling #
# drops any rows with a tripDuration larger than 3 times interquantile range
OutlierHandling(df)

#########################
# Plotting rides on map #
plot_map(df)
