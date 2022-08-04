import sys
from flask import (
    Blueprint, render_template, request, g,  url_for, redirect, session,flash, current_app
)
import random
import asyncio
import pandas as pd
import yfinance as yf
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from newsapi import NewsApiClient
import urllib
from PIL import Image
from flask_caching import Cache
from time import time
# from uuid import RESERVED_FUTURE
import matplotlib.style as mplstyle
# from flask.ext.images import resized_img_src
from sys import stderr
import matplotlib
#from sqlalchemy import true
matplotlib.use('Agg')

bp = Blueprint('route', __name__)

# Graph visuals
plt.style.use('bmh')
mplstyle.use('fast')
# PANDAS DISPLAY
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
 # cache the companies api calls server side to improve speed

def make_cache_config():
    current_app.config.from_mapping(
        CACHE_TYPE="SimpleCache",  # Flask-Caching related configs
        CACHE_DEFAULT_TIMEOUT=300
    )
    #cache for the site only for current session
    global cache 
    cache = Cache(current_app)
@bp.route("/", methods=["GET", "POST"])
def home():
    if "user" in session:
        user = session['user']
        flash('welcome back {}'.format(user))
    
      # WILL COMPARE TOP COMAPNIES POST TOP 3 GRAPHS AND INFO ON HOME, make this into one loop and make them all concurrent task calls as to not do sequentially
      # removed for simplicity, will need ifs and try blocks for none values.
    top_companies = ["TSLA", "GOOGL", "MKL", "AMZN",
                       "BKNG", "NVR", "SEB", "LDSVF"]

      # ENUMERATE through articles and grabs general information
    article_titles = []
    article_authors = []
    article_descriptions = []
    article_images = []
    article_url = []

    async def populate_article_arrays(x):
        """populates article arrays

        Args:
            x (int): index of current article to retrieve data from
        """
        article_titles.append(articles_df['title'][x])
        article_authors.append(articles_df['author'][x])
        article_descriptions.append(articles_df['description'][x])
        article_images.append(articles_df['urlToImage'][x])
        article_url.append(articles_df['url'][x])

    async def make_call(company):
        """retrieves company objects from yfinance

        Args:
            company (str): company searched

        Returns:
            Ticker object: Ticker object from yfinance module
        """
        return yf.Ticker(company)

    def article_api_call():
        """creates all news api variables and makes list of articles
        """
        global newsapi
        newsapi = NewsApiClient(api_key='0dea726db11d4447930182ff2920e22f')
        global top_headlines
        top_headlines = newsapi.get_everything(
        q='stocks', language='en', page_size=3)

    # creates list of articles
        global articles
        articles = top_headlines['articles']

    # MAKING articles into data frame allows for easier manipulation
        global articles_df
        articles_df = pd.DataFrame(articles)
        return True

    async def homepage_graph_calls():
        """makes all necessary api calls

        Returns:
            list: list of company objects from yfinance
        """
        calls_made = article_api_call()
        article_tasks = []
        tasks = []
        returnList = []
        for company in top_companies:
            task = asyncio.create_task(make_call(company))
            tasks.append(task)
        if calls_made:
            for i in range(len(articles)):
                article_tasks.append(
                    asyncio.create_task(populate_article_arrays(i)))
        for task in tasks:
            result = await task
            returnList.append(result)
        for task in article_tasks:
            await task
        return returnList

    @cache.cached(timeout=15000, key_prefix="api_calls_home")
    def calls():
        """creates list of ticker companys from yfinance and article list
        """
        global api_responses
        api_responses = asyncio.run(homepage_graph_calls())

    start = time()
    #@TODO add exception handler
    try:
        calls()
    except:
        print("calls failed", file=sys.stderror)
        flash("api calls failed!")
    print('calls made! making comparisons')

    @cache.cached(timeout=15000, key_prefix="chosen_companys")
    def work():
        NUM_HOME_GRAPHS = 3
        temp_list = []
        index_list = []
        # choose a random company
        for i in range(NUM_HOME_GRAPHS):
            while True:
                index = random.randrange(0, len(top_companies))
                if index in index_list:
                    continue
                index_list.append(index)
                temp_list.append(api_responses[index])
                break
        return tuple(temp_list)
    tuple_holder = work()
    print('companys ')
    print(time()-start)
    comp_1 = tuple_holder[0]
    comp_2 = tuple_holder[1]
    comp_3 = tuple_holder[2]

    print(time()-start)

    def make_new_graph(history_time, company_obj, title, xlabel="year", ylabel="$USD"):
        """generates graph

        Args:
            history_time (str): timeframe to retrieve data from
            company_obj (ticker_object): company object from yfinance
            title (str): title of graph
            xlabel (str, optional):x label. Defaults to "year".
            ylabel (str, optional): y label. Defaults to "$USD".

        Returns:
            str: ascii encoding of pyplot
        """
        plt.figure()
        # company = numpy.array(company_obj.history(period=history_time)["High"])
        ax = plt.axes()
        plt.plot(company_obj.history(period=history_time)
                ["High"],color='#845ec2', label='Yearly_line')
        ax.set_facecolor('#4b4453')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        data = base64.b64encode(buffer.getbuffer()).decode("ascii")
        plt.clf()
        return data

    @cache.cached(timeout=15000, key_prefix="chosen_company_graphs")
    def graphs():
        """handles caching and construction of graphs

        Returns:
            List: returns a list of graphs which are encoded as ascii
        """
        graphs = []
        task1 = make_new_graph("1y", comp_1, comp_1.info['longName'])
        task2 = make_new_graph("1y", comp_2, comp_2.info['longName'])
        task3 = make_new_graph("1y",  comp_3, comp_3.info['longName'])

        graphs.append(task1)
        graphs.append(task2)
        graphs.append(task3)

        return graphs

    print('making graphs')
    #@TODO add exception handler
    try:
        graph_list = graphs()
        plt.close('all')
        print(time()-start)
        top_data = graph_list[0]
        second_data = graph_list[1]
        third_data = graph_list[2]
        print(time()-start)
    except: 
        flash("failed to make graphs!")
        print("graphs failed to load", file=sys.stderror)
    

    #@TODO handle invalid calls and sanitize inputs
    if request.method == "POST":
        #add to session to find in other route (/search/)
        session['request_ticker'] = request.form.get("ticker")
        return redirect(url_for('route.search'))
    #@TODO add exception handler 
    try:
        return render_template('index.html',
        top_data_to_send=top_data,
        second_data_to_send=second_data,
        third_data_to_send=third_data,
        # ARTICLES
        article_titles_to_send=article_titles,
        article_authors_to_send=article_authors,
        article_descriptions_to_send=article_descriptions,
        article_images_to_send=article_images,
        article_url_to_send=article_url
        )
    except:
        flash("failed to render tamplate")
        return render_template('404.html')
        

@bp.route("/search/", methods=["GET", "POST"])
def search():
    def make_new_graph(history_time, company_obj, title, xlabel="year", ylabel="$USD"):
        plt.figure()
        # company = numpy.array(company_obj.history(period=history_time)["High"])
        ax = plt.axes()
        plt.plot(company_obj.history(period=history_time)
                ["High"], color='#845ec2', label='Yearly_line')
        ax.set_facecolor('#4b4453')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        data = base64.b64encode(buffer.getbuffer()).decode("ascii")
        plt.clf()
        return data
    #@TODO handle invalid calls and sanitize inputs
    def main(searched_ticker):
        """Renders the template for searches

        Args:
            searched_ticker (str): symbol used in search
        """
        def render_company_image(url):
            """creates image based on url and saves/overwrites same png file (webImage.png)

            Args:
                url (str): company url
            """
            urllib.request.urlretrieve(
                url, "webiste_folder/static/webImage.png")
            img = Image.open("webiste_folder/static/webImage.png")
        #remove from dict if new search used
        session.pop('request_ticker', None)
        try:
            ticker_symbol = searched_ticker
           # request.form.get("ticker")
            company_name = yf.Ticker(ticker_symbol)
            
            #render the image
            render_company_image(company_name.info['logo_url'])
            print("image made")

            data = make_new_graph("max", company_name, "Historical Data",)
            data2 = make_new_graph(
                "1y", company_name, "52 Week Data", "Months")
            data3 = make_new_graph("1wk", company_name, "1 Week Data", "days")
            plt.close("all")
            
            holders_to_send=company_name.major_holders
            iholders_to_send=company_name.institutional_holders
            sustainability_to_send = company_name.sustainability
            recommendations_to_send = company_name.recommendations.tail(10)
            calendar_to_send = company_name.calendar
            
            return render_template("search_result.html",
            h_table=[holders_to_send.to_html(classes='data')], h_titles=holders_to_send.columns.values,
            ih_table = [iholders_to_send.to_html(classes='data')], ih_titles= iholders_to_send.columns.values,
            sustainability_table=[sustainability_to_send.to_html(classes='data')], sus_titles=sustainability_to_send.columns.values,
            recommendation_table=[recommendations_to_send.to_html(classes='data')], recomm_titles=recommendations_to_send.columns.values,
            calendar_table=[calendar_to_send.to_html(classes='data')], calendar_titles=calendar_to_send.columns.values,
            isin_to_send=company_name.isin,
            company_name_to_send=company_name.info['longName'],
            volume_to_send=company_name.info['volume'],
            market_cap_to_send=company_name.info['marketCap'],
            dividend_rate_to_send=company_name.info['dividendRate'],
            supply_to_send=company_name.info['circulatingSupply'],
            fifty2_high_to_send=company_name.info['fiftyTwoWeekHigh'],
            fifty2_low_to_send=company_name.info['fiftyTwoWeekLow'],
            fifty2_change_to_send=company_name.info['52WeekChange'],
            yield_to_send=company_name.info['yield'],
            company_sector_to_send=company_name.info['sector'],
            logo_to_send=company_name.info['logo_url'],
            market_price_to_send=company_name.info['regularMarketPrice'],
            todays_high_to_send=company_name.info['dayHigh'],
            todays_low_to_send=company_name.info['dayLow'],
            company_summary_to_send=company_name.info['longBusinessSummary'],
            data_to_send=data,
            graph2=data2,
            graph3=data3)
        except:
            url = "https://finance.yahoo.com/lookup"
            if "user" in session:
                user = session['user']
                flash("sorry {}, we couldnt find {}! Try searching with the companys correct 'tickers' symbol. EX: 'aapl'\n. Use {} for reference".format(
                    user, searched_ticker,url))
            else:
                flash("sorry, we couldnt find {}! Try searching with the companys correct 'tickers' symbol. EX: 'aapl'\n. Use {} for reference".format(searched_ticker, url))
            # find something to do here, maybe js?
            return render_template('404.html')
    # SEARCH BAR
    if request.method == "POST":
       return main(request.form.get("ticker"))
        
    #need to clear session value after used
    temp_request = session.get('request_ticker',None)
    return  main(temp_request)
        
@bp.route("/account/", methods =["GET", "POST"])
def account():
    try:
        return render_template('account.html')
    except:
        flash("error occured")
        return render_template('404.html')