import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
import datetime


def plot_map(df):
    # plots start coordinates from df onto OpenStreetMap tile
    # Currently size = idleTime and color = peak_hour
    fig = px.scatter_mapbox(df[(~df.idleTime.isnull()) & (df.idleTime > 0)], lat="Latitude_Start",
                            lon="Longitude_Start", hover_name="TurID",
                            hover_data=["BilID", "tripDuration", "FromZoneID", "idleTime"],
                            zoom=10, height=900, color="hour", size="idleTime",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=7)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

    # color_discrete_sequence=["fuchsia"]


# Plots trips per day for the entire period
def plot_trip_per_weekday(df):
    df['Hour'] = df['Start_tidspunkt'].values.astype('<M8[h]')
    res = df.groupby([df['Start_tidspunkt'].dt.day_name(), df['Hour'].dt.time])['Start_tidspunkt'].count()

    res = res.unstack(level=0)
    res.index = pd.to_datetime(res.index, format='%H:%M:%S')

    fig, ax = plt.subplots()
    hours = mdates.HourLocator(interval=3)
    h_fmt = mdates.DateFormatter('%H:%M:%S')

    # ax.plot(res.index, res.values, linewidth = 1)
    # or use
    res.plot(ax=ax, linewidth=1, x_compat=True,
             color=["#1A3780", "#336EFF", "#FF00E0", "#67B608", "#20459F", "#2D60DF", "#2652BF"])
    # Then tick and format with matplotlib:
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(h_fmt)
    ax.grid(axis='y')

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [1, 5, 6, 4, 0, 2, 3]
    plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], shadow=True, title="Weekday")
    plt.ylabel("Demand")

    fig.autofmt_xdate()
    plt.show()
    return


# Plots trips per day for the entire period
def plot_trip_per_day(df):
    df['date_week'] = df['Start_tidspunkt'].dt.strftime('%D')
    week_groups = df.groupby(df['date_week']
                             )['TurID'].count()

    week_groups = pd.DataFrame(week_groups)
    # week_groups = week_groups.set_index(['date_week'])

    week_groups.index = pd.to_datetime(week_groups.index)

    fig, ax = plt.subplots()
    ax.plot(week_groups)
    ax.set_xlim([datetime.date(2017, 7, 30), datetime.date(2017, 11, 10)])
    # Make ticks on occurrences of each month:
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    # Get only the month to show in the x-axis:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d-%Y'))
    ax.grid(axis='both')

    # '%b' means month as locale’s abbreviated name
    fig.autofmt_xdate()
    plt.ylabel("Demand")
    plt.show()

    return


def HistoUgedage(df):
    sorter = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sorterIndex = dict(zip(sorter, range(len(sorter))))
    week_df = df.groupby(df['Start_tidspunkt'].dt.day_name())['TurID'].count()

    week_df = pd.DataFrame(week_df)
    week_df['Day_id'] = week_df.index
    week_df['Day_id'] = week_df['Day_id'].map(sorterIndex)
    week_df.sort_values('Day_id', inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    ax.bar(week_df.Day_id, week_df.TurID, color = ["#1A3780", "#20459F", "#2652BF", "#2D60DF",  "#336EFF", "#67B608", "#FF00E0"])
    ax.set_xticks([x + 0 for x in week_df.Day_id])
    ax.set_xticklabels(week_df.index)

    # ax.set_axis_bgcolor('white')
    plt.show()
    return