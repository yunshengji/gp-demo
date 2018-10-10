from copy import deepcopy

from nose import tools
import json

from demo.model import User
from tests import test_app, user_one, BaseTest


class TestUser(BaseTest):
    @classmethod
    def setup_class(cls):
        cls.test_data = deepcopy(user_one)
        cls.test_login()
        cls.__test_save_user

    @classmethod
    def __test_save_user(cls):
        user = User(**cls.test_data)
        user.save()
        cls.user_id = user.id

    @tools.nottest
    def test_paging(self, response, page, page_size=20):
        """
        翻页功能测试

        @param page: 页数
        @type page: int
        @param page_size: 每页条数
        @type page_size: int
        @return: None
        @rtype: None
        """
        json_resp = self.validate_response(response, 200)
        user = User.objects()
        print(user)
        length = len(user)
        list_len = page_size

        tools.assert_equals(json_resp['data']['page_sum'], length//20+1)
        if page == json_resp['data']['page_sum']:
            list_len = length % page_size
            if list_len == 0:
                list_len = 20

        tools.assert_equals(len(json_resp['data']['list']), list_len)

        tools.assert_equals(json_resp['data']['count'], length)
        tools.assert_equals(json_resp['data']['current_page'], page)

    def test_me(self):
        """
        测试current user是否正确并且不显示用户信息密码
        """
        headers = {'Authorization': self.token}
        response = test_app.get('/api/v1/user/me', headers=headers)
        json_resp = self.validate_response(response, 200)

        user_data = json_resp.get('data')
        user = User.get_by_id(self.id)
        tools.assert_equals(user_data, user.api_response())
        tools.assert_is_none(user_data.get('password'))

    def test_get(self):
        """
        测试用户的get接口

        1、测试传错误token或者不传token能否get到用户
        2、测试登录认证
        3、测试翻页功能
        4、测试查询全部用户列表详情
        5、测试查询错误ID
        6、测试查询正确ID
        """
        api_url = 'api/v1/user'
        api_method = test_app.get
        self.test_api_jwt(api_url, api_method)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)

        response = test_app.get('/api/v1/user',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        self.test_paging(response, 1)
        tools.assert_equals(json_resp['data']['count'], 1)

        for i in range(25):
            user = User(**t_data)
            user.username = user.username + str(i)
            user.password = user.password + str(i)
            user.email = user.email + str(i)
            user.save()

        response = test_app.get('/api/v1/user?page=2',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        self.test_paging(response, 2)
        tools.assert_equals(json_resp['data']['count'], 26)

        response = test_app.get(f'/api/v1/user/{self.id} + aaa',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 500)
        tools.assert_equals(json_resp.get('data'),
                            {'msg': "Id is not found."})

        response = test_app.get(f'/api/v1/user/{self.id}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp['data'].get('id'))

    def test_post(self):
        """
        测试用户的post接口

        1、测试登录认证
        2、测试普通用户无法新增用户
        3、测试admin level9能否正常新增用户
        """
        api_url = 'api/v1/user'
        api_method = test_app.post
        self.test_api_jwt(api_url, api_method)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)
        t_data['username'] = 'someone'
        t_data['email'] = 'someone@gmail.com'
        t_data['password'] = 'test1'
        self.change_user_level(1)
        response = test_app.post('api/v1/user',
                                 data=json.dumps(t_data),
                                 headers=headers,
                                 content_type='application/json')
        json_resp = self.validate_response(response, 500)
        tools.assert_equals(json_resp,
                            {'msg': "Do not have authority"})

        self.change_user_level(9)
        response = test_app.post('api/v1/user',
                                 data=json.dumps(t_data),
                                 headers=headers,
                                 content_type='application/json')
        json_resp = self.validate_response(response, 200)
        tools.assert_is_not_none(json_resp.get('data'))
        tools.assert_is_not_none(json_resp.get('data').get('id'))

    def test_put(self):
        """
        测试用户的put接口

        1、测试修改不存在的用户
        2、测试修改权限
        """
        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)

        response = test_app.put(f'/api/v1/user',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        self.validate_response(response, 400)

        response = test_app.put(f'/api/v1/user/{str(self.id) + "111"}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        self.validate_response(response, 500)
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Id is not found.'})

        t_data['username'] = 'fweajobnfsd'
        t_data['password'] = '4684waf'
        t_data['email'] = 'skr123@geekpark.net'
        t_user = User(**t_data)
        t_user.save()

        self.change_user_level(1)
        response = test_app.put(f'api/v1/user/{str(t_user.id)}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 500)
        tools.assert_equals(json_resp,
                            {'msg': "Do not have authority"})

        self.change_user_level(9)
        response = test_app.put(f'api/v1/user/{str(t_user.id)}',
                                data=json.dumps(t_data),
                                headers=headers,
                                content_type='application/json')
        json_resp = self.validate_response(response, 200)
        self.clean_user()

    def test_delete(self):
        """
        测试用户的delete接口

        1、测试登录认证
        2、测试删除不存在的用户
        3. 测试普通用户删除用户
        4. 测试admin level 9 删除用户
        """
        api_url = 'api/v1/user'
        api_method = test_app.get
        self.test_api_jwt(api_url, api_method)

        headers = {'Authorization': self.token}
        t_data = deepcopy(self.test_data)

        response = test_app.delete(f'/api/v1/user/{str(self.id) + "111"}',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        tools.assert_equals(json.loads(response.data)['data'],
                            {'msg': 'Id is not found.'})
        self.validate_response(response, 500)

        response = test_app.delete(f'/api/v1/user',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        self.validate_response(response, 400)

        t_data['username'] = 'fweajobn'
        t_data['password'] = '4684waf'
        t_data['email'] = 'skr3@geekpark.net'
        t_user = User(**t_data)
        t_user.save()

        self.change_user_level(1)
        response = test_app.delete(f'api/v1/user/{str(t_user.id)}',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        json_resp = self.validate_response(response, 500)
        tools.assert_equals(json_resp,
                            {'msg': "You do not have authority."})

        self.change_user_level(9)
        response = test_app.delete(f'api/v1/user/{str(t_user.id)}',
                                   data=json.dumps(t_data),
                                   headers=headers,
                                   content_type='application/json')
        self.validate_response(response, 200)
