import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error

try:
    df = pd.read_pickle("Data/DTU_DriveNow_Cleaned_Data")
except FileNotFoundError:
    print("MISSING FILE IN DATA FOLDER; RUN MainScript!")


def expand_zones(df):
    df['FromZoneID'] = df['FromZoneID'].floordiv(10)
    df['ToZoneID'] = df['ToZoneID'].floordiv(10)
    return


def get_day_before(dayName):
    if dayName == "Monday":
        return "Sunday"
    if dayName == "Tuesday":
        return "Monday"
    if dayName == "Wednesday":
        return "Tuesday"
    if dayName == "Thursday":
        return "Wednesday"
    if dayName == "Friday":
        return "Thurday"
    if dayName == "Saturday":
        return "Friday"
    if dayName == "Sunday":
        return "Saturday"


def time_to_block(time):
    dayName = time.day_name()
    clockTime = time.hour
    if dayName in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}:
        if 7 >= clockTime >= 0:
            return "Off-Peak Evening {}".format(get_day_before(dayName))
        elif 10 >= clockTime >=7:
            return "Peak Morning {}".format(dayName)
        elif 17 >= clockTime >= 10:
            return "Off-Peak Morning {}".format(dayName)
        elif 21 >= clockTime >= 17:
            return "Peak Evening {}".format(dayName)
        elif 24 >= clockTime >= 21:
            return "Off-Peak Evening {}".format(dayName)
    if dayName == "Saturday":
        if 8 >= clockTime >= 0:
            return "Off-Peak Morning {}".format(dayName)
        if 22 >= clockTime >= 8:
            return "Peak {}".format(dayName)
        if 24 >= clockTime >= 22:
            return "Off-Peak Weekend {}".format(dayName)
    if dayName == "Sunday":
        if 21 >= clockTime >= 9:
            return "Peak {}".format(dayName)
        if 9 >= clockTime >= 0:
            return "Off-Peak Weekend {}".format(dayName)
        if 24 >= clockTime >= 21:
            return "Off-Peak Evening {}".format(dayName)

def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def plotMovingAverage(series, window, plot_intervals=False, scale=1.96, plot_anomalies=False):
    """
        series - dataframe with timeseries
        window - rolling window size
        plot_intervals - show confidence intervals
        plot_anomalies - show anomalies

    """
    rolling_mean = series.rolling(window=window).mean()

    plt.figure(figsize=(15, 5))
    plt.title("Moving average\n window size = {}".format(window))
    plt.plot(rolling_mean, "g", label="Rolling mean trend")

    # Plot confidence intervals for smoothed values
    if plot_intervals:
        mae = mean_absolute_error(series[window:], rolling_mean[window:])
        deviation = np.std(series[window:] - rolling_mean[window:])
        lower_bond = rolling_mean - (mae + scale * deviation)
        upper_bond = rolling_mean + (mae + scale * deviation)
        plt.plot(upper_bond, "r--", label="Upper Bond / Lower Bond")
        plt.plot(lower_bond, "r--")

        # Having the intervals, find abnormal values
        if plot_anomalies:
            anomalies = pd.DataFrame(index=series.index, columns=series.columns)
            anomalies[series < lower_bond] = series[series < lower_bond]
            anomalies[series > upper_bond] = series[series > upper_bond]
            plt.plot(anomalies, "ro", markersize=10)

    plt.plot(series[window:], label="Actual values")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.show()


# def manuel_block_sum(df):
#     for seri

expand_zones(df)

df["Time_Block"] = df.Start_tidspunkt.apply(lambda x: time_to_block(x))
df_time_block = df.groupby(["FromZoneID", "date", "Time_Block"])["TurID"].count()
df_time_block = df_time_block.reset_index()

df_time_block_shift = df_time_block.shift(periods=-1)
indexvals = df_time_block[(df_time_block.FromZoneID == df_time_block_shift.FromZoneID) &
                          (df_time_block.Time_Block == df_time_block_shift.Time_Block) &
                          (df_time_block.date - df_time_block_shift.date <= datetime.timedelta(-1))].index.values
df_time_block.loc[indexvals, "TurID"] = df_time_block.loc[indexvals, "TurID"] +\
                                        df_time_block_shift.loc[indexvals, "TurID"]


print(df_time_block)
working_df = pd.DataFrame
for ZoneID in df_time_block.FromZoneID.unique():
    if ZoneID == 9999:
        print("skip")
    else:
        working_df = df_time_block[df_time_block.FromZoneID == ZoneID]
        working_df["date_time_block"] = working_df.date.astype(str) + " " + working_df.Time_Block
        working_df = working_df.groupby(["date_time_block"])["TurID"].sum()
        print(working_df)
        plotMovingAverage(working_df, 4)