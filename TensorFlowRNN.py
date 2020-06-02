import numpy as np
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
import datetime
# Adapted code from https://towardsdatascience.com/time-series-forecasting-with-lstms-using-tensorflow-2-and-keras-in-python-6ceee9c6c651

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

def time_to_block_hourly(time):
    dayName = time.day_name()
    clockTime = time.hour
    if dayName in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}:
        return str(clockTime) + " " + "{}".format(dayName)

# %matplotlib inline
# %config InlineBackend.figure_format='retina'

sns.set(style='whitegrid', palette='muted', font_scale=1.5)

rcParams['figure.figsize'] = 16, 10

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

time = np.arange(0, 100, 0.1)
sin = np.sin(time) + np.random.normal(scale=0.5, size=len(time))

try:
    df = pd.read_pickle("Data/DTU_DriveNow_Cleaned_Data")
except FileNotFoundError:
    print("MISSING FILE IN DATA FOLDER; RUN MainScript!")

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

working_df = df_time_block[df_time_block.FromZoneID == 10215] ################### CHANGE VALUES HERE ###################################################################################
working_df["date_time_block"] = working_df.date.astype(str) + " " + working_df.Time_Block
working_df = working_df.groupby(["date_time_block"])["TurID"].sum()
time = np.arange(0, len(working_df.index)/10, 0.1)
df = pd.DataFrame(working_df.values, index=time, columns=["trips"])
# df['date_week'] = df['Start_tidspunkt'].dt.strftime('%D')
# hour_test = df[df.FromZoneID == 10234]
# hour_test["newtest"] = hour_test.date.astype(str) + " " + hour_test.hour.astype(str)
# hour_test = hour_test.groupby(["newtest"])["TurID"].count()
#
# time = np.arange(0, len(hour_test)/10, 0.1)
# df = pd.DataFrame(hour_test.values, index=time, columns=["trips"])

train_size = int(len(df) * 0.8)
test_size = len(df) - train_size
train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]
print(len(train), len(test))


def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)


time_steps = 10

# reshape to [samples, time_steps, n_features]

X_train, y_train = create_dataset(train, train.trips, time_steps)
X_test, y_test = create_dataset(test, test.trips, time_steps)

print(X_train.shape, y_train.shape)

model = keras.Sequential()
model.add(keras.layers.LSTM(
  units=128,
  input_shape=(X_train.shape[1], X_train.shape[2])
))
model.add(keras.layers.Dense(units=1))
model.compile(
  loss='mean_squared_error',
  optimizer=keras.optimizers.Adam(0.001)
)

history = model.fit(
    X_train, y_train,
    epochs=30,
    batch_size=16,
    validation_split=0.1,
    verbose=1,
    shuffle=False
)

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend();
plt.show()

y_pred = model.predict(X_test)

plt.plot(np.arange(0, len(y_train)), y_train, 'g', label="history")
plt.plot(np.arange(len(y_train), len(y_train) + len(y_test)), y_test, marker='.', label="true")
plt.plot(np.arange(len(y_train), len(y_train) + len(y_test)), y_pred, 'r', label="prediction")
plt.ylabel('Value')
plt.xlabel('Time Step')
plt.legend()
plt.show();


plt.plot(y_test, marker='.', label="true")
plt.plot(y_pred, 'r', label="prediction")
plt.ylabel('Value')
plt.xlabel('Time Step')
plt.legend()
plt.show();