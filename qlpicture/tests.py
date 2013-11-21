# coding=utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from django.test.client import MULTIPART_CONTENT, BOUNDARY, encode_multipart
import json
from urllib import urlencode

import urllib2
from urllib2 import HTTPError
import base64
import random

# from PIL import Image
# Image.init()


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TestRegisterSessionPictureInformation(TestCase):
    """测试发送Session Picture时,注册以及序号的累加过程"""
    def test_register_session(self):
        url = "/pictures/registerSessionID/"
        # 首次注册
        response = self.client.post(url, {"session_id":1})
        self.assertEqual(response.status_code, 201)
        # 再次注册
        response = self.client.post(url, {"session_id":1})
        self.assertEqual(response.status_code, 200)

        # 拿取最大序号,应该为0,因为还没发送图片
        url = "/pictures/getMaximumIndex/" + "1" +"/"
        response = self.client.get(url)
        self.assertEqual(response.data, 0)

    def test_beforeSending_and_end_session(self):
        # 先进行注册
        url_register = "/pictures/registerSessionID/"
        # 首次注册
        response = self.client.post(url_register, {"session_id":1})        

        url = "/pictures/getStartIndex/"
        url_index = "/pictures/getMaximumIndex/" + "1" +"/"
        image_amount_all = 0
        for i in range(100):
            response = self.client.get(url_index)
            self.assertEqual(response.data, image_amount_all)
            image_amount=random.randint(1,100)
            response = self.client.post(url, {"session_id":1, "image_amount":image_amount})
            self.assertEqual(image_amount_all+1, response.data)
            image_amount_all = image_amount_all + image_amount
            response = self.client.get(url_index)
            self.assertEqual(response.data, image_amount_all)
        # 结束session,删除记录
        url_delete = "/pictures/endSession/" + "1" + "/"
        self.client.delete(url_delete)
        response = self.client.get(url_index)
        self.assertEqual(response.status_code, 404)        
        url_register = "/pictures/registerSessionID/"
        # 首次注册
        response = self.client.post(url_register, {"session_id":1})
        self.assertEqual(response.status_code, 201)
        response = self.client.get(url_index)
        self.assertEqual(response.data, 0)

class TestSendPicture(TestCase):
    """测试用户发送图片的过程"""

    # 无法通过self.client.put进行测试, 因为服务器总是无法读取相应的image文件


    # def test_upload_picture(self):
    #     """测试上传正确的图片,包含PNG和JPG"""
    #     url = "/pictures/"
    #     image_data = open(
    #         "/Users/user/Documents/Workspace/Python/djcode/mysite/"
    #         "resourceForTest/1.png", 
    #         "rb")
    #     response = self.client.put(url, urlencode({
    #         'picture': image_data,
    #         'session_id': 1,
    #         'index': 1
    #     }), content_type = 'application/x-www-form-urlencoded')
    #     print response.data
    #     self.assertEqual(response.status_code, 201)

# content_type = 'application/x-www-form-urlencoded'
        # # 测试上传jpg图像
        # data = open(
        #     "/Users/user/Documents/Workspace/Python/djcode/mysite/"
        #     "resourceForTest/1.jpg", 
        #     "rb")
        # response = self.client.post(url,
        #     json.dumps({
        #     'picture': data.read(),
        #     'session_id': 1,
        #     'index': 1
        # }), content_type='application/json')
        # self.assertEqual(response.status_code, 201)     

        # # 在 urllib2 上注册 http 流处理句柄
        # register_openers()

        # # 开始对文件 "DSC0001.jpg" 的 multiart/form-data 编码
        # # "image1" 是参数的名字，一般通过 HTML 中的 <input> 标签的 name 参数设置

        # # headers 包含必须的 Content-Type 和 Content-Length
        # # datagen 是一个生成器对象，返回编码过后的参数
        # datagen, headers = multipart_encode({"picture": open(
        #     "/Users/user/Documents/Workspace/Python/djcode/mysite/"
        #     "resourceForTest/1.png", 
        #     "rb")
        # })

        # # 创建请求对象
        # request = urllib2.Request(
        #     "http://127.0.0.1:8000/pictures/", datagen, headers)
        # # 实际执行请求并取得返回
        # result = urllib2.urlopen(request)
        # self.assertEqual(result.getcode(), 201)

        # # # 测试上传jpg图像
        # datagen, headers = multipart_encode({"picture": open(
        #     "/Users/user/Documents/Workspace/Python/djcode/mysite/"
        #     "resourceForTest/1.jpg", 
        #     "rb")
        # })
        # request = urllib2.Request(
        #     "http://127.0.0.1:8000/pictures/", datagen, headers)
        # result = urllib2.urlopen(request)
        # self.assertEqual(result.getcode(), 201)

    # def test_upload_not_picture(self):
    #     """上传文本文件,应该返回失败值"""
    #     url = "/pictures/"
    #     data = open(
    #         "/Users/user/Documents/Workspace/Python/djcode/mysite/"
    #         "resourceForTest/test", 
    #         "rb")
    #     response = self.client.put(url,  urlencode({
    #         'picture': data,
    #         'session_id': 1,
    #         'index': 1
    #     }), content_type = 'application/x-www-form-urlencoded')
    #     print response.data
    #     self.assertEqual(response.status_code, 400)     
        # # 在 urllib2 上注册 http 流处理句柄
        # register_openers()

        # # 开始对文件 "DSC0001.jpg" 的 multiart/form-data 编码
        # # "image1" 是参数的名字，一般通过 HTML 中的 <input> 标签的 name 参数设置

        # # headers 包含必须的 Content-Type 和 Content-Length
        # # datagen 是一个生成器对象，返回编码过后的参数
        # datagen, headers = multipart_encode({
        #     "picture": open(
        #     "/Users/user/Documents/Workspace/Python/djcode/mysite/"
        #     "resourceForTest/test", 
        #     "rb")
        #     })

        # # 创建请求对象
        # request = urllib2.Request(
        #     "http://127.0.0.1:8000/pictures/", datagen, headers)
        # # 实际执行请求并取得返回
        # # result = urllib2.urlopen(request)
        # # print result.read()
        # # self.assertEqual(result.getcode(), 400)
        # self.assertRaises(HTTPError, urllib2.urlopen, request)
