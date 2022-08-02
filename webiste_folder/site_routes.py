from flask import (
    Blueprint, render_template, request, g,  url_for, redirect, session, current_app
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
    calls()
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
    graph_list = graphs()
    plt.close('all')
    print(time()-start)
    top_data = graph_list[0]
    second_data = graph_list[1]
    third_data = graph_list[2]
    print(time()-start)

    #@TODO handle invalid calls and sanitize inputs
    if request.method == "POST":
        #add to session to find in other route (/search/)
        session['request_ticker'] = request.form.get("ticker")
        return redirect(url_for('route.search'))

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

            urllib.request.urlretrieve(
                url, "webiste_folder/static/webImage.png")
            img = Image.open("webiste_folder/static/webImage.png")

        try:
            ticker_symbol = searched_ticker
           # request.form.get("ticker")
            company_name = yf.Ticker(ticker_symbol)
            
            # Company info
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
            
            #render the image
            render_company_image(company_name.info['logo_url'])
            print("image made")

            data = make_new_graph("max", company_name, "Historical Data",)
            data2 = make_new_graph(
                "1y", company_name, "52 Week Data", "Months")
            data3 = make_new_graph("1wk", company_name, "1 Week Data", "days")
            plt.close("all")

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
            graph2=data2,
            graph3=data3,
            logo_to_send=company_logo,
            company_name_to_send=company_long_name,
            company_sector_to_send=company_sector,
            market_price_to_send=market_price,
            todays_high_to_send=todays_high,
            todays_low_to_send=todays_low,
            company_summary_to_send=company_summary)
        except:
            # find something to do here, maybe js?
            redirect(url_for("route.home"))
    # SEARCH BAR
    if request.method == "POST":
       return main(request.form.get("ticker"))
        
    #need to clear session value after used
    temp_request = session.get('request_ticker',None)
    return  main(temp_request)
        
@bp.route("/account/", methods =["GET", "POST"])
def account():
    return render_template('account.html')