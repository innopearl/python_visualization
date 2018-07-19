#!/usr/bin/env python

########## REQUIRE
#pip install -U pip wheel setuptools
#python3 -mpip install pandas_datareader
#python3 -mpip install pandas
#python3 -mpip install matplotlib
#

from utils import *
from channels import *
from nextlogging import *


import matplotlib
from matplotlib import gridspec
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
#matplotlib.use('Agg')
import pandas as pd
import pandas_datareader.data as web

import matplotlib.pyplot as plt
from matplotlib import dates
from datetime import datetime

### Removed modal stuffs here
        
if __name__ == "__main__":
    initLogger(__name__, None)
    logger = logging.getLogger(__name__)

    # Setup Argument Parser
    parser = argparse.ArgumentParser(description='Poloniex/Bittrex Arbitrage Bot')
    parser.add_argument('-s', '--symbol', default='XMR', type=str, required=False, help='symbol of your target coin [default: XMR]')
    parser.add_argument('-b', '--basesymbol', default='BTC', type=str, required=False, help='symbol of your base coin [default: BTC]')
    parser.add_argument('-r', '--rateBid', default=1.01, type=float, required=False, help='minimum price difference, 1.01 is 1 percent price difference (exchanges charge .05 percent fee) [default: 1.01]')
    parser.add_argument('-R', '--rateAsk', default=1.01, type=float, required=False, help='minimum price difference, 1.01 is 1 percent price difference (exchanges charge .05 percent fee) [default: 1.01]')
    parser.add_argument('-t', '--tickSize', default=1.0, type=float, required=False, help='minimun quantity to buy or sell [default: 1]')
    parser.add_argument('-c', '--config', default='arbbot.conf', type=str, required=False, help='config file [default: arbbot.conf]')
    parser.add_argument('-l', '--logfile', default='arbbot.log', type=str, required=False, help='file to output log data to [default: arbbot.log]')
    parser.add_argument('-B', '--bidref', type=float, required=False, help='Set bid price reference')
    parser.add_argument('-A', '--askref', type=float, required=False, help='Set ask price reference')
    parser.add_argument('-S', '--maxPctSpread', default=0.2, type=float, required=False, help='Maximum spread in percentage of Ask price reference')
    parser.add_argument('-d', '--duration', default=3600, type=int, required=False, help='Duration in seconds')
    args = parser.parse_args()

    config = {}
    modal = AnalyticModal(config)
    modal.loadMarketData('{}_{}.json'.format(args.basesymbol, args.symbol), args.duration)

    df = pd.DataFrame(modal.rows, columns = ["time", "last", "mAvgShort", "mAvgLong", "mAvgULong", "MTrend", "mTrend"])
    print(df.head())

    # Get the exec price time series. This now returns a Pandas Series object indexed by time
    time = df.ix[:, 'time']
    last = df.ix[:, 'last']

    myShort = df.ix[:, 'mAvgShort']
    myLong = df.ix[:, 'mAvgLong']
    myULong = df.ix[:, 'mAvgULong']

    MTrend = df.ix[:, 'MTrend']
    mTrend = df.ix[:, 'mTrend']

    print('len {}'.format(len(time)))
    # Calculate the 20 and 100 days moving averages of the closing prices
    short_rolling_last = last.rolling(window=60).mean()
    long_rolling_last = last.rolling(window=300).mean()
    xlong_rolling_last = last.rolling(window=600).mean()

    # Plot everything by leveraging the very powerful matplotlib package
    plt.style.use('default')
    plt.xticks(rotation=30)
    fig = plt.figure()
    gs  = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    ax = plt.subplot(gs[0])
    bx = plt.subplot(gs[1])
    #fig.autofmt_xdate()
    ax.fmt_xdata = DateFormatter("%Y-%m-%d %H:%M:%S")
    bx.fmt_xdata = DateFormatter("%Y-%m-%d %H:%M:%S")

    ax.set_xlabel('Date')
    ax.set_ylabel('Adjusted closing price ($)')

    bx.set_xlabel('Date')
    bx.set_ylabel('Trend')

    #http://leancrew.com/all-this/2015/01/labeling-time-series/
    days = dates.DayLocator()
    hours = dates.HourLocator()
    minutes = dates.MinuteLocator()
    seconds = dates.SecondLocator()
    dfmt = dates.DateFormatter('%m%d-%H:%M')

    #2018-03-16 13:25:31,113
    #datemin = datetime.strptime(time[0], "%Y-%m-%d %H:%M:%S")
    #datemax = datetime.strptime(time[len(time)-1], "%Y-%m-%d %H:%M:%S")
    #logger.info('{}  {}'.format(datemin, datemax)) 


    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_minor_locator(minutes)
    ax.xaxis.set_major_formatter(dfmt)
    #ax.set_xlim(datemin, datemax)
    #ax.set_xlim(time[0], time[len(time)-1])

    #https://matplotlib.org/users/colors.html
    time = pd.to_datetime(time)
    ax.plot(time, last, label='BTC_XMR', color='C0')
    ax.plot(time, myShort, color='C1', label='my Short')
    ax.plot(time, myLong, color='C2', label='my Long')
    ax.plot(time, myULong, color='C3', label='my ULong')
    ax.legend()



    modal.trends.insert(0, {"time": time[0], "MTrend": 0, "mTrend": 0})
    modal.trends.insert(len(modal.trends), {"time": time[len(time)-1], "MTrend": 0, "mTrend": 0})
    df2 = pd.DataFrame(modal.trends, columns = ["time", "MTrend", "mTrend"])
    print(df2)

    time = df2.ix[:, 'time']
    MTrend = df2.ix[:, 'MTrend']
    mTrend = df2.ix[:, 'mTrend']

    bx.xaxis.set_major_locator(hours)
    bx.xaxis.set_minor_locator(minutes)
    bx.xaxis.set_major_formatter(dfmt)
    bx.step(time, MTrend, color='C7', label='MTrend')
    bx.step(time, mTrend, color='C8', label='mTrend')
    bx.legend()
    plt.show()
