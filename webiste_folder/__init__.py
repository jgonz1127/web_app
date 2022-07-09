#used to prevent data from corruption over transfer
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
import yfinance as yf
from flask import Flask, request, render_template

def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)
   # if __name__=='__main__':
   #   app.run()
   app.config.from_mapping(
       SECRET_KEY='dev',
       DATABASE=os.path.join(app.instance_path, 'users.sqlite'),
   )
   if test_config is None:
      app.config.from_pyfile('config.py',silent=True)
   else:
      app.config.from_mapping(test_config)
      
   try:
      os.makedirs(app.instance_path)
   except OSError:
      pass
      
      
   @app.route("/", methods =["GET", "POST"])
   def home():

      #WILL COMPARE TOP COMAPNIES POST TOP 3 GRAPHS AND INFO ON HOME
      # alphabet, Madras Rubber Factory Limited, Markel Corporation, Amazon Inc, Booking Holdings Inc.,NVR Inc.
      # Seaboard Corporation, Next Plc, Lindt & Sprüngli AG ,Berkshire Hathaway
      # top_companies = {"GOOGL", "INR", "MKL", "AMZN", "BKNG", "NVR", "SEB", "NXGPY", "LDSVF", "BRK.A"}

      #TOP 3 COMPANIES hard coded for now WILL CHANGE
      top_company = "GOOGL"
      second_company = "AMZN"
      third_company = "MKL"

      #TOP COMPANY DATA 
      top_ticker_symbol = top_company
      top_company_name = yf.Ticker(top_ticker_symbol)

      top_company_market_price = top_company_name.info['regularMarketPrice']
      top_company_sector = top_company_name.info['sector']

      #TOP Historical graph
      top_history_data = top_company_name.history(period = "max")
      plt.plot(top_history_data['High'])
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      top_buf = BytesIO()
      plt.savefig(top_buf, format="png")
      top_data = base64.b64encode(top_buf.getbuffer()).decode("ascii")
      plt.close()

      #SECOND COMPANY DATA
      second_ticker_symbol = second_company
      second_company_name = yf.Ticker(second_ticker_symbol)

      second_company_market_price = second_company_name.info['regularMarketPrice']
      second_company_sector = second_company_name.info['sector']

      #SECOND Historical graph
      second_history_data = second_company_name.history(period = "max")
      plt.plot(second_history_data['High'])
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
      plt.plot(third_history_data['High'])
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      third_buf = BytesIO()
      plt.savefig(third_buf, format="png")
      third_data = base64.b64encode(third_buf.getbuffer()).decode("ascii")
      plt.close()

      #SEARCH BAR  
      if request.method == "POST":
         ticker_symbol = request.form.get("ticker")
         company_name = yf.Ticker(ticker_symbol)

         #Company info
         company_sector = company_name.info['sector']
         market_price = "Market price: ",company_name.info['regularMarketPrice']
         todays_high = "Todays high: ", company_name.info['dayHigh']
         todays_low = "Todays low: ", company_name.info['dayLow']
         company_summary = "Company summary: ", company_name.info['longBusinessSummary']

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
         data_to_send = data,
         company_sector_to_send = company_sector,
         market_price_to_send = market_price,
         todays_high_to_send = todays_high,
         todays_low_to_send = todays_low,
         company_summary_to_send = company_summary,)

   # FIX HOME PAGE TO LOAD GRAPHS NOT IMAGES, FIX SPACING, FIX LINKS TO OTHER PAGES
      return render_template("index.html",
      top_ticker_symbol_to_send = top_ticker_symbol,
      top_company_sector_to_send = top_company_sector,
      top_company_market_price_to_send = top_company_market_price,
      top_data_to_send = top_data,
      
      second_ticker_symbol_to_send = second_ticker_symbol,
      second_company_sector_to_send = second_company_sector,
      second_company_market_price_to_send = second_company_market_price,
      second_data_to_send = second_data,

      third_ticker_symbol_to_send = third_ticker_symbol,
      third_company_sector_to_send = third_company_sector,
      third_company_market_price_to_send = third_company_market_price,
      third_data_to_send = third_data
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

      #CHECK if it is even possible to graph earnings throughout the years
      #Earnings graph 
      earnings_data = company_earnings
      plt.plot(earnings_data['High'])
      plt.xlabel('Year')
      plt.ylabel('$ USD')
      company_buf = BytesIO()
      plt.savefig(company_buf, format="png")
      company_data = base64.b64encode(company_buf.getbuffer()).decode("ascii")
      plt.close()

      return render_template('company_page.html', 
      company_dividends_to_send = company_dividends,
      company_financials_to_send = company_financials,
      company_major_holders_to_send = company_major_holders,
      company_institutional_holders_to_send = company_institutional_holders,
      company_balance_sheet_to_send = company_balance_sheet,
      company_cashflow_to_send = company_cashflow,
      company_earnings_to_send = company_earnings,
      company_data_to_send = company_data
      )
   
   from . import db
   db.init_app(app)
      
   from . import auth
   app.register_blueprint(auth.bp)
      
   return app