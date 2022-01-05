import streamlit as st
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import plotly.express as px
import datetime
import plotly.graph_objects as go
from streamlit.state.session_state import Value
from ModelAnalysis import ModelAnalysis
from getStockData import DistributedInvestment
import sqlite3
import base64
import time
from app import getSentiments
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)


st.markdown("<h1 style='text-align: center;font-style: italic; color: purple;'>INVESTMENT PLANNER</h1>", unsafe_allow_html=True)
st.image(
            "https://i.gifer.com/7D7o.gif",
            width=900,
        )

st.sidebar.title('Applications')

if st.sidebar.checkbox('Get started'):
    x=st.sidebar.radio("Strategy",["Percentage Return","Sentiment Analysis","Historic Data Analysis"])
    about_me = st.sidebar.checkbox("Know the Developer")

    if x == "Percentage Return":
        ## taking prev and current date to extract stocks prices
        today = datetime.date.today()
        prev = today - datetime.timedelta(days=365)
        curr = datetime.date.today()
        start_date = st.date_input('Start date', prev)
        end_date = st.date_input('End date', curr)

        ## entering different tickers for distributed investments as a comma separated .

        user_input_compare = st.text_input("Write Stock Ticker separate by comma's ")
        if user_input_compare:
            user_input_compare = str(user_input_compare)
            user_input_compare = user_input_compare.split(",")
            DI = DistributedInvestment(start_date, end_date, user_input_compare)
            st.write(DI.get_stocks_details())
            

            ## filtering stocks by there %change value
            ## and calculating the return over the past few days/months.
            results = DI.filterByStock()
            for key, value in results.items():
                x= "MAX. RETURN FOR "+str(key) +" : "+str(value) +"%"
                # st.markdown(x)
                html_str = f"""
                <style>
                p.a {{
                font: bold 30px Courier;
                }}
                </style>
                <p class="a">{x}</p>
                """

                st.markdown(html_str, unsafe_allow_html=True)
                # # st.markdown(key)
                # # st.markdown(value)

    ## analysis of historic data by plotting different graphs and analysing them            
    elif x == 'Historic Data Analysis':
        progress=st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i+1)

        def main(ticker_name_list):
            today = datetime.date.today()
            prev = today - datetime.timedelta(days=365)
            curr = datetime.date.today()
            start_date = st.date_input('Start date', prev)
            end_date = st.date_input('End date', curr)
            
            ## selecting one stock ticker ysing selectbox
            if start_date < end_date:
                stock_name = st.selectbox(label='Select Stock ticker:',options=ticker_name_list)
                
                MA = ModelAnalysis(start_date, end_date, stock_name)
                data = MA.get_stock_name()
                st.write("Stocks for previous 14 Days.....")
                st.write(data.tail(14))
                
                ## download function for the above table
                def get_table_download_link(df):
                    """Generates a link allowing the data in a given panda dataframe to be downloaded
                    in:  dataframe
                    out: href string
                    """
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(
                        csv.encode()
                    ).decode()  # some strings <-> bytes conversions necessary here
                    
                    return f'<a href="data:file/csv;base64,{b64}" download="mypredications.csv">Download the above table in the form of csv</a>'
                
                st.markdown(get_table_download_link(data), unsafe_allow_html=True)

                ## different types of plotting techniques
                stock_column = st.sidebar.selectbox(label='Select Column to Draw Plot:',options=data.columns)
                stock_column = str(stock_column)
                
                fig = MA.get_plot(stock_column)
                
                agree = st.sidebar.selectbox("Visualization",["Plot","Inline Plot","Expontential Moving Average Plot","Candle Plot"])
                
                if agree=="Inline Plot":
                    if fig is None:
                        st.write('The name is not valid.Please check the name')
                    else:
                        st.plotly_chart(fig)
                
                if agree=="Expontential Moving Average Plot":
                    st.write(
                        "An exponential moving average (EMA) is a type of moving average (MA) that places a greater weight and significance on the most recent data points. EMA gives the direction in which the stocks is going."
                    )
                    fig = MA.ewa_sma()
                    if fig is None:
                        st.write('The name is not valid.Please check the name')
                    else:
                        st.plotly_chart(fig)
                        
                if agree=="Candle Plot":
                    fig = MA.candle_plot()
                    if fig is None:
                        st.write('The name is not valid.Please check the name')
                    else:
                        st.plotly_chart(fig)

                user_input_compare = st.sidebar.text_input("Compare stocks by Write Stock Ticker separate by comma's ")
                if user_input_compare:
                    user_input_compare = str(user_input_compare)
                    user_input_compare = user_input_compare.split(",")
                    user_input_compare = [user.upper().strip() for user in user_input_compare]
                    fig, no_stocks = MA.compare_stocks(user_input_compare)
                    if fig is None or user_input_compare is None:
                        st.write("data for the stocks given is not available")
                    else:
                        st.plotly_chart(fig)
                        for i in no_stocks:
                            st.write('<font color="blue"> No stock data available for {}</font>'.format(i),unsafe_allow_html=True\
                                        )    

                user_input = st.sidebar.text_input("Know Trading Strategy by Entering Stock Ticker separate by comma's ")
                if user_input:
                    user_input = str(user_input)
                    user_input = user_input.split(",")
                    details = MA.buy_sell(user_input)
                    if details is None or user_input is None:
                        st.write("data for the stocks given is not available")
                    else:
                        st.write(details)
                        if len(details['Ticker'].unique()) != len(user_input):
                            ticker_missing = set(user_input).difference(details['Ticker'].unique())
                            for i in ticker_missing:
                                st.write('<font color="blue"> No stock data available for {}</font>'.format(i),unsafe_allow_html=True\
                                        )
                            st.markdown(get_table_download_link(details), unsafe_allow_html=True)
                
            else:
                st.warning("Start end should be less than end date")


        if __name__ == "__main__":
            database = 'ticker.db'
            st.info(''' Here, you can analyse and take decision regarding stocks with more than 450+ stock tickers ''')
            st.markdown('**Make sure that start date is less than end date**.')
            conn = sqlite3.connect(database)
            df = pd.read_sql_query("select * from sqlite_master where tbl_name ='stock_ticker' ", con=conn)

            st_names = pd.read_sql_query("""
                SELECT * 
                FROM stock_ticker;
            """,conn)
            
            ticker_name_list = list()

            for i in range(st_names.shape[0]):
                ticker_name_list.append(st_names['Tickers'][i])

            main(ticker_name_list)
            
            conn.close()

    if x == 'Sentiment Analysis':
        user_input_compare = st.text_input("Write Stock Ticker separate by comma's ")
        user_input_compare = str(user_input_compare)
        user_input_compare = user_input_compare.split(",")
        user_input_compare = [user_input.upper().strip() for user_input in user_input_compare]
        try:
            if user_input_compare != None:
                df = getSentiments(user_input_compare)
                plt.figure(figsize=(10,8))
                mean_df = df.groupby(['ticker', 'date']).mean().unstack()
                mean_df = mean_df.xs('compound', axis="columns")
                mean_df.plot(kind='bar')
                st.pyplot(plt.show())
                
            else:
                st.write("Enter tickers correctly")    
        except Exception as e:
            pass

    if about_me:
        st.sidebar.markdown("**Github Profile:**")
        st.sidebar.markdown("[Abdul Razzaq](https://github.com/Abdul-Razzaq-40)")
        st.sidebar.markdown('<font color="red">Student,from Hyderabad</font>',unsafe_allow_html=True)        
