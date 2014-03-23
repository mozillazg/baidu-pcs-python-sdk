#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


def get_new_access_token(refresh_token, client_id, client_secret,
                         scope=None, **kwargs):
    """使用 Refresh Token 刷新以获得新的 Access Token.

    :param refresh_token: 用于刷新 Access Token 用的 Refresh Token；
    :param client_id: 应用的 API Key；
    :param client_secret: 应用的 Secret Key;
    :param scope: 以空格分隔的权限列表，若不传递此参数，代表请求的数据访问
                  操作权限与上次获取 Access Token 时一致。通过 Refresh Token
                  刷新 Access Token 时所要求的 scope 权限范围必须小于等于上次
                  获取 Access Token 时授予的权限范围。 关于权限的具体信息请参考
                  “ `权限列表`__ ”。
    :return: Response 对象

    关于 ``response.json()`` 字典的内容所代表的含义，
    请参考 `相关的百度帮助文档`__ 。

     __ http://developer.baidu.com/wiki/index.php?title=docs/oauth/baiduoauth/list
     __ http://developer.baidu.com/wiki/index.php?title=docs/oauth/refresh
    """
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    if scope:
        data['scope'] = scope
    url = 'https://openapi.baidu.com/oauth/2.0/token'
    return requests.post(url, data=data)
