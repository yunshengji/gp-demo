
import datetime

import mongoengine
from demo.model.base import BaseModel


class Article(BaseModel, mongoengine.Document):
    title = mongoengine.StringField(required=True, default='')
    author = mongoengine.StringField(required=True, default='')
    updated = mongoengine.DateTimeField(required=False, default=None)
    added = mongoengine.DateTimeField(required=True,
                                      default=datetime.datetime.now())

    meta = {'indexes': ['title', 'added', 'author', 'updated'],
            'strict': False
            }

    @classmethod
    def get_by_title(cls, title):
        return cls.objects(title=title).first()

    def api_base_response(self):
        return {'id': str(self.id), 'title': self.title,
                'added': str(self.added), 'updated': str(self.updated)}

    def api_response(self):
        if self.updated is None:
            return {
                'id': str(self.id),
                'title': self.title,
                'added': str(self.added),
                'updated': 'no update',
                'author': self.author
            }
        else:
            return {
                'id': str(self.id),
                'title': self.title,
                'added': str(self.added),
                'updated': str(self.updated),
                'author': self.author
            }
