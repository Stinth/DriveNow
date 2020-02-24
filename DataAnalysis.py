import pandas as pd
import numpy as np
import os

df = pd.read_csv("Data/DTU-data-til-case_LTMZones1.csv", sep=";")
removeList = [[" ", "_"], ["(", ""], [")", ""]]
for remove, replaceWith in removeList:
    df.columns = [c.replace(remove, replaceWith) for c in df.columns]
# 'coerce' results in NaN for entries that can't be converted
df.Batteristatus_start = pd.to_numeric(df.Batteristatus_start,errors='coerce')
df.Batteristatus_slut = pd.to_numeric(df.Batteristatus_slut, errors='coerce')

# Dropping last 6 rows as the date for these rides are 2 months later than the last datapoint in the rest of the data
df.drop(df.tail(6).index, inplace=True)
# Dropping data lines with "-" as BilID
df.drop(df[df.BilID == "-"].index, inplace=True)


# stringToDatetime
# converts dataframe colums eg. from list to type datetime with formating "%d/%m/%Y %H:%M"
def stringToDatetime(columns):
    for column in columns:
        df[column] = pd.to_datetime(df[column], dayfirst=True, format="%d/%m/%Y %H:%M")
    return


stringToDatetime(["Reservationstidspunkt", "Start_tidspunkt", "Slut_tidspunkt"])
df.sort_values(by=["Start_tidspunkt"], inplace=True)


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


# Adds column tripDuration in minutes to the dataframe
df["tripDuration"] = (df.Slut_tidspunkt - df.Start_tidspunkt).astype("timedelta64[m]")
# Adds column idleTime in minutes to the dataframe
df["idleTime"] = "default"
for BilID in df.BilID.unique():
    df.loc[df["BilID"] == BilID, ["idleTime"]] = (df[df["BilID"] == BilID]["Start_tidspunkt"] - df[df["BilID"] == BilID]
    ["Slut_tidspunkt"].shift(periods=1)).astype("timedelta64[m]")
