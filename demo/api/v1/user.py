from flask import request
from flask_restful import reqparse
from flask_jwt import jwt_required, JWTError

from demo import app, rest_api, jwt
from demo.common import util
from demo.api.base import BaseAPI
from demo.model.user import User
from demo.service.user import rule_required, get_current_user
from demo.service.user import save_new_user, update_user


@rest_api.route('/api/v1/login', endpoint='login')
class LoginAPI(BaseAPI):
    def post(self):
        data = request.get_json()
        username = data.get(app.config.get('JWT_AUTH_USERNAME_KEY'), None)
        password = data.get(app.config.get('JWT_AUTH_PASSWORD_KEY'), None)

        criterion = [username, password, len(data) == 2]
        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')
        identity = jwt.authentication_callback(
            User, username, util.md5(password))
        if identity:
            access_token = jwt.jwt_encode_callback(identity)
            return jwt.auth_response_callback(access_token, identity)
        else:
            raise JWTError('Bad Request', 'Invalid credentials')


@rest_api.route('/api/v1/user', endpoint='user')
@rest_api.route('/api/v1/user/<string:id>', endpoint='user_detail')
class UserAPI(BaseAPI):

    @jwt_required()
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('page_size', type=int, default=20)
            args = parser.parse_args()

            data = util.paging(cls=User,
                               page=args.get('page'),
                               page_size=args.get('page_size'))

            return util.api_response(data=data)

        elif id == 'me':
            return util.api_response(data=self.me().api_response())
        else:
            return util.api_response(data=User.get_by_id(id).api_response())

    def me(self):
        return get_current_user()

    @jwt_required()
    @rule_required()
    def post(self):
        data = request.get_json()
        current_user = get_current_user()
        if User.get_by_username(data['username']):
            raise ValueError('user already exist')
        if not current_user.is_admin:
            return util.api_error_response('Do not have authority')
        return util.api_response(
            data=save_new_user(data, current_user).api_response()
            )

    @jwt_required()
    @rule_required()
    def put(self, id=None):

        if id is None:
            return util.api_error_response('Need user id.', 400)

        user = User.get_by_id(id)
        current_user = get_current_user()
        if user:
            if user.id != current_user.id and not current_user.is_admin:
                return util.api_error_response('Do not have authority')
            return util.api_response(
                update_user(request.get_json(),
                            current_user, user).api_response())

        return util.api_error_response('Id not found', 400)

    @jwt_required()
    @rule_required()
    def delete(self, id=None):
        if id is None:
            return util.api_error_response('Need user id.', 400)

        user = User.get_by_id(id)
        current_user = get_current_user()

        if user:
            if not current_user.is_admin:
                return util.api_error_response('You do not have authority.')
            user.delete()
            return util.api_response('user deleted', 200)
        return util.api_error_response('Id not found', 400)
