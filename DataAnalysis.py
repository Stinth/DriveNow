import pandas as pd
import numpy as np
import os

###############################################
# Place DriveNow data in the path given below #
###############################################

df = pd.read_csv("Data/DTU-data-til-case_LTMZones1.csv", sep=";")
removeList = [[" ", "_"], ["(", ""], [")", ""]]
for remove, replaceWith in removeList:
    df.columns = [c.replace(remove, replaceWith) for c in df.columns]
# 'coerce' results in NaN for entries that can't be converted
df.Batteristatus_start = pd.to_numeric(df.Batteristatus_start, errors='coerce')
df.Batteristatus_slut = pd.to_numeric(df.Batteristatus_slut, errors='coerce')


# stringToDatetime
# converts dataframe colums eg. from list to type datetime with formating "%d/%m/%Y %H:%M"
def stringToDatetime(columns):
    for column in columns:
        df[column] = pd.to_datetime(df[column], dayfirst=True, format="%d/%m/%Y %H:%M")
    return


stringToDatetime(["Reservationstidspunkt", "Start_tidspunkt", "Slut_tidspunkt"])
df.sort_values(by=["Start_tidspunkt"], inplace=True)
# Dropping last 6 rows as the date for these rides are 2 months later than the last datapoint in the rest of the data
df.drop(df.tail(6).index, inplace=True)
# Dropping data lines with "-" as BilID
df.drop(df[df.BilID == "-"].index, inplace=True)
# replace "," with "." in strings
for column in ["Latitude_Start", "Latitude_Slut", "Longitude_Start", "Longitude_Slut"]:
    df[column] = df[column].str.replace(",", ".").astype(float)


# function should only be used on df's filtered to only ONE BilID
def fixDataMissing(df):
    if len(df.BilID.unique()) != 1:
        print("Please only use function fixDataMissing on df's filtered to ONE BilID!")
    else:
        # Drop all rows that start and stop in same exact X-coordinate
        df.drop(df[(df.Latitude_Start == df.shift(periods=-1).Latitude_Start) & (
                df.Latitude_Start == df.Latitude_Slut)].index, inplace=True)

        # If end point data is missing, fill in start data from next trip.
        for idx in df[(df.ToZoneID == 0) & (df.Latitude_Slut == "0") & (
                df.Latitude_Start != df.Latitude_Start.shift(periods=-1))].index.values.astype(int):
            df.at[idx, "Latitude_Slut"] = df.shift(periods=-1).at[idx, "Latitude_Start"]
            df.at[idx, "Longitude_Slut"] = df.shift(periods=-1).at[idx, "Longitude_Start"]
            df.at[idx, "ToZoneID"] = df.shift(periods=-1).at[idx, "ToZoneID"]

        # If FromZoneID or ToZoneID is empty, but coords populated, set *ZoneID=999999
        # This is a bug caused by cars parked on bridges or near water.
        for idx in df[(df.ToZoneID == 0) | (df.FromZoneID == 0) & (df.Latitude_Slut != "0")].index.values.astype(int):
            df.at[idx, "ToZoneID"] = 999999

        # If PersonID = PersonID.shift(periods=1) and time between slut and start < 5 min
        # use first coord start and last coord slut, first time start last time slut etc. combine km kørt
    return df


# Column tables for fixing
mergeColumns = ["Latitude_Start", "Longitude_Start", "Reservationstidspunkt", "Start_tidspunkt", "Batteristatus_start",
                "Km_kørt", "FromZoneID", "tripDuration"]


def fixMultiTravel(df):
    if len(df.BilID.unique()) != 1:
        print("Please only use function fixDataMissing on df's filtered to ONE BilID!")
    else:
        alterRows = df[(df.PersonID == df.PersonID.shift(periods=1)) & (df.idleTime <= 6)]
        dfshift = df.shift(periods=1)[(df.PersonID == df.PersonID.shift(periods=1)) & (df.idleTime <= 6)]
        dfnoshift = df[(df.PersonID == df.PersonID.shift(periods=1)) & (df.idleTime <= 6)]
        timeSeries = dfnoshift.tripDuration + dfshift.tripDuration - dfnoshift.idleTime.astype(float)
        df.loc[(df.PersonID == df.PersonID.shift(periods=1)) & (df.idleTime <= 6)].assign(
            Latitude_Start=dfshift.Latitude_Start,
            Longitude_Start=dfshift.Longitude_Start,
            Reservationstidspunkt=dfshift.Reservationstidspunkt,
            Start_tidspunkt=dfshift.Start_tidspunkt,
            Batteristatus_start=dfshift.Batteristatus_start,
            Km_kørt=dfnoshift.Km_kørt + dfshift.Km_kørt,
            FromZoneID=dfshift.FromZoneID,
            tripDuration=dfnoshift.tripDuration + dfshift.tripDuration - dfnoshift.idleTime.astype(float)
        )


# Adds column tripDuration in minutes to the dataframe
df["tripDuration"] = (df.Slut_tidspunkt - df.Start_tidspunkt).astype("timedelta64[m]")
# Adds column idleTime in minutes to the dataframe
df["idleTime"] = "default"

for BilID in df.BilID.unique():
    df[df.BilID == BilID] = fixDataMissing(df[df.BilID == BilID])

    #

    # Populates column idleTime by difference in last use end minus this use start time
    df.loc[df["BilID"] == BilID, ["idleTime"]] = (df[df["BilID"] == BilID]["Start_tidspunkt"] - df[df["BilID"] == BilID]
    ["Slut_tidspunkt"].shift(periods=1)).astype("timedelta64[m]")

import plotly.express as px

# fig = px.scatter_mapbox(df.tail(100), lat="Latitude_Start", lon="Longitude_Start", hover_name="TurID", hover_data=["BilID","tripDuration"],
#                         zoom=10, height=900, color="tripDuration") # color_continuous_scale=px.colors.cyclical.IceFire
# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()

# color_discrete_sequence=["fuchsia"]

ok = df.tail(100)
