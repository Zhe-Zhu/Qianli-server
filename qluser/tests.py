# coding=utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from qluser.models import QLUser
from rest_framework.renderers import JSONRenderer

class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class CheckWhoIsActive(TestCase):
    """
    测试返回已激活用户给Client端的功能
    """
    def setUp(self):
        QLUser.objects.create(
            udid='test1', name='test1', phone_number='18664565400',
            email='cainholic@gmail.com', os_type='i', avatar='testAvatar.jpg')

    def test_check_who_is_active(self):
        """
        测试能否返回正确的激活用户
        """
        url = "/users/whoisactive/"
        # 最后必须要加"/"否则就会重定向网页导致测试不成功
        data = ["willNotReturn", "18664565400", "alsoWillNotReturn", "18664565401", 18664565400]
        data_json = JSONRenderer().render(data)
        response = self.client.post(url, content_type='application/json', data=data_json)
        for phone_number in data:
            if phone_number in ["18664565400", 18664565400]:
                self.assertContains(response, phone_number)
            else:
                self.assertFalse(phone_number in response.content)

class RegisterNewUserTestCase(TestCase):
    """测试新建用户的功能"""
    def setUp(self):
        pass

    # 只测试bad input,因为通过API无法在test_database上进行测试
    # 通过client就可以在test_database上进行测试
    def test_register_new_user(self):
        url = "/users/register/"
        data = {'udid': 'create1', 'name': 'create1', 'phone_number':'186645654399', 'email': 'create1@gmail.com', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_bad_os_type_input_to_register(self):
        """无效的系统类型输入"""
        url = "/users/register/"
        # 不输入os_type
        data_no_os_type = {'udid': 'create1', 'name': 'create1', 
        'phone_number':'186645654399', 'email': 'create1@gmail.com', 
        'os_type': '', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_no_os_type)
        self.assertContains(response, "os_type", status_code=400)

        # 输入错误的os_type
        data_error_os_type = {'udid': 'create1', 'name': 'create1', 
        'phone_number':'186645654399', 'email': 'create1@gmail.com', 
        'os_type': 'x', 'avatar': 'create1Avatar.jpg', 
        'password': 'password'}
        response = self.client.post(url, data_error_os_type)
        self.assertContains(response, "os_type", status_code=400)

        # 还是输入错误的os_type
        data_error_os_type_another = {'udid': 'create1', 'name': 'create1', 
        'phone_number':'186645654399', 'email': 'create1@gmail.com', 
        'os_type': '123', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_error_os_type_another)
        self.assertContains(response, "os_type", status_code=400)

    def test_bad_udid_input_to_register(self):
        """无效udid输入"""
        url = "/users/register/"
        data_error_udid = {'udid': '', 'name': 'create1', 'phone_number':'186645654399', 'email': 'create1@gmail.com', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_error_udid)
        self.assertContains(response, "udid", status_code=400)

    def test_bad_email_input_to_register(self):
        """测试无效邮件地址或空地址输入"""
        url = "/users/register/"
        data_error_email = {'udid': 'create1', 'name': 'create1', 'phone_number':'186645654399', 'email': 'create1gmail.com', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_error_email)
        self.assertContains(response, "email", status_code=400)
        data_error_email_another = {'udid': 'create1', 'name': 'create1', 'phone_number':'186645654399', 'email': 'create1', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_error_email_another)
        self.assertContains(response, "email", status_code=400)

    def test_bad_account_log_imformation_to_register(self):
        """测试无效的账户登录信息输入,电话号码或邮箱必须输入一个,否则无法令用户登录"""
        url = "/users/register/"
        data_empty_phone_email = {'udid': 'create1', 'name': 'create1', 'phone_number':'', 'email': '', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password'}
        response = self.client.post(url, data_empty_phone_email)
        self.assertContains(response, "phone", status_code=400)

    # 经测试, django rest framework会自动忽略is_staff的值
    # def test_bad_admin_and_active_input(self):
    #     """试图尝试更改is_admin和is_active的值"""
    #     data = urllib.urlencode({'udid': 'create1', 'name': 'create1', 'phone_number':'123', 'email': '', 'os_type': 'i', 'avatar': 'create1Avatar.jpg', 'password': 'password', 'is_staff': True})
    #     create = urllib.urlopen("http://127.0.0.1:8000/users/register/", data)
    #     self.assertEqual(create.getcode(), 400)

class QLUserTestCase(TestCase):
    """测试将用户数据存储入数据库并读取"""

    def setUp(self):
        QLUser.objects.create_user(
            udid='test1', name='test1', phone_number='18664565400',
            email='cainholic@gmail.com', os_type='i', avatar='testAvatar.jpg')
        QLUser.objects.create_user(
            udid='test2', name='test2', phone_number='18664565401',
            email='cainholic@gmail.com', os_type='i', avatar='testAvatar.jpg')

    # 返回的是数据库异常,无法测试,应该在更上面一层来做判断
    # def test_duplicate_udid(self):
    #     """出现两个相同udid时是否会出现异常"""
    #     args = ('test1', 'test1', '18664565400',
    #             'cainholic@gmail.com', 'i', 'testAvatar.jpg')
    #     kwds = ('udid', 'name', 'phone_number', 'email', 'os_type', 'avatar')
    #     self.assertRaises(
    #         ValueError, QLUser.objects.create_user, args, kwds)

    def test_name_none(self):
        """如果name为none"""
        self.assertRaises(
            ValueError, QLUser.objects.create_user, 'test3', '', 'i', 'testAvatar.jpg', '18664565400', 'cainholic@gmail.com')

    def test_os_type(self):
        self.assertRaises(
            ValueError, QLUser.objects.create_user, 'test4', 'test4', '', 'testAvatar.jpg', '18664565400', 'cainholic@gmail.com')
        self.assertRaises(
            ValueError, QLUser.objects.create_user, 'test4', 'test4', 'x', 'testAvatar.jpg', '18664565400', 'cainholic@gmail.com')

    def test_email_and_phone(self):
        # email和phone都为空
        self.assertRaises(
            ValueError, QLUser.objects.create_user, 'test4', 'test4', '', 'testAvatar.jpg', '', '')

    def test_fetch_users(self):
        # 测试正常读取用户信息
        user = QLUser.objects.get(udid='test1')
        self.assertEqual(user.name, 'test1')
        self.assertEqual(user.phone_number, '18664565400')

    def test_fetch_users_by_phone_number(self):
        # 测试根据手机号码来获取用户
        user_exist = QLUser.objects.filter(phone_number='18664565400')
        self.assertTrue(user_exist)
        self.assertEqual(user_exist.count(), 1)
        self.assertTrue(user_exist[0].udid == 'test1')
        user_not_exist = QLUser.objects.filter(phone_number='1866456540')
        self.assertTrue(not user_not_exist)

    def test_fetch_users_by_email(self):
        # 测试根据邮箱来获取用户
        user_set = QLUser.objects.filter(email='cainholic@gmail.com')
        self.assertEqual(user_set.count(), 2)
        self.assertTrue(user_set[0].udid in ('test1', 'test2'))
        self.assertTrue(user_set[1].udid in ('test1', 'test2'))
