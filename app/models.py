from app import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from collections import defaultdict
import requests

class Search:
    def __init__(self):
        self.url = "https://api.twitter.com/1.1/search/tweets.json?count=100&"
        self.auth = "AAAAAAAAAAAAAAAAAAAAAFb8HQEAAAAAKAQEoCqQmt7ppR2lxgiwnPeVYPQ%3DzL0nkOnNVUFx7kzLM39PXOqNXbS2M0yXs2NMYyawrtt08crDyd"
        self.geocode = "13.8700,100.9925,1200km"

    def query(self, query, local=False):
        headers = {"authorization": "Bearer " + self.auth}
        url = self.url + f"q={query}"
        if local:
            url += "&geocode=" + self.geocode
        return requests.get(url, headers=headers).json()

    def query_metadata(self, query):
        local = self.query(query, local=True)
        all = self.query(query)
        # print(f"Local: {len(local['statuses'])}, Global: {len(all['statuses'])}\n")
        return all['statuses'], local['statuses']


    def print(self, resp):
        tweets = resp['statuses']
        print(f"\n\n".join([x["text"] for x in tweets]))


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    url = db.Column(db.String, unique=True)
    content = db.Column(JSONB)
    publish_date = db.Column(db.DateTime)
    created_timestamp = db.Column(db.DateTime)
    news_metadata = db.Column(JSONB)

    """
        metadata = {
            'tags':
            'twitter_all':
            'twitter_local':
        }
    """
    def __init__(self):
        self.news_metadata = defaultdict(lambda x: None)

    def populate_from_mc(self, data):
        self.publish_date = data['publish_date']
        self.title = data['title']
        self.url = data['url']

        self.news_metadata['tags'] = data['tags']

    def get_twitter_metadata(self):
        s = Search()
        all, local = s.query_metadata("Thailand " + self.title)
        self.news_metadata["twitter_all"] = all
        self.news_metadata["twitter_local"] = local
        print(f"Retrieved Twitter metadata (Local: {len(local)}, Global: {len(all)})")
        return all, local

    def serialize(self, fields=None):
        fields = [c.name for c in self.__table__.columns] if fields is None else fields
        return {attr: getattr(self, attr) for attr in fields}