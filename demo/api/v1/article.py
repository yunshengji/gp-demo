from flask import request
from flask_restful import reqparse
from flask_jwt import jwt_required

from demo import rest_api
from demo.common import util
from demo.api.base import BaseAPI
from demo.model.article import Article
from demo.service.article import update_article


@rest_api.route('/api/v1/article', endpoint='article')
@rest_api.route('/api/v1/article/<string:id>', endpoint='article_detail')
class ArticleAPI(BaseAPI):

    @jwt_required()
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('page_size', type=int, default=20)
            args = parser.parse_args()

            data = util.paging(cls=Article,
                               page=args.get('page'),
                               page_size=args.get('page_size'))

            return util.api_response(data=data)
        else:
            return util.api_response(data=Article.get_by_id(id).api_response())

    @jwt_required()
    def post(self):
        data = request.get_json()
        if Article.get_by_title(data['title']):
            raise ValueError('article already exist')
        article = Article(**data).save()
        return util.api_response(data=article.api_response())

    @jwt_required()
    def put(self, id=None):
        if id is None:
            return util.api_error_response('Need article id.', 400)

        article = Article.get_by_id(id)
        if article:
            return util.api_response(update_article(request.get_json(),
                                     article).api_response())

        return util.api_error_response('Id not found', 400)

    @jwt_required()
    def delete(self, id=None):
        if id is None:
            return util.api_error_response('Need user id.', 400)

        article = Article.get_by_id(id)

        if article:
            article.delete()
            return util.api_response('article deleted', 200)
        return util.api_error_response('Id not found', 400)
