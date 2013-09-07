#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
import json
import pdb

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

    def delete(self, remote_path, **kwargs):
        """删除单个文件/目录。"""
        params = {
            'method': 'delete',
            'access_token': self.access_token,
            'path': remote_path
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def multi_delete(self, path_list, **kwargs):
        """批量删除文件/目录。"""
        params = {
            'method': 'delete',
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

    def search(self, remote_path, keyword, recurrent='0', **kwargs):
        """获取目录下的文件列表."""
        params = {
            'method': 'search',
            'access_token': self.access_token,
            'path': remote_path,
            'wd': keyword,
            're': recurrent,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def thumbnail(self, remote_path, height, width, quality=100, **kwargs):
        """获取指定图片文件的缩略图。"""
        params = {
            'method': 'generate',
            'access_token': self.access_token,
            'path': remote_path,
            'height': height,
            'width': width,
            'quality': quality,
        }
        api = self.api_template.format('thumbnail')
        response = requests.get(api, params=params, **kwargs)
        return response.content

    def diff(self, cursor='null', **kwargs):
        """文件增量更新操作查询接口。本接口有数秒延迟，但保证返回结果为最终一致。"""
        params = {
            'method': 'diff',
            'access_token': self.access_token,
            'cursor': cursor,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def video_convert(self, remote_path, video_type, **kwargs):
        """对视频文件进行转码，实现实时观看视频功能。"""
        params = {
            'method': 'streaming',
            'access_token': self.access_token,
            'path': remote_path,
            'type': video_type,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.content

    def stream_list(self, file_type, start=0, limit=100,
                    filter_path='', **kwargs):
        """以视频、音频、图片及文档四种类型的视图获取所创建应用程序下的
        文件列表。"""
        params = {
            'method': 'list',
            'access_token': self.access_token,
            'type': file_type,
            'start': start,
            'limit': limit,
            'filter_path': filter_path,
        }
        api = self.api_template.format('stream')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def stream_download(self, remote_path, **kwargs):
        """为当前用户下载一个流式文件。其参数和返回结果与下载单个文件的相同。
        """
        params = {
            'method': 'download',
            'access_token': self.access_token,
            'path': remote_path,
        }
        api = self.api_template.format('stream')
        response = requests.get(api, params=params, **kwargs)
        return response.content

    def rapid_upload(self, remote_path, content_length, content_md5,
                     content_crc32, slice_md5, ondup='', **kwargs):
        """秒传一个文件。
        被秒传文件必须大于256KB（即 256*1024 B）
        """
        params = {
            'method': 'rapidupload',
            'access_token': self.access_token,
            'path': remote_path,
            'content-length': content_length,
            'content-md5': content_md5,
            'content-crc32': content_crc32,
            'slice-md5': slice_md5,
            'ondup': ondup,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def add_offline_download_task(self, source_url, remote_path,
                                  rate_limit=0, timeout=60 * 60,
                                  expires=0, callback='', **kwargs):
        """添加离线下载任务，实现单个文件离线下载。"""
        params = {
            'method': 'add_task',
            'access_token': self.access_token,
            'source_url': source_url,
        }
        data = {
            'save_path': remote_path,
            'expires': expires,
            'rate_limit': rate_limit,
            'timeout': timeout,
            'callback': callback,
        }
        api = '%s?%s' % (self.api_template.format('services/cloud_dl'),
                         urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def query_offline_download_task(self, task_ids, operate_type=1,
                                    expires=0, **kwargs):
        """根据任务ID号，查询离线下载任务信息及进度信息。"""
        params = {
            'method': 'query_task',
            'access_token': self.access_token,
        }
        data = {
            'task_ids': ','.join(map(str, task_ids)),
            'op_type': operate_type,
            'expires': expires,
        }
        api = '%s?%s' % (self.api_template.format('services/cloud_dl'),
                         urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def list_offline_download_task(self, create_time=None, status=None,
                                   need_task_info=1, start=0, limit=10, asc=0,
                                   source_url=None, remote_path=None,
                                   expires=None, **kwargs):
        """查询离线下载任务ID列表及任务信息。"""
        params = {
            'method': 'list_task',
            'access_token': self.access_token,
            'need_task_info': need_task_info,
        }
        data = {
            'expires': expires,
            'start': start,
            'limit': limit,
            'asc': asc,
            'source_url': source_url,
            'save_path': remote_path,
            'create_time': create_time,
            'status': status,
            'need_task_info': need_task_info,
        }
        for k, v in data.copy().items():
            if v is None:
                data.pop(k)
        api = '%s?%s' % (self.api_template.format('services/cloud_dl'),
                         urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        pdb.set_trace()
        return response.json()

    def cancel_offline_download_task(self, task_id, expires=None, **kwargs):
        """查询离线下载任务ID列表及任务信息。"""
        params = {
            'method': 'cancel_task',
            'access_token': self.access_token,
        }
        data = {
            'expires': expires,
            'task_id': task_id,
        }
        for k, v in data.copy().items():
            if v is None:
                data.pop(k)
        api = '%s?%s' % (self.api_template.format('services/cloud_dl'),
                         urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def recycle_bin_list(self, start=0, limit=1000, **kwargs):
        """获取回收站中的文件及目录列表。"""
        params = {
            'method': 'listrecycle',
            'access_token': self.access_token,
            'start': start,
            'limit': limit,
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()

    def recycle_bin_restore(self, fs_id, **kwargs):
        """还原单个文件或目录（非强一致接口，调用后请sleep 1秒读取）。"""
        params = {
            'method': 'restore',
            'access_token': self.access_token,
        }
        data = {
            'fs_id': fs_id,
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()

    def recycle_bin_multi_restore(self, fs_ids, **kwargs):
        """批量还原文件或目录（非强一致接口，调用后请sleep1秒 ）。"""
        params = {
            'method': 'restore',
            'access_token': self.access_token,
        }
        data = {
            'param': json.dumps({
                'list': [{'fs_id': fs_id} for fs_id in fs_ids]
            }),
        }
        api = '%s?%s' % (self.api_template.format('file'), urlencode(params))
        response = requests.post(api, data=data, **kwargs)
        return response.json()
