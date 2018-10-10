from copy import deepcopy

from nose import tools
import json

from demo.model import Article
from tests import test_app, article_data, BaseTest, user_one


class TestArticle(BaseTest):
    @classmethod
    def setup_class(cls):
        cls.user_one = deepcopy(user_one)
        cls.article_data = deepcopy(article_data)
        cls.test_login()
        cls.__test_save_article()

    @classmethod
    def teardown_class(cls):
        cls.clean_user()

    @classmethod
    def __test_save_article(cls):
        article = Article(**cls.article_data)
        article.save()
        cls.article_id = article.id

    def test_get(self):
        """
        测试文章的get接口

        1、测试传错误token或者不传token能否get到文章
        2、测试查询全部文章列表详情
        3、测试查询错误ID
        4、测试查询正确ID
        """
        api_url = 'api/v1/user'
        api_method = test_app.get
        self.test_api_jwt(api_url, api_method)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.article_data)
        response = test_app.get('/api/v1/article',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        article_id = json_resp['data']['list'][0]['id']
        tools.assert_equals(json_resp['data']['count'], 1)

        response = test_app.get(f'/api/v1/article/{article_id} + aaa',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 500)
        tools.assert_equals(json_resp.get('data'),
                            {'msg': "Id is not found."})
        print(self.id)
        response = test_app.get(f'/api/v1/article/{article_id}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp['data'].get('id'))

    def test_post(self):
        """
        测试article的post接口

        1、测试登录认证
        2、测试用户能否正常添加文章
        """
        api_url = 'api/v1/user'
        api_method = test_app.post
        self.test_api_jwt(api_url, api_method)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.article_data)
        t_data['title'] = 'memeda'
        t_data['author'] = 'memeda'

        response = test_app.post('api/v1/article',
                                 data=json.dumps(t_data),
                                 headers=headers,
                                 content_type='application/json')
        json_resp = self.validate_response(response, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))

    def test_put(self):
        """
        测试用户的put接口

        1、测试登录认证
        2、测试修改不存在的article
        3、测试修改权限
        """
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.article_data)

        response = test_app.put(f'/api/v1/article',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        self.validate_response(response, 400)

        response = test_app.put(f'/api/v1/article/{str(self.id) + "111"}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        self.validate_response(response, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Id is not found.'})

        t_data['title'] = 'fweajobnfsd'
        t_data['author'] = '4684waf'
        t_article = Article(**t_data)
        t_article.save()
        headers = {'Authorization': self.token+'111'}
        response = test_app.put(f'api/v1/article/{str(t_article.id)}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 401)
        tools.assert_equals(json_resp['data'],
                            {'msg': 'Signature verification failed'})

        headers = {'Authorization': self.token}
        response = test_app.put(f'api/v1/article/{str(t_article.id)}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        self.clean_user()

    def test_delete(self):
        """
        测试用户的delete接口

        1、是否能成功删除存在的article
        2、当没有token时能否删除
        3、测试能否删除不存在的article
        """
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.article_data)
        t_data['title'] = 'one'
        t_data['author'] = 'two'
        t_article = Article(**t_data)
        t_article.save()
        response = test_app.delete(f'/api/v1/article/{str(t_article.id)}',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        self.validate_response(response, 200)
        response = test_app.delete(f'/api/v1/article/{str(t_article.id)}+11',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        self.validate_response(response, 500)
        headers = {'Authorization': self.token+'111'}
        response = test_app.delete(f'/api/v1/article/{str(t_article.id)}',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        self.validate_response(response, 401)
