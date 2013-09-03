#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
import os
import pdb
import json

import requests

api_template = 'https://pcs.baidu.com/rest/2.0/pcs/{0}'

class PCS(object):
    def __init__(self, access_token, api_template=api_template):
        self.access_token = access_token
        self.api_template = api_template

    def info(self):
        """获取当前用户空间配额信息."""
        api = self.api_template.format('quota')
        params = {
            'method': 'info',
            'access_token': self.access_token
        }
        response = requests.get(api, params=params)
        return response.json()

    def upload(self, remote_path, file_content, ondup=''):
        """上传单个文件（<2G）.
        remote_path 必须以 /apps/ 开头
        """
        params = {
            'method': 'upload',
            'access_token': self.access_token,
            'path': remote_path,
            'ondup': ondup
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        files = {'file': file_content}
        response = requests.post(api, files=files)
        return response.json()

    def upload_tmpfile(self, file_content):
        """."""
        params = {
            'method': 'upload',
            'access_token': self.access_token,
            'type': 'tmpfile',
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        files = {'file': file_content}
        response = requests.post(api, files=files)
        return response.json()

    def upload_superfile(self, remote_path, block_list, ondup=''):
        """."""
        # pdb.set_trace()
        params = {
            'method': 'createsuperfile',
            'access_token': self.access_token,
            'path': remote_path,
            'ondup': ondup
        }
        data = {
                'param': json.dumps({'block_list': block_list}),
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data)
        return response.json()

if __name__ == '__main__':
    # access_token = '3.3f56524f9e796191ce5baa84239feb15.2592000.1380728222.'
    # access_token += '570579779-1274287'
    # pcs = PCS(access_token)
    # f1_md5 = pcs.upload_tmpfile('abc')['md5']
    # f2_md5 = pcs.upload_tmpfile('def')['md5']
    # result = pcs.upload_superfile('/apps/test_sdk/super.txt', [f1_md5, f2_md5])
    # pdb.set_trace()
    pass
