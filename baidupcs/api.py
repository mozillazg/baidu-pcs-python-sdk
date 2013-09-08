#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
import json
import pdb

import requests

api_template = 'https://pcs.baidu.com/rest/2.0/pcs/{0}'


class BaseClass(object):
    def __init__(self, access_token, api_template=api_template):
        self.access_token = access_token
        self.api_template = api_template

    def _remove_empty_items(self, data):
        for k, v in data.copy().items():
            if v is None:
                data.pop(k)

    def _request(self, uri, method, extra_params=None, data=None,
                 files=None, **kwargs):
        params = {
            'method': method,
            'access_token': self.access_token
        }
        if extra_params:
            params.update(extra_params)
            self._remove_empty_items(params)
        if data or files:
            api = '%s?%s' % (self.api_template.format(uri),
                             urlencode(params))
            if data:
                self._remove_empty_items(data)
                response = requests.post(api, data=data, **kwargs)
            else:
                self._remove_empty_items(files)
                response = requests.post(api, files=files, **kwargs)
        else:
            api = self.api_template.format(uri)
            response = requests.get(api, params=params, **kwargs)
        return response


class PCS(BaseClass):
    """百度个人云存储（PCS）Python SDK.

    所有 api 方法的返回值均为 requests.Response 对象::

      >>> pcs = PCS('access_token')
      >>> response = pcs.info()
      >>> response
      <Response [200]>
      >>> response.ok  # 状态码是否是 200
      True
      >>> response.status_code  # 状态码
      200
      >>> response.content  # 原始内容（二进制，json 字符串）
      '{"quota":6442450944,"used":5138887,"request_id":1216061570}'
      >>>
      >>> response.json()  # 将 json 字符串转换为 python dict
      {u'used': 5138887, u'quota': 6442450944L, u'request_id': 1216061570}
    """

    def __init__(self, access_token, api_template=api_template):
        super(PCS, self).__init__(access_token, api_template)

    def info(self, **kwargs):
        """获取当前用户空间配额信息."""
        return self._request('quota', 'info', **kwargs)

    def upload(self, remote_path, file_content, ondup=None, **kwargs):
        """上传单个文件（<2G）.

        | 百度PCS服务目前支持最大2G的单个文件上传。
        | 如需支持超大文件（>2G）的断点续传，请参考下面的“分片文件上传”方法。

        :param remote_path: 网盘中文件的保存路径（包含文件名）。
                            必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param file_content: 上传文件的内容。
        :param ondup: （可选）

                      * overwrite：表示覆盖同名文件；
                      * newcopy：表示生成文件副本并进行重命名，命名规则为“
                        文件名_日期.后缀”。
        :return: Response 对象
        """

        params = {
            'path': remote_path,
            'ondup': ondup
        }
        files = {'file': file_content}
        return self._request('file', 'upload', extra_params=params,
                             files=files, **kwargs)

    def upload_tmpfile(self, file_content, **kwargs):
        """分片上传—文件分片及上传.

        百度 PCS 服务支持每次直接上传最大2G的单个文件。

        如需支持上传超大文件（>2G），则可以通过组合调用分片文件上传的
        ``upload_tmpfile`` 方法和 ``upload_superfile`` 方法实现：

        1. 首先，将超大文件分割为2G以内的单文件，并调用 ``upload_tmpfile``
           将分片文件依次上传；
        2. 其次，调用 ``upload_superfile`` ，完成分片文件的重组。

        除此之外，如果应用中需要支持断点续传的功能，
        也可以通过分片上传文件并调用 ``upload_superfile`` 接口的方式实现。

        :param file_content: 上传文件的内容
        :return: Response 对象
        """

        params = {
            'type': 'tmpfile'
        }
        files = {'file': file_content}
        return self._request('file', 'upload', extra_params=params,
                             files=files, **kwargs)

    def upload_superfile(self, remote_path, block_list, ondup=None, **kwargs):
        """分片上传—合并分片文件.

        与分片文件上传的 ``upload_tmpfile`` 方法配合使用，
        可实现超大文件（>2G）上传，同时也可用于断点续传的场景。

        :param remote_path: 网盘中文件的保存路径（包含文件名）。
                            必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param block_list: 子文件内容的 MD5 值列表；子文件至少两个，最多1024个。
        :type block_list: list
        :param ondup: （可选）

                      * overwrite：表示覆盖同名文件；
                      * newcopy：表示生成文件副本并进行重命名，命名规则为“
                        文件名_日期.后缀”。
        :return: Response 对象
        """

        params = {
            'path': remote_path,
            'ondup': ondup
        }
        data = {
            'param': json.dumps({'block_list': block_list}),
        }
        return self._request('file', 'createsuperfile', extra_params=params,
                             data=data, **kwargs)

    def download(self, remote_path, **kwargs):
        """下载单个文件。

        download 接口支持HTTP协议标准range定义，通过指定range的取值可以实现
        断点下载功能。 例如：如果在request消息中指定“Range: bytes=0-99”，
        那么响应消息中会返回该文件的前100个字节的内容；
        继续指定“Range: bytes=100-199”，
        那么响应消息中会返回该文件的第二个100字节内容::

          >>> headers = {'Range': 'bytes=0-99'}
          >>> pcs.download('/apps/test_sdk/test.txt', headers=headers)

        :param remote_path: 网盘中文件的路径（包含文件名）。
                            必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :return: Response 对象
        """

        params = {
            'path': remote_path,
        }
        return self._request('file', 'download', extra_params=params, **kwargs)

    def mkdir(self, remote_path, **kwargs):
        """为当前用户创建一个目录.

        :param remote_path: 网盘中目录的路径，必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :return: Response 对象
        """

        data = {
            'path': remote_path
        }
        return self._request('file', 'mkdir', data=data, **kwargs)

    def meta(self, remote_path, **kwargs):
        """获取单个文件或目录的元信息.

        :param remote_path: 网盘中文件/目录的路径，必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :return: Response 对象
        """

        params = {
            'path': remote_path
        }
        return self._request('file', 'meta', extra_params=params, **kwargs)

    def multi_meta(self, path_list, **kwargs):
        """批量获取文件或目录的元信息.

        :param path_list: 网盘中文件/目录的路径列表，路径必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :type path_list: list
        :return: Response 对象
        """

        data = {
            'param': json.dumps({
                'list': [{'path': path} for path in path_list]
            }),
        }
        return self._request('file', 'meta', data=data, **kwargs)

    def list_files(self, remote_path, by=None, order=None,
                   limit=None, **kwargs):
        """获取目录下的文件列表.

        :param remote_path: 网盘中目录的路径，必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param by: 排序字段，缺省根据文件类型排序：

                   * time（修改时间）
                   * name（文件名）
                   * size（大小，注意目录无大小）
        :param order: “asc”或“desc”，缺省采用降序排序。

                      * asc（升序）
                      * desc（降序）
        :param limit: 返回条目控制，参数格式为：n1-n2。

                      返回结果集的[n1, n2)之间的条目，缺省返回所有条目；
                      n1从0开始。
        :return: Response 对象
        """

        params = {
            'path': remote_path,
            'by': by,
            'order': order,
            'limit': limit
        }
        return self._request('file', 'list', extra_params=params, **kwargs)

    def move(self, from_path, to_path, **kwargs):
        """移动单个文件/目录.

        :param from_path: 源文件/目录在网盘中的路径（包括文件名）。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param to_path: 目标文件/目录在网盘中的路径（包括文件名）。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :return: Response 对象
        """

        data = {
            'from': from_path,
            'to': to_path,
        }
        return self._request('file', 'move', data=data, **kwargs)

    def multi_move(self, path_list, **kwargs):
        """批量移动文件/目录。

        :param path_list: 源文件地址和目标文件地址列表:

                           >>> path_list = [
                           ...   ('/apps/test_sdk/test.txt',  # 源文件
                           ...    '/apps/test_sdk/testmkdir/b.txt'  # 目标文件
                           ...    ),
                           ...   ('/apps/test_sdk/test.txt',  # 源文件
                           ...    '/apps/test_sdk/testmkdir/b.txt'  # 目标文件
                           ...   ),
                           ... ]

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :type path_list: list
        :return: Response 对象
        """

        data = {
            'param': json.dumps({
                'list': [{'from': x[0], 'to': x[1]} for x in path_list]
            }),
        }
        return self._request('file', 'move', data=data, **kwargs)

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

    def list_streams(self, file_type, start=0, limit=100,
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

    def download_stream(self, remote_path, **kwargs):
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

    def add_download_task(self, source_url, remote_path,
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

    def query_download_tasks(self, task_ids, operate_type=1,
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

    def list_download_tasks(self, create_time=None, status=None,
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
        return response.json()

    def cancel_download_task(self, task_id, expires=None, **kwargs):
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

    def list_recycle_bin(self, start=0, limit=1000, **kwargs):
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

    def restore_recycle_bin(self, fs_id, **kwargs):
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

    def multi_restore_recycle_bin(self, fs_ids, **kwargs):
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

    def clean_recycle_bin(self, **kwargs):
        """清空回收站。"""
        params = {
            'method': 'delete',
            'access_token': self.access_token,
            'type': 'recycle',
        }
        api = self.api_template.format('file')
        response = requests.get(api, params=params, **kwargs)
        return response.json()
