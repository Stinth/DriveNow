#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 11:01:20 2020

@author: juliusrasmussen
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 14, 6
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.ar_model import AR



from statsmodels.tsa.arima_model import ARIMA


from DataAnalysis import *
from Plotting import *




def biggerZones(df):
    df['FromZoneID'] = df['FromZoneID'].floordiv(10)
    df['ToZoneID'] = df['ToZoneID'].floordiv(10)                              
    
    return
  
    
def timelags(df):
    df = df.set_index(['Start_tidspunkt'])
    d = df.groupby('FromZoneID').resample('3H')['TurID'].count()
    d = pd.DataFrame(d) 
    #d = d.reset_index(level=['FromZoneID'])

    #d = d.set_index(['Start_tidspunkt'])

    
    #d = df3timer.unstack(level=0)

    return d


def series_to_supervised(d, n_in=1, n_out=1, dropnan=True):
	"""
	Frame a time series as a supervised learning dataset.
	Arguments:
		data: Sequence of observations as a list or NumPy array.
		n_in: Number of lag observations as input (X).
		n_out: Number of observations as output (y).
		dropnan: Boolean whether or not to drop rows with NaN values.
	Returns:
		Pandas DataFrame of series framed for supervised learning.
	"""
	n_vars = 1 if type(d) is list else d.shape[1]
	df = pd.DataFrame(d)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = pd.concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg

def splitData(d):
    
    X_filter = series_to_supervised(d, 3, 1)
    target = X_filter['var1(t)']

    predictors = X_filter.drop('var1(t)', axis = 1)

    #autocorrelation_plot(target)
    
    return target, predictors

"""
def Autoregression(predictors):
    data = predictors
    model = AR(data)
    model_fit = model.fit()
    yhat = model_fit.predict(len(data), len(data))
    
    return yhat
"""


#model = ARIMA(d, order=(3,1,0))
#model_fit = model.fit(disp=0)
#print(model_fit.summary())
# plot residual errors
#residuals = pd(model_fit.resid)
#residuals.plot()
#plt.show()
#residuals.plot(kind='kde')
#plt.show()
#print(residuals.describe())
