from . import *
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Comment
from collections import defaultdict
from datetime import datetime
import json
import matplotlib.pyplot as plot
import numpy as np
import re
import requests

def get_articles_about(search_term):
    url = (f'https://newsapi.org/v2/everything?q={search_term}&apiKey=62d5f7a15c0041f2a8eb980dd9cbbecb')
    response = requests.get(url).json()
    for article in response['articles']:
        article_in_db = SESSION.query(Article).filter_by(url=article['url']).first()
        article_object = article_in_db if article_in_db else Article(
            url=article['url'],
            date=datetime.fromisoformat(article['publishedAt'].replace('Z', '')).date())
        SESSION.add(article_object)
        SESSION.commit()
    return response['articles']

def get_stock_period(ticker: str, period: str):
    url = (f'https://cloud.iexapis.com/stable/stock/{ticker}/batch?types=chart&range=1{period}&token=sk_5e5d4ba8e4684bf89a76014d5f017d35')
    response = requests.get(url).json()
    for stock_day in response['chart']:
        stock_day_in_db = SESSION.query(StockDay).filter_by(
            stock_ticker=ticker,
            date=datetime.fromisoformat(stock_day['date']
            ).date()).first()
        print(stock_day)
        stock_day_object = stock_day_in_db if stock_day_in_db else StockDay(
            stock_ticker=ticker,
            date=datetime.fromisoformat(stock_day['date']),
            change=stock_day['change'] * 100)
        SESSION.add(stock_day_object)
        SESSION.commit()

def read_element(words, element):
    if type(element) in (Comment,):
        pass
    elif not type(element) in (str, NavigableString):
        for content in element.contents:
            read_element(words, content)
    else:
        words += str(element).split()

def read_article(url):
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    words = list()
    for element in soup.findAll('p'):
        read_element(words, element)
    print(words)
    return words

def analyze(article_object, words: list):
    for word in words:
        if not any(character.isdigit() for character in word):
            literal = re.sub(r'[^\w\s]', '', word).lower()
            word_in_db = SESSION.query(Word).filter_by(literal=literal).first()
            word_object = word_in_db if word_in_db else Word(
                literal=literal,
                guid=new_guid())
            SESSION.add(word_object)

            usage_in_db = SESSION.query(Usage).filter_by(
                word_guid=word_object.guid,
                article_guid=article_object.guid).first()
            usage_object = usage_in_db if usage_in_db else Usage(
                word_guid=word_object.guid,
                article_guid=article_object.guid,
                occurences=0)
            usage_object.occurences += 1
            SESSION.add(usage_object)
            SESSION.commit()
    article_object.analyzed = True
    SESSION.commit()

def predict(stock_ticker: str, url: str):
    article_obj = Article(
        url=url
    )
    try:
        SESSION.add(article_obj)
        SESSION.commit()
    except:
        SESSION.rollback()
    words = read_article(url)
    article_impact = 0
    for word in words:
        word_obj = SESSION.query(Word).filter_by(literal=word.lower()).first()
        if word_obj:
            article_impact += word_obj.average_impact_on(stock_ticker)
    return article_impact

def main():
    get_articles_about('tsla')
    get_stock_period('tsla', 'y')
    for article_object in SESSION.query(Article).all():
        if not article_object.analyzed:
            words = read_article(article_object.url)
            analyze(article_object, words)

    words_in_db = SESSION.query(Word).all()
    words = {}
    for word in words_in_db:
        words[word.literal] = word.average_impact_on('tsla')
    with open('output.json', 'w') as f:
        f.write(json.dumps(words, default=str))
    # x = np.arange(len(words_in_db))
    # plot.bar(x, height=[
    #     word.average_impact_on('tsla') for word in words_in_db
    #     ])
    # plot.xticks(x, [word.literal for word in words_in_db], rotation=90)
    # plot.show()

if __name__ == '__main__':
    main()