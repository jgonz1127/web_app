#used to prevent data from corruption over transfer
from newsapi import NewsApiClient
import urllib
import flask_monitoringdashboard as dashboard
import requests
from PIL import Image
from flask_caching import Cache
from time import sleep, time
# from uuid import RESERVED_FUTURE
from flask_debugtoolbar import DebugToolbarExtension
from datetime import timedelta
from datetime import date
import matplotlib.style as mplstyle
from flask import Flask, request, render_template, redirect, url_for
# from flask.ext.images import resized_img_src
from sys import stderr
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
import yfinance as yf
from flask import Flask, request, render_template
import matplotlib.style as mplstyle
from datetime import date
from datetime import timedelta
import pandas as pd
import asyncio

# API KEY
newsapi = NewsApiClient(api_key='0dea726db11d4447930182ff2920e22f')

# PANDAS DISPLAY
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)
   # if __name__=='__main__':
   #   app.run()
   app.config.from_mapping(
       SECRET_KEY='dev',
       DATABASE=os.path.join(app.instance_path, 'users.sqlite'),
       DEBUG_TB_PROFILER_ENABLED = True,
       CACHE_TYPE= "SimpleCache",  # Flask-Caching related configs
       CACHE_DEFAULT_TIMEOUT= 300
   )
   #cache for the site 
   cache = Cache(app)
   #debug tool
   toolbar = DebugToolbarExtension(app)
   dashboard.bind(app)

    
   if test_config is None:
      app.config.from_pyfile('config.py',silent=True)
   else:
      app.config.from_mapping(test_config)
      
   try:
      os.makedirs(app.instance_path)
   except OSError:
      pass
   
   # Graph visuals
   plt.style.use('bmh')
   mplstyle.use('fast')

   #cache the companies api calls server side to improve speed 
   @app.route("/", methods =["GET", "POST"])
   def home():
      #WILL COMPARE TOP COMAPNIES POST TOP 3 GRAPHS AND INFO ON HOME, make this into one loop and make them all concurrent task calls as to not do sequentially 
      #removed for simplicity, will need ifs and try blocks for none values.
      top_companies = ["TSLA","GOOGL", "MKL", "AMZN",
                       "BKNG", "NVR", "SEB", "NXGPY", "LDSVF"]
      #Find company with highest volume
      async def make_call (company):
         return yf.Ticker(company)
         
      async def homepage_graph_calls():
         # async with aiohttp.ClientSession() as session:
         # tasks= create_list()
         tasks=[]
         returnList =[]
         for company in top_companies:
            task = asyncio.create_task(make_call(company))
            tasks.append(task)
         for task in tasks:
            result = await task
            returnList.append(result)
         return returnList
   
      start = time()
      api_responses= asyncio.run(homepage_graph_calls())
      print(time()-start)
      # for response in api_responses:   
      #    string = "name: {} mc: {} volume {}".format(response.info['longName'],response.info['marketCap'],response.info['volume'])
      #    print(string)
      @cache.cached(timeout=15000, key_prefix="company_calls")
      def work():
         highest_volume_company = api_responses[0]
         highest_marketCap_company = api_responses[0]
         for response in api_responses:   
            if(highest_volume_company.info['volume'] < response.info['volume']):
               highest_volume_company = response
               top_company = response
               
            if(highest_marketCap_company.info['marketCap'] < response.info['marketCap']):
               highest_marketCap_company = response
         return (top_company, highest_marketCap_company, highest_volume_company)
      print(time()-start)
      tuple_holder = work()
      top_company = tuple_holder[0]
      highest_volume_company = tuple_holder[2]
      highest_marketCap_company = tuple_holder[1]
      third_company = "MKL"

      # WILL GRAB IMAGE AND ARTICLE SUMMARY OF 3 ARTICLES AND DISPLAY PREVIEW WITH LINKS TO FULL ARTICLES
      # TOP "STOCK" NEWS
      top_headlines = newsapi.get_everything(q='stocks', language='en', page_size=3)

      # Returns list of articles
      articles = top_headlines['articles']

      #TOP COMPANY DATA 
      top_ticker_symbol = top_company
      top_company_name = yf.Ticker(top_ticker_symbol)
      
      

      # MAKING articles into data frame allows for easier manipulation
      articles_df = pd.DataFrame(articles)
      
      # print(articles_df)

      # ENUMERATE through articles and grabs general information
      article_titles = []
      article_authors = []
      article_descriptions = []
      article_images = []
      article_url = []
      for x in range(0, 3 , 1):
         article_titles.append(articles_df['title'][x])
         article_authors.append(articles_df['author'][x])
         article_descriptions.append(articles_df['description'][x])
         article_images.append(articles_df['urlToImage'][x])
         article_url.append(articles_df['url'][x])
      
     
      top_company_name = highest_volume_company
      top_company_market_price = top_company_name.info['regularMarketPrice']
      top_company_sector = top_company_name.info['sector']


      #TOP Historical graph
      top_history_data = top_company_name.history(period="max")
      @cache.cached(timeout=15000, key_prefix="graph1")
      def graph1():
         plt.plot(top_history_data['High'], color='Red')
         plt.title(top_company, color='Black')
         plt.xlabel('Year')
         plt.ylabel('$ USD')
         top_buf = BytesIO()
         plt.savefig(top_buf, format="png")
         top_data = base64.b64encode(top_buf.getbuffer()).decode("ascii")
         plt.close()
         return top_data
      top_data= graph1()
      
      #HIGHEST MARKET CAP COMPANY DATA
      second_company_name = highest_marketCap_company

      second_company_market_price = second_company_name.info['regularMarketPrice']
      second_company_sector = second_company_name.info['sector']

      #SECOND Historical graph
      second_history_data = second_company_name.history(period="max")
      @cache.cached(timeout=15000, key_prefix="graph2")
      def graph2():
         plt.plot(second_history_data['High'])
         plt.title(second_company_name, color='Black')
         plt.xlabel('Year')
         plt.ylabel('$ USD')
         second_buf = BytesIO()
         plt.savefig(second_buf, format="png")
         second_data = base64.b64encode(second_buf.getbuffer()).decode("ascii")
         plt.close()
         return second_data
      second_data = graph2()

      #THIRD COMPANY DATA
      third_ticker_symbol = third_company
      third_company_name = yf.Ticker(third_ticker_symbol)
      third_company_market_price = third_company_name.info['regularMarketPrice']
      third_company_sector = third_company_name.info['sector']

      #THIRD Historical graph
      third_history_data = third_company_name.history(period="max")
      @cache.cached(timeout=15000, key_prefix="graph3")
      def graph3():
         plt.plot(third_history_data['High'], color='Green')
         plt.title(third_company, color='Black')
         plt.xlabel('Year')
         plt.ylabel('$ USD')
         third_buf = BytesIO()
         plt.savefig(third_buf, format="png")
         third_data = base64.b64encode(third_buf.getbuffer()).decode("ascii")
         plt.close()
         return third_data
      third_data = graph3()
      
      print(time()-start)

      #SEARCH BAR  
      #home will not redirect to search unless search bar is reused on search page
      if request.method == "POST":
         def render_company_image(url):
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            return img
         try:
            ticker_symbol = request.form.get("ticker")
            company_name = yf.Ticker(ticker_symbol)
            print("found company")

            #Company info
            major_holders = company_name.major_holders
            institutional_holders = company_name.institutional_holders
            sustainability = company_name.sustainability
            recommendations=company_name.recommendations.tail(5)
            company_calendar= company_name.calendar
            company_isin =company_name.isin
            company_long_name = company_name.info['longName']
            company_volume = company_name.info['volume']
            company_market_cap = company_name.info['marketCap']
            company_dividend_rate = company_name.info['dividendRate']
            company_circulating_supply = company_name.info['circulatingSupply']
            company_52week_high = company_name.info['fiftyTwoWeekHigh']
            company_52week_low = company_name.info['fiftyTwoWeekLow']
            company_52week_change = company_name.info['52WeekChange']
            company_yield = company_name.info['yield']
            company_sector = company_name.info['sector']
            company_logo = company_name.info['logo_url']
            market_price = company_name.info['regularMarketPrice']
            todays_high =  company_name.info['dayHigh']
            todays_low = company_name.info['dayLow']
            company_summary = company_name.info['longBusinessSummary']
            company_image = render_company_image(company_name.info['logo_url'])
            #Historical graph
            history_data = company_name.history(period="max")
            plt.plot(history_data['High'])
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf = BytesIO()
            plt.savefig(buf, format="png")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.close()
            
            history_data = company_name.history(period="1y") 
            plt.plot(['High'])
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf2 = BytesIO()
            plt.savefig(buf2, format="png")
            data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")
            plt.close()
            print(history_data)
            
            history_data = company_name.history(period="1d")           
            plt.plot(history_data['High'])
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf3 = BytesIO()
            plt.savefig(buf3, format="png")
            data3 = base64.b64encode(buf3.getbuffer()).decode("ascii")
            plt.close()
            print(history_data)

            # print("before change")
            # #STOCK CHANGE - Change is the difference between the current price and the last trade of the previous day
            # today = date.today()
            # yesterday = today - timedelta(days=1)
            # print("before history")
            # yesterday_close = company_name.history(interval='1d', start=yesterday, end=today)
            # current_price = company_name.info['regularMarketPrice']
            # print("before og price")
            # original_price = yesterday_close['close'][0] 
            # print("before change calc")
            # change = (((original_price - current_price) / original_price) * 100) * 100
            # change = change * -1
            return render_template("search_result.html",
            company_image_to_send =company_image,
            yield_to_send=company_yield,
            holders_to_send= major_holders,
            iholders_to_send=institutional_holders,
            sustainability_to_send=sustainability,
            recommendations_to_send=recommendations,
            calendar_to_send=company_calendar,
            isin_to_send=company_isin,
            volume_to_send= company_volume,
            market_cap_to_send =company_market_cap,
            dividend_rate_to_send= company_dividend_rate,
            supply_to_send =company_circulating_supply,
            fifty2_high_to_send=company_52week_high,
            fifty2_low_to_send=company_52week_low,
            fifty2_change_to_send=company_52week_change,
            data_to_send = data,
            graph2=data2,
            graph3=data3,
            logo_to_send= company_logo,
            company_name_to_send=company_long_name,
            company_sector_to_send = company_sector,
            market_price_to_send = market_price,
            todays_high_to_send = todays_high,
            todays_low_to_send = todays_low,
            company_summary_to_send = company_summary)
         except:
            #find something to do here, maybe js?
            print("Company could not be found",stderr)
            redirect(url_for('auth.login'))
            
      print(time()-start)

      return render_template ('index.html',
      top_ticker_symbol_to_send = top_company_name,
      top_company_sector_to_send = top_company_sector,
      top_company_market_price_to_send = top_company_market_price,
      top_data_to_send = top_data,

      second_ticker_symbol_to_send = second_company_name,
      second_company_sector_to_send = second_company_sector,
      second_company_market_price_to_send = second_company_market_price,
      second_data_to_send = second_data,

      third_ticker_symbol_to_send = third_ticker_symbol,
      third_company_sector_to_send = third_company_sector,
      third_company_market_price_to_send = third_company_market_price,
      third_data_to_send = third_data,

      # ARTICLES
      article_titles_to_send = article_titles,
      article_authors_to_send = article_authors,
      article_descriptions_to_send = article_descriptions,
      article_images_to_send = article_images,
      article_url_to_send = article_url
      )

   @app.route("/search/", methods =["GET", "POST"])
   def search():
      #SEARCH BAR
      if request.method == "POST":
         def render_company_image(url):
            urllib.request.urlretrieve(url, "webiste_folder/static/webImage.png")
            img = Image.open("webiste_folder/static/webImage.png")
         try:
            ticker_symbol = request.form.get("ticker")
            company_name = yf.Ticker(ticker_symbol)
            print("found company")

            #Company info
            major_holders = company_name.major_holders
            institutional_holders = company_name.institutional_holders
            sustainability = company_name.sustainability
            recommendations = company_name.recommendations.tail(5)
            company_calendar = company_name.calendar
            company_isin = company_name.isin
            company_long_name = company_name.info['longName']
            company_volume = company_name.info['volume']
            company_market_cap = company_name.info['marketCap']
            company_dividend_rate = company_name.info['dividendRate']
            company_circulating_supply = company_name.info['circulatingSupply']
            company_52week_high = company_name.info['fiftyTwoWeekHigh']
            company_52week_low = company_name.info['fiftyTwoWeekLow']
            company_52week_change = company_name.info['52WeekChange']
            company_yield = company_name.info['yield']
            company_sector = company_name.info['sector']
            company_logo = company_name.info['logo_url']
            market_price = company_name.info['regularMarketPrice']
            todays_high = company_name.info['dayHigh']
            todays_low = company_name.info['dayLow']
            company_summary = company_name.info['longBusinessSummary']
            render_company_image(company_name.info['logo_url'])
            print("image made")

            graph_font = {'family': 'Dosis', 'weight':'bold'}
            #Historical graph
            history_data = company_name.history(period="max")
            plt.plot(history_data['High'])
            plt.title("Hisotrical Data", fontdict = graph_font)
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf = BytesIO()
            plt.savefig(buf, format="png")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.close()

            year_data = company_name.history(period="1y")
            plt.plot(year_data['High'])
            plt.title("52 Week Data", fontdict=graph_font)
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf2 = BytesIO()
            plt.savefig(buf2, format="png")
            data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")
            plt.close()
            print(year_data)

            last_week_data = company_name.history(period="1wk")
            plt.plot(last_week_data['High'])
            plt.title("1 Week Data", fontdict = graph_font)
            plt.xlabel("Last Week")
            plt.ylabel('$ USD')
            buf3 = BytesIO()
            plt.savefig(buf3, format="png")
            data3 = base64.b64encode(buf3.getbuffer()).decode("ascii")
            plt.close()
            print(last_week_data)


            # print("before change")
            # #STOCK CHANGE - Change is the difference between the current price and the last trade of the previous day
            # today = date.today()
            # yesterday = today - timedelta(days=1)
            # print("before history")
            # yesterday_close = company_name.history(interval='1d', start=yesterday, end=today)
            # current_price = company_name.info['regularMarketPrice']
            # print("before og price")
            # original_price = yesterday_close['close'][0]
            # print("before change calc")
            # change = (((original_price - current_price) / original_price) * 100) * 100
            # change = change * -1
            print("calling template")
            return render_template("search_result.html",
            yield_to_send=company_yield,
            holders_to_send=major_holders,
            iholders_to_send=institutional_holders,
            sustainability_to_send=sustainability,
            recommendations_to_send=recommendations,
            calendar_to_send=company_calendar,
            isin_to_send=company_isin,
            volume_to_send=company_volume,
            market_cap_to_send=company_market_cap,
            dividend_rate_to_send=company_dividend_rate,
            supply_to_send=company_circulating_supply,
            fifty2_high_to_send=company_52week_high,
            fifty2_low_to_send=company_52week_low,
            fifty2_change_to_send=company_52week_change,
            data_to_send=data,
            graph2 =data2,
            graph3= data3,
            logo_to_send=company_logo,
            company_name_to_send=company_long_name,
            company_sector_to_send=company_sector,
            market_price_to_send=market_price,
            todays_high_to_send=todays_high,
            todays_low_to_send=todays_low,
            company_summary_to_send=company_summary)
         except:
            #find something to do here, maybe js?
            print("Company could not be found", stderr)
            render_template("auth.login")
   #CONNECT to db, ADD account information, ADD followed companies
   @app.route("/account/", methods =["GET", "POST"])
   def account():
      return render_template('account.html')
      
   #GET company_ticker from search_result.html
   @app.route("/company_page/", methods =["GET", "POST"])
   def company_page():

      ticker_from_html = "GOOGL"
      company_ticker = yf.Ticker(ticker_from_html)
      company_dividends = company_ticker.dividends
      company_financials = company_ticker.financials
      company_major_holders = company_ticker.major_holders
      company_institutional_holders = company_ticker.institutional_holders
      company_balance_sheet = company_ticker.balance_sheet
      company_cashflow = company_ticker.cashflow
      company_earnings = company_ticker.earnings

      return render_template('company_page.html', 
      company_dividends_to_send = company_dividends,
      company_financials_to_send = company_financials,
      company_major_holders_to_send = company_major_holders,
      company_institutional_holders_to_send = company_institutional_holders,
      company_balance_sheet_to_send = company_balance_sheet,
      company_cashflow_to_send = company_cashflow,
      company_earnings_to_send = company_earnings
      )
   
   from . import db
   db.init_app(app)
      
   from . import auth
   app.register_blueprint(auth.bp)
      
   return app