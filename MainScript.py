import pandas as pd
import numpy as np
import os
from dateutil import tz
from datetime import datetime, timedelta
import seaborn
import matplotlib.pyplot as plt

from DataAnalysis import *
from Plotting import *

# Dataframe visual settings
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


try:
    df = pd.read_pickle("Data/DTU_DriveNow_Cleaned_Data")
except FileNotFoundError:
    ###############################################
    # Place DriveNow data in the path given below #
    ###############################################

    df = pd.read_csv("Data/DTU-data-til-case_LTMZones1.csv", sep=";")

    #####################
    # Dataframe Cleanup #
    initial_columnname_changes(df)
    stringToDatetime(df, ["Reservationstidspunkt", "Start_tidspunkt", "Slut_tidspunkt"])
    sort_drop_nans_add_colums(df)
    add_hour_and_date(df)

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
    drop_first_and_last_day(df)

    df.to_pickle("Data/DTU_DriveNow_Cleaned_Data")


#########################
# Plotting rides on map #
# plot_map(df)
plot_trip_per_day(df)
plot_trip_per_weekday(df)
print(statistics_table(df))
HistoUgedage(df)