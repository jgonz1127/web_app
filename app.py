import base64
from io import BytesIO
from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
if __name__=='__main__':
   #debug allows errors to show in the webpage for debugging, set to false before production
   app.run(debug=True)
   #key needed to enable csrf protection sand use FlaskForm
   app.config["SECRET_KEY"]="TempKey"
@app.route("/", methods =["GET", "POST"])
def home():

   #WILL COMPARE TOP COMAPNIES POST TOP 3 GRAPHS AND INFO ON HOME
   # alphabet, Madras Rubber Factory Limited, Markel Corporation, Amazon Inc, Booking Holdings Inc.,NVR Inc.
   # Seaboard Corporation, Next Plc, Lindt & Sprüngli AG ,Berkshire Hathaway

    top_companies = {"GOOGL", "MRF", "MKL", "AMZN", "BKNG", "NVR", "SEB", "NXGPY", "LDSVF", "BRK.A"}

    #FIND TOP 3 MARKETPRICE
    # for top_companies


    
   #  #SEARCH BAR  
    if request.method == "POST":
       ticker_symbol = request.form.get("ticker")
       company_name = yf.Ticker(ticker_symbol)

       #Company info
       company_sector = company_name.info['sector']
       market_price = "Market price: ",company_name.info['regularMarketPrice']
       todays_high = "Todays high: ", company_name.info['dayHigh']
       todays_low = "Todays low: ", company_name.info['dayLow']
       company_summary = "Company summary: ", company_name.info['longBusinessSummary']

       #ADD other graphs if necessary
       #Historical graph
       history_data = company_name.history(period = "max")
       plt.plot(history_data['High'])
       plt.xlabel('Year')
       plt.ylabel('$ USD')
       buf = BytesIO()
       plt.savefig(buf, format="png")
       data = base64.b64encode(buf.getbuffer()).decode("ascii")

       return render_template("search_result.html",
        data_to_send = data,
        company_sector_to_send = company_sector,
        market_price_to_send = market_price,
        todays_high_to_send = todays_high,
        todays_low_to_send = todays_low,
        company_summary_to_send = company_summary)
   
    return render_template('index.html')

#CONNECT to db, ADD account information, ADD followed companies
@app.route("/account/", methods =["GET", "POST"])
def account():
   return render_template('account.html')
   
#FIX, will be how search is currently
@app.route("/company_page/", methods =["GET", "POST"])
def company_page():
   return render_template('company_page.html')

#ADD login functionality with db
@app.route("/log_in/", methods =["GET", "POST"])
def log_in():
   return render_template('log_in.html')

#CONNECT with database
@app.route("/sign_up/", methods =["GET", "POST"])
def sign_up():
   return render_template('sign_up.html')

