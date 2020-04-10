import plotly.express as px
import matplotlib.pyplot as plt

def plot_map(df):
    # plots start coordinates from df onto OpenStreetMap tile
    # Currently size = idleTime and color = peak_hour
    fig = px.scatter_mapbox(df[(~df.idleTime.isnull()) & (df.idleTime > 0)], lat="Latitude_Start", lon="Longitude_Start", hover_name="TurID", hover_data=["BilID","tripDuration","FromZoneID", "idleTime"],
                            zoom=10, height=900, color="hour", size="idleTime", color_continuous_scale=px.colors.cyclical.IceFire, size_max=7)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

    # color_discrete_sequence=["fuchsia"]


# Plots trips per day for the entire period
def plot_trip_per_weekday(df):
    # week_df = df.groupby([df['Start_tidspunkt'].dt.weekday_name, df['Start_tidspunkt'].dt.hour])['Start_tidspunkt'].count()
    res = df.groupby([df['Start_tidspunkt'].dt.day_name(), df['Start_tidspunkt'].dt.hour])['Start_tidspunkt'].count()
    res.index.names = ["Weekday", "Hour of the day"]

    res.unstack(level=0).plot(color=["#1A3780", "#336EFF", "#FF00E0", "#67B608", "#20459F", "#2D60DF", "#2652BF"])
    # plt.set_cmap("viridis")
    handles, labels = plt.gca().get_legend_handles_labels()
    order = [1,5,6,4,0,2,3]
    plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], shadow=True, title="Weekday")
    plt.ylabel("Demand")
    plt.show()
    return


# Plots trips per day for the entire period
def plot_trip_per_day(df):
    df['date_week'] = df['Start_tidspunkt'].dt.strftime('%D')
    week_groups = df.groupby(df['date_week']
                             )['date_week'].count()
    plt.figure()
    week_groups.plot(figsize=(10, 5), legend=None)
    plt.ylabel("Demand")
    plt.show()

    return