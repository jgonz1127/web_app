import base64
from io import BytesIO
from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
if __name__=='__main__':
   app.run()

@app.route("/", methods =["GET", "POST"])
def home():

    if request.method == "POST":
       ticker_symbol = request.form.get("ticker")
       company_name = yf.Ticker(ticker_symbol)

       #Company info
       company_sector = company_name.info['sector']
       market_price = "Market price: ",company_name.info['regularMarketPrice']
       todays_high = "Todays high: ", company_name.info['dayHigh']
       todays_low = "Todays low: ", company_name.info['dayLow']
       company_summary = "Company summary: ", company_name.info['longBusinessSummary']

       company = {company_sector, market_price, todays_high, todays_low, company_summary}

       #GRAPH's buffer/information
       #ADD other graphs if necessary
       #Historical graph
       history_data = company_name.history(period = "max")
       plt.plot(history_data['High'])
       plt.xlabel('Year')
       plt.ylabel('$ USD')
       buf = BytesIO()
       plt.savefig(buf, format="png")
       data = base64.b64encode(buf.getbuffer()).decode("ascii")

#FIX company list is sent in a different order each time

       return render_template("search_result.html", data_to_send = data, company_to_send = company)
    return render_template("index.html")

#ADD account information, ADD followed companies
@app.route("/account/", methods =["GET", "POST"])
def account():
   return render_template('account.html')
   
@app.route("/company_page/", methods =["GET", "POST"])
def company_page():
   return render_template('company_page.html')

#ADD login functionality with db, ADD signup button
@app.route("/log_in/", methods =["GET", "POST"])
def log_in():
   return render_template('log_in.html')

#CREATE sign up information, CONNECT with database
@app.route("/sign_up/", methods =["GET", "POST"])
def sign_up():
   return render_template('sign_up.html')