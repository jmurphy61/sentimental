import holidays, re
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from uuid import uuid4
from datetime import datetime, timedelta

HOLIDAYS = (
    datetime(2020, 1, 20).date(),
)

DB_ENGINE = create_engine(f"sqlite:///main.db", echo=True)
Session = sessionmaker()
Session.configure(bind=DB_ENGINE)
SESSION = Session()

def new_guid():
    return str(uuid4()).replace('-', '')

class Object(object):
    pass

class Base(Object):
    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    guid = Column(String(32), primary_key=True, default=new_guid)
Base = declarative_base(cls=Base)

class Stock(Base):
    ticker = Column(String, primary_key=True)

class StockReference(Base):
    stock_ticker = Column(String, ForeignKey(Stock.ticker), primary_key=True)
    word_guid = Column(String(32), ForeignKey('word.guid'), primary_key=True)

    stock = relationship('Stock', backref='references')
    word = relationship('Word', backref=backref('related_to', uselist=True))


class StockDay(Base):
    stock_ticker = Column(String, ForeignKey(Stock.ticker), primary_key=True)
    date = Column(Date, nullable=False, primary_key=True)
    change = Column(Integer, nullable=false, default=0)
    # open = Column(Integer, nullable=false)
    # close = Column(Integer, nullable=false)
    # high = Column(Integer, nullable=false)
    # low = Column(Integer, nullable=false)
    # close = Column(Integer, nullable=false)

    stock = relationship(
        Stock,
        backref='history'
    )

class Usage(Base):
    article_guid = Column(String(32), ForeignKey('article.guid'), primary_key=True)
    word_guid = Column(String(32), ForeignKey('word.guid'), primary_key=True)
    occurences = Column(Integer, nullable=False, default=0)

    article = relationship('Article', backref='usages')
    word = relationship('Word', backref='usages')

    def impact_on(self, stock_ticker):
        date = self.article.date
        print(f'the date is {date}')
        print(holidays.UnitedStates())
        while date.weekday() in (5,6)\
            or date in HOLIDAYS:
            date += timedelta(days=1)
        if date >= datetime.today().date():
            return 0
        print(f'date is now{date}')
        stock_day = SESSION.query(StockDay).filter_by(
            stock_ticker=stock_ticker,
            date=date
            ).first()
        return stock_day.change

class Word(Base):
    literal = Column(String, nullable=False, unique=True)

    # @property
    # def usages(self):
    #     return SESSION.query(usage.c.impact).filter(usage.c.word_guid==self.guid).all()
    
    @property
    def total_occurences(self):
        return sum(usage.occurences for usage in self.usages)

    def total_impact_on(self, stock_ticker):
        return sum(usage.impact_on(stock_ticker) for usage in self.usages) / 100
    
    def average_impact_on(self, stock_ticker):
        return self.total_impact_on(stock_ticker) / self.total_occurences / 100

    def __str__(self):
        return f'Word("{self.literal}")'

class Article(Base):
    url = Column(String, nullable=False, unique=True)
    date = Column(Date, nullable=False, default=lambda: datetime.now().date())
    analyzed  = Column(Boolean, nullable=False, default=False)

Base.metadata.create_all(DB_ENGINE)