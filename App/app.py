from flask import request
from datetime import timedelta
import json
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

@app.route('/metro/news/')
def main():
    day = request.args.get('day')
    articles = db.session.query(Article)
    if day:
        date = datetime.today().date() - timedelta(days=int(day))
        articles = articles.filter(Article.date > date)
    else:
        articles = articles.all()
    ans = [{'title': article.title, 'url': article.url, 'date': str(article.date)} for article in articles]
    return json.dumps(ans, ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)