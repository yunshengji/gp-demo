

import mongoengine as me
from demo.model.base import BaseModel


class User(BaseModel, me.Document):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    level = me.IntField(required=True, default=1)

    meta = {
        'collection': 'user',
        'indexes': ['username', 'email', 'level']
    }

    @classmethod
    def validate_password(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.password.encode('utf-8') == password.encode('utf-8'):
            return user

    @classmethod
    def get_by_username(cls, username):
        return cls.objects(username=username).first()

    @property
    def is_admin(self):
        return self.level == 9

    def api_base_response(self):
        return {'id': str(self.id), 'username': self.username,
                'email': self.email}

    def me(self):
        return self.api_response()

    def api_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'level': self.level
        }


def authenticate(user, username, password):
    user = User.validate_password(username, password)
    return user if user else None


def identity(payload):
    return User.objects.get(id=payload['identity'])
