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
       history_data = company_name.history(period = "max")
       plt.plot(history_data['High'])
       plt.xlabel('Year')
       plt.ylabel('$ USD')
       
       buf = BytesIO()
       plt.savefig(buf, format="png")
       data = base64.b64encode(buf.getbuffer()).decode("ascii")

#FIX search_result.html in /template
#IMPLEMENT template to update graphs and summaries accordingly

       return f"<center <p>Historically</p> <img src='data:image/png;base64,{data}'/> </center>"
    return render_template("index.html")

@app.route("/account/", methods =["GET", "POST"])
def account():
   return render_template('account.html')

@app.route("/company_page/", methods =["GET", "POST"])
def company_page():
   return render_template('company_page.html')

@app.route("/log_in/", methods =["GET", "POST"])
def log_in():
   return render_template('log_in.html')