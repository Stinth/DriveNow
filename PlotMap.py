import plotly.express as px

def plot_map(df):
    # plots start coordinates from df onto OpenStreetMap tile
    # Currently size = idleTime and color = peak_hour
    fig = px.scatter_mapbox(df[(~df.idleTime.isnull()) & (df.idleTime > 0)], lat="Latitude_Start", lon="Longitude_Start", hover_name="TurID", hover_data=["BilID","tripDuration","FromZoneID", "idleTime"],
                            zoom=10, height=900, color="hour", size="idleTime", color_continuous_scale=px.colors.cyclical.IceFire, size_max=7)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

    # color_discrete_sequence=["fuchsia"]