from functools import wraps
from flask import _request_ctx_stack
from demo.common import util
from demo.model.user import User


def save_new_user(data, current_user):
    if current_user.level == 9:
        data['username'] = data['username'].strip()
        data['password'] = util.md5(data['password'].strip())
        data['email'] = data['email'].strip()
        user = User(**data).save()
        return user
    raise Exception("user don't have authority")


def update_user(data, current_user, user):
    if data.get('password', None):
        user.password = util.md5(data['password'].strip())
    if current_user.level == 9:
        user.level = data.get('level', user.level)
    user.email = data.get('email', user.email).strip()
    if current_user == user:
        user.email = data.get('email', user.email).strip()
    return user.save()


def delete_user(current_user):
    current_user.delete()
    return util.api_error_response('This user is deleted')


def rule_required(level=None):

    if level is None:
        level = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if user.level not in level:
                raise Exception("user don't has authority")
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():

    return _request_ctx_stack.top.current_identity
