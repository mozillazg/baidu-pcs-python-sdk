#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
import json

import requests

api_template = 'https://pcs.baidu.com/rest/2.0/pcs/{0}'


class PCS(object):
    def __init__(self, access_token, api_template=api_template):
        self.access_token = access_token
        self.api_template = api_template

    def info(self, **kwargs):
        """获取当前用户空间配额信息. """
        api = self.api_template.format('quota')
        params = {
            'method': 'info',
            'access_token': self.access_token
        }
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def upload(self, remote_path, file_content, ondup='', **kwargs):
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
        response = requests.post(api, files=files, **kwargs)
        return response.json()

    def upload_tmpfile(self, file_content, **kwargs):
        """.  """
        params = {
            'method': 'upload',
            'access_token': self.access_token,
            'type': 'tmpfile',
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        files = {'file': file_content}
        response = requests.post(api, files=files, **kwargs)
        return response.json()

    def upload_superfile(self, remote_path, block_list, ondup='', **kwargs):
        """. """
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
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def download(self, remote_path, **kwargs):
        """下载单个文件."""
        params = {
            'method': 'download',
            'access_token': self.access_token,
            'path': remote_path,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.content

    def mkdir(self, remote_path, **kwargs):
        """创建目录。"""
        params = {
            'method': 'mkdir',
            'access_token': self.access_token,
            'path': remote_path
        }
        api = self.api_template.format('file')
        response = requests.post(api, params=params, **kwargs)
        return response.json()

    def meta(self, remote_path, **kwargs):
        """获取单个文件或目录的元信息。"""
        params = {
            'method': 'meta',
            'access_token': self.access_token,
            'path': remote_path
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def multi_meta(self, path_list, **kwargs):
        """批量获取文件或目录的元信息。"""
        params = {
            'method': 'meta',
            'access_token': self.access_token,
        }
        data = {
            'param': json.dumps({
                'list': [{'path': path} for path in path_list]
            }),
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def file_list(self, remote_path, by='', order='', limit='', **kwargs):
        """获取目录下的文件列表."""
        params = {
            'method': 'list',
            'access_token': self.access_token,
            'path': remote_path,
            'by': by,
            'order': order,
            'limit': limit,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def move(self, from_path, to_path, **kwargs):
        """移动单个文件/目录。"""
        params = {
            'method': 'move',
            'access_token': self.access_token,
        }
        data = {
            'from': from_path,
            'to': to_path,
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def multi_move(self, path_list, **kwargs):
        """批量移动文件/目录。"""
        params = {
            'method': 'move',
            'access_token': self.access_token,
        }
        data = {
            'param': json.dumps({'list': path_list}),
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def copy(self, from_path, to_path, **kwargs):
        """拷贝文件(目录)。"""
        params = {
            'method': 'copy',
            'access_token': self.access_token,
        }
        data = {
            'from': from_path,
            'to': to_path,
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def multi_copy(self, path_list, **kwargs):
        """拷贝文件(目录)。"""
        params = {
            'method': 'copy',
            'access_token': self.access_token,
        }
        data = {
            'param': json.dumps({'list': path_list}),
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()
