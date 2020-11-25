from datetime import timedelta
from bs4 import BeautifulSoup
import requests, re, threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////usr/src/db/mosmetro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(128), nullable=True)
    date = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    def __repr__(self):
        return '<Article %r>' % self.id

class Parser:
    months = {'Января': '01',
              'Февраля': '02',
              'Марта': '03',
              'Апреля': '04',
              'Мая': '05',
              'Июня': '06',
              'Июля': '07',
              'Августа': '08',
              'Сентября': '09',
              'Октября': '10',
              'Ноября': '11',
              'Декабря': '12'}

    def get_date(self, id):
        try:
            url = 'https://mosmetro.ru/press/news/' + id
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            date = soup.find('div', class_='pagetitle__content-date').text.split()
            dd = date[0]
            if len(dd) == 1:
                dd = '0' + dd
            mm = self.months[date[1]]
            yyyy = date[2]
            return datetime.strptime(yyyy + mm + dd, '%Y%m%d').date()
        except:
            return None

    def set_article(self, id, title, url, date):

        if db.session.query(Article).filter(Article.id == id).scalar():
            return
        article = Article(id=id, title=title, url=url, date=date)
        try:
            db.session.add(article)
            db.session.commit()
        except:
            db.session.rollback()

    def get_article(self):
        url = 'https://mosmetro.ru/press/news/'
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('div', class_='newslist__list-item')
        for article in articles:
            id = re.search(r'\d+', article.a['href'])[0]
            date = self.get_date(id)
            if not date:
                number = int(article.find('span', class_='newslist__text-time').text.split()[0])
                measure = article.find('span', class_='newslist__text-time').text.split()[1][0]
                if measure == 'д':
                    date = datetime.today().date() - timedelta(days=number)
                elif measure == 'н':
                    date = datetime.today().date() - timedelta(weeks=number)
                elif measure == 'м':
                    date = datetime.today().date() - timedelta(days=number*30)
            try:
                url = article.img['src']
            except:
                url = None
            title = article.find('span', class_="newslist__text-title").text
            self.set_article(id, title, url, date)

if __name__ == '__main__':
    db.create_all()
    def repeat():
        Parser().get_article()
        threading.Timer(600.0, repeat).start()
    repeat()
