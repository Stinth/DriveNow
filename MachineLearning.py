import pandas as pd


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
            return "Peak Saturday {}".format(dayName)
        if 24 >= clockTime >= 22:
            return "Off-Peak Weekend {}".format(dayName)
    if dayName == "Sunday":
        if 21 >= clockTime >= 9:
            return "Peak Sunday {}".format(dayName)
        if 9 >= clockTime >= 0:
            return "Off-Peak Weekend {}".format(dayName)
        if 24 >= clockTime >= 21:
            return "Off-Peak Evening {}".format(dayName)


# def manuel_block_sum(df):
#     for seri

expand_zones(df)

df["Time_Block"] = df.Start_tidspunkt.apply(lambda x: time_to_block(x))

# dfmelt = df.sort_values(by="Start_tidspunkt").copy()
# dfmelt.group
# print(dfmelt)
# def start_time_to_blocks(df):
#     df.iloc[df.Start_tidspunkt.dt.day_name() == ]
#     df["Time_block"] =

# df.melt(id_vars="FromZoneID", var_name="Time_Block", value_name=)
print(df)