#used to prevent data from corruption over transfer
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
from newsapi import NewsApiClient
import pandas as pd

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
   )
   #images = Images(app)
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

   @app.route("/", methods =["GET", "POST"])
   def home():

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
      
      top_companies = ["GOOGL", "INR", "MKL", "AMZN", "BKNG", "NVR", "SEB", "NXGPY", "LDSVF"]
# test
      # TOP Find company with highest volume
      highest_volume_company = yf.Ticker(top_companies[0])

      for x in range(1, 9, 1):
         temp_volume_company = yf.Ticker(top_companies[x])

         # print("compare: ", highest_volume_company.info['volume'], " and " ,temp_volume_company.info['volume'], " and " , x)

         if(highest_volume_company.info['volume'] < temp_volume_company.info['volume']):
            highest_volume_company = temp_volume_company
            top_company = top_companies[x]


      # SECOND Find company with highest market cap CHECK NUMBERS
      highest_market_company = yf.Ticker(top_companies[0])
      for x in range(1, 9, 1):
         temp_market_company = yf.Ticker(top_companies[x])
         if(temp_market_company.info['marketCap'] != None):

            # print("compare: ", highest_volume_company.info['volume'], " and " ,temp_volume_company.info['volume'], " and " , x)
            if(highest_market_company.info['marketCap'] < temp_market_company.info['marketCap']):
               highest_market_company = temp_market_company
               second_company = top_companies[x]

      second_company = top_companies[x]
      third_company = "MKL"

      #TOP MOST VOLUME COMPANY DATA 
      top_company_name = highest_volume_company
      top_company_market_price = top_company_name.info['regularMarketPrice']
      top_company_sector = top_company_name.info['sector']

      #TOP Historical graph try to print
      top_history_data = top_company_name.history(period = "max")
      plt.plot(top_history_data['High'], color = 'Red')
      plt.title(top_company, color = 'Black')
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      top_buf = BytesIO()
      plt.savefig(top_buf, format="png")
      top_data = base64.b64encode(top_buf.getbuffer()).decode("ascii")
      plt.close()

      # SECOND HIGHEST MARKET CAP COMPANY DATA
      second_company_name = highest_market_company
      second_company_market_price = second_company_name.info['regularMarketPrice']
      second_company_sector = second_company_name.info['sector']

      #SECOND Historical graph
      second_history_data = second_company_name.history(period = "max")
      plt.plot(second_history_data['High'])
      plt.title(second_company, color = 'Black')
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      second_buf = BytesIO()
      plt.savefig(second_buf, format="png")
      second_data = base64.b64encode(second_buf.getbuffer()).decode("ascii")
      plt.close()

      #THIRD COMPANY DATA
      third_ticker_symbol = third_company
      third_company_name = yf.Ticker(third_ticker_symbol)
      third_company_market_price = third_company_name.info['regularMarketPrice']
      third_company_sector = third_company_name.info['sector']

      #THIRD Historical graph
      third_history_data = third_company_name.history(period = "max")
      plt.plot(third_history_data['High'], color='Green')
      plt.title(third_company, color = 'Black')
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      third_buf = BytesIO()
      plt.savefig(third_buf, format="png")
      third_data = base64.b64encode(third_buf.getbuffer()).decode("ascii")
      plt.close()

      #SEARCH BAR  
      if request.method == "POST":
         try:
            ticker_symbol = request.form.get("ticker")
            company_name = yf.Ticker(ticker_symbol)

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
            #Historical graph
            history_data = company_name.history(period = "max")
            plt.plot(history_data['High'])
            plt.xlabel('Year')
            plt.ylabel('$ USD')
            buf = BytesIO()
            plt.savefig(buf, format="png")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.close()
            
            return render_template("search_result.html",
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
            redirect(url_for('home'))
            

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
      company_earnings_to_send = company_earnings,
      )
   
   from . import db
   db.init_app(app)
      
   from . import auth
   app.register_blueprint(auth.bp)
      
   return app