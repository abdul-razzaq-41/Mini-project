import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yf
import datetime as dt
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import math 


class DistributedInvestment():
    def __init__(self,start_date, end_date, stock_name: list):
        self.start_date = start_date
        self.end_date = end_date
        self.stock_name = stock_name
        self.data = pd.DataFrame()
        self.ticker_list = list()
        self.buy_sell_data = pd.DataFrame()
        
        yf.pdr_override()
        
        
    def get_stocks_details(self):
        self.data = pd.DataFrame()
        no_stock_list = list()
        
        for stock in self.stock_name:
            try:
                df = pdr.get_data_yahoo(stock,start=self.start_date,end=self.end_date)
                df['Ticker'] = stock
                df['%change'] = np.nan
                for j in range(1,df.shape[0]):
                    df['%change'][j] = (
                        (np.floor(df['Open'][j] - df['Close'][j-1]))/np.abs(df['Close'][j]))*100

                        ##((px_last - px_open) / px_open) * 100
                
                self.data = self.data.append(df)
                del df
            except Exception as e:
                no_stock_list.append(stock)
        
        Title = "Compare stocks with " 
        length = 0
        for s in self.stock_name:
            if length == len(self.stock_name) - 1:
                Title += s
            else:
                Title += s + " and "
                length += 1

        return self.data    


    def filterByStock(self):
        result = dict()
        for stock in self.stock_name:
            mean = (self.data[self.data['Ticker'] == stock]["%change"]) * 100
            result[stock] = np.mean(mean)

        return result