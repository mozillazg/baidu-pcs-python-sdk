#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import json
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import requests
from requests_toolbelt import MultipartEncoder

API_TEMPLATE = 'https://pcs.baidu.com/rest/2.0/pcs/{0}'


class InvalidToken(Exception):
    """异常：Access Token 不正确或者已经过期."""
    pass


def check_token(func):
    """检查 access token 是否有效."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code == 401:
            raise InvalidToken('Access token invalid or no longer valid')
        else:
            return response
    return wrapper


class BaseClass(object):
    def __init__(self, access_token, api_template=API_TEMPLATE):
        self.access_token = access_token
        self.api_template = api_template

    def _remove_empty_items(self, data):
        for k, v in data.copy().items():
            if v is None:
                data.pop(k)

    @check_token
    def _request(self, uri, method, url=None, extra_params=None,
                 data=None, files=None, **kwargs):
        params = {
            'method': method,
            'access_token': self.access_token
        }
        if extra_params:
            params.update(extra_params)
            self._remove_empty_items(params)

        if not url:
            url = self.api_template.format(uri)
        api = url

        if data or files:
            api = '%s?%s' % (url, urlencode(params))
            if data:
                self._remove_empty_items(data)
            else:
                self._remove_empty_items(files)
                data = MultipartEncoder(files)
                if kwargs.get('headers'):
                    kwargs['headers']['Content-Type'] = data.content_type
                else:
                    kwargs['headers'] = {'Content-Type': data.content_type}
            response = requests.post(api, data=data, **kwargs)
        else:
            response = requests.get(api, params=params, **kwargs)
        return response


class PCS(BaseClass):
    """百度个人云存储（PCS）Python SDK.

    所有 api 方法的返回值均为 ``requests.Response`` 对象::

      >>> pcs = PCS('access_token')
      >>> response = pcs.info()
      >>> response
      <Response [200]>
      >>> response.ok  # 状态码是否是 200
      True
      >>> response.status_code  # 状态码
      200
      >>> response.content  # 原始内容（二进制/json 字符串）
      '{"quota":6442450944,"used":5138887,"request_id":1216061570}'
      >>>
      >>> response.json()  # 将 json 字符串转换为 python dict
      {u'used': 5138887, u'quota': 6442450944L, u'request_id': 1216061570}
    """
    def info(self, **kwargs):
        """获取当前用户空间配额信息.

        :return: Response 对象
        """

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
        :param file_content: 上传文件的内容/文件对象 。
                             (e.g. ``open('foobar', 'rb')`` )
        :param ondup: （可选）

                      * 'overwrite'：表示覆盖同名文件；
                      * 'newcopy'：表示生成文件副本并进行重命名，命名规则为“
                        文件名_日期.后缀”。
        :return: Response 对象
        """

        params = {
            'path': remote_path,
            'ondup': ondup
        }
        files = {'file': ('file', file_content, '')}
        url = 'https://c.pcs.baidu.com/rest/2.0/pcs/file'
        return self._request('file', 'upload', url=url, extra_params=params,
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

        :param file_content: 上传文件的内容/文件对象
                             (e.g. ``open('foobar', 'rb')`` )
        :return: Response 对象
        """

        params = {
            'type': 'tmpfile'
        }
        files = {'file': ('file', file_content, '')}
        url = 'https://c.pcs.baidu.com/rest/2.0/pcs/file'
        return self._request('file', 'upload', url=url, extra_params=params,
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

                      * 'overwrite'：表示覆盖同名文件；
                      * 'newcopy'：表示生成文件副本并进行重命名，命名规则为“
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
          >>> pcs = PCS('token')
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
        url = 'https://d.pcs.baidu.com/rest/2.0/pcs/file'
        return self._request('file', 'download', url=url,
                             extra_params=params, **kwargs)

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
        """移动单个文件或目录.

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
        """批量移动文件或目录.

        :param path_list: 源文件地址和目标文件地址对列表:

                          >>> path_list = [
                          ...   ('/apps/test_sdk/test.txt',  # 源文件
                          ...    '/apps/test_sdk/testmkdir/b.txt'  # 目标文件
                          ...   ),
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
        """拷贝文件或目录.

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

        .. warning::
           ``move`` 操作后，源文件被移动至目标地址；
           ``copy`` 操作则会保留原文件。
        """

        data = {
            'from': from_path,
            'to': to_path,
        }
        return self._request('file', 'copy', data=data, **kwargs)

    def multi_copy(self, path_list, **kwargs):
        """批量拷贝文件或目录.

        :param path_list: 源文件地址和目标文件地址对的列表:

                          >>> path_list = [
                          ...   ('/apps/test_sdk/test.txt',  # 源文件
                          ...    '/apps/test_sdk/testmkdir/b.txt'  # 目标文件
                          ...   ),
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
        return self._request('file', 'copy', data=data, **kwargs)

    def delete(self, remote_path, **kwargs):
        """删除单个文件或目录.

        .. warning::
           * 文件/目录删除后默认临时存放在回收站内，删除文件或目录的临时存放
             不占用用户的空间配额；
           * 存放有效期为10天，10天内可还原回原路径下，10天后则永久删除。

        :param remote_path: 网盘中文件/目录的路径，路径必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :type remote_path: str
        :return: Response 对象
        """

        data = {
            'path': remote_path
        }
        return self._request('file', 'delete', data=data, **kwargs)

    def multi_delete(self, path_list, **kwargs):
        """批量删除文件或目录.

        .. warning::
           * 文件/目录删除后默认临时存放在回收站内，删除文件或目录的临时存放
             不占用用户的空间配额；
           * 存放有效期为10天，10天内可还原回原路径下，10天后则永久删除。

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
        return self._request('file', 'delete', data=data, **kwargs)

    def search(self, remote_path, keyword, recurrent='0', **kwargs):
        """按文件名搜索文件（不支持查找目录）.

        :param remote_path: 需要检索的目录路径，路径必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :type remote_path: str
        :param keyword: 关键词
        :type keyword: str
        :param recurrent: 是否递归。

                          * "0"表示不递归
                          * "1"表示递归
        :type recurrent: str
        :return: Response 对象
        """

        params = {
            'path': remote_path,
            'wd': keyword,
            're': recurrent,
        }
        return self._request('file', 'search', extra_params=params, **kwargs)

    def thumbnail(self, remote_path, height, width, quality=100, **kwargs):
        """获取指定图片文件的缩略图.

        :param remote_path: 源图片的路径，路径必须以 /apps/ 开头。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param height: 指定缩略图的高度，取值范围为(0,1600]。
        :type height: int
        :param width: 指定缩略图的宽度，取值范围为(0,1600]。
        :type width: int
        :param quality: 缩略图的质量，默认为100，取值范围(0,100]。
        :type quality: int
        :return: Response 对象

        .. warning::
           有以下限制条件：

           * 原图大小(0, 10M]；
           * 原图类型: jpg、jpeg、bmp、gif、png；
           * 目标图类型:和原图的类型有关；例如：原图是gif图片，
             则缩略后也为gif图片。
        """

        params = {
            'path': remote_path,
            'height': height,
            'width': width,
            'quality': quality,
        }
        return self._request('thumbnail', 'generate', extra_params=params,
                             **kwargs)

    def diff(self, cursor='null', **kwargs):
        """文件增量更新操作查询接口.
        本接口有数秒延迟，但保证返回结果为最终一致.

        :param cursor: 用于标记更新断点。

                       * 首次调用cursor=null；
                       * 非首次调用，使用最后一次调用diff接口的返回结果
                         中的cursor。
        :type cursor: str
        :return: Response 对象
        """

        params = {
            'cursor': cursor,
        }
        return self._request('file', 'diff', extra_params=params, **kwargs)

    def video_convert(self, remote_path, video_type, **kwargs):
        """对视频文件进行转码，实现实时观看视频功能.
        可下载支持 HLS/M3U8 的 `媒体云播放器 SDK <HLSSDK_>`__ 配合使用.

        .. _HLSSDK:
           http://developer.baidu.com/wiki/index.php?title=docs/cplat/media/sdk

        :param remote_path: 需要下载的视频文件路径，以/开头的绝对路径，
                            需含源文件的文件名。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :type remote_path: str
        :param video_type: 目前支持以下格式：
                           M3U8_320_240、M3U8_480_224、M3U8_480_360、
                           M3U8_640_480和M3U8_854_480
        :type video_type: str
        :return: Response 对象

        .. warning::
           目前这个接口支持的源文件格式如下：

           +--------------------------+------------+--------------------------+
           |格式名称                  |扩展名      |备注                      |
           +==========================+============+==========================+
           |Apple HTTP Live Streaming |m3u8/m3u    |iOS支持的视频格式         |
           +--------------------------+------------+--------------------------+
           |ASF                       |asf         |视频格式                  |
           +--------------------------+------------+--------------------------+
           |AVI                       |avi         |视频格式                  |
           +--------------------------+------------+--------------------------+
           |Flash Video (FLV)         |flv         |Macromedia Flash视频格式  |
           +--------------------------+------------+--------------------------+
           |GIF Animation             |gif         |视频格式                  |
           +--------------------------+------------+--------------------------+
           |Matroska                  |mkv         |Matroska/WebM视频格式     |
           +--------------------------+------------+--------------------------+
           |MOV/QuickTime/MP4         |mov/mp4/m4a/|支持3GP、3GP2、PSP、iPod  |
           |                          |3gp/3g2/mj2 |之类视频格式              |
           +--------------------------+------------+--------------------------+
           |MPEG-PS (program stream)  |mpeg        |也就是VOB文件/SVCD/DVD格式|
           +--------------------------+------------+--------------------------+
           |MPEG-TS (transport stream)|ts          | 即DVB传输流              |
           +--------------------------+------------+--------------------------+
           |RealMedia                 |rm/rmvb     | Real视频格式             |
           +--------------------------+------------+--------------------------+
           |WebM                      |webm        | Html视频格式             |
           +--------------------------+------------+--------------------------+
        """

        params = {
            'path': remote_path,
            'type': video_type,
        }
        return self._request('file', 'streaming', extra_params=params,
                             **kwargs)

    def list_streams(self, file_type, start=0, limit=100,
                     filter_path=None, **kwargs):
        """以视频、音频、图片及文档四种类型的视图获取所创建应用程序下的
        文件列表.

        :param file_type: 类型分为video、audio、image及doc四种。
        :param start: 返回条目控制起始值，缺省值为0。
        :param limit: 返回条目控制长度，缺省为1000，可配置。
        :param filter_path: 需要过滤的前缀路径，如：/apps/album

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :return: Response 对象
        """

        params = {
            'type': file_type,
            'start': start,
            'limit': limit,
            'filter_path': filter_path,
        }
        return self._request('stream', 'list', extra_params=params,
                             **kwargs)

    def download_stream(self, remote_path, **kwargs):
        """为当前用户下载一个流式文件.其参数和返回结果与下载单个文件的相同.

        :param remote_path: 需要下载的文件路径，以/开头的绝对路径，含文件名。

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
        url = 'https://d.pcs.baidu.com/rest/2.0/pcs/file'
        return self._request('stream', 'download', url=url,
                             extra_params=params, **kwargs)

    def rapid_upload(self, remote_path, content_length, content_md5,
                     content_crc32, slice_md5, ondup=None, **kwargs):
        """秒传一个文件.

        .. warning::
           * 被秒传文件必须大于256KB（即 256*1024 B）。
           * 校验段为文件的前256KB，秒传接口需要提供校验段的MD5。
             (非强一致接口，上传后请等待1秒后再读取)

        :param remote_path: 上传文件的全路径名。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param content_length: 待秒传文件的长度。
        :param content_md5: 待秒传文件的MD5。
        :param content_crc32: 待秒传文件的CRC32。
        :param slice_md5: 待秒传文件校验段的MD5。
        :param ondup: （可选）

                      * 'overwrite'：表示覆盖同名文件；
                      * 'newcopy'：表示生成文件副本并进行重命名，命名规则为“
                        文件名_日期.后缀”。
        :return: Response 对象
        """
        data = {
            'path': remote_path,
            'content-length': content_length,
            'content-md5': content_md5,
            'content-crc32': content_crc32,
            'slice-md5': slice_md5,
            'ondup': ondup,
        }
        return self._request('file', 'rapidupload', data=data, **kwargs)

    def add_download_task(self, source_url, remote_path,
                          rate_limit=None, timeout=60 * 60,
                          expires=None, callback='', **kwargs):
        """添加离线下载任务，实现单个文件离线下载.

        :param source_url: 源文件的URL。
        :param remote_path: 下载后的文件保存路径。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param rate_limit: 下载限速，默认不限速。
        :type rate_limit: int or long
        :param timeout: 下载超时时间，默认3600秒。
        :param expires: 请求失效时间，如果有，则会校验。
        :type expires: int
        :param callback: 下载完毕后的回调，默认为空。
        :type callback: str
        :return: Response 对象
        """

        data = {
            'source_url': source_url,
            'save_path': remote_path,
            'expires': expires,
            'rate_limit': rate_limit,
            'timeout': timeout,
            'callback': callback,
        }
        return self._request('services/cloud_dl', 'add_task',
                             data=data, **kwargs)

    def query_download_tasks(self, task_ids, operate_type=1,
                             expires=None, **kwargs):
        """根据任务ID号，查询离线下载任务信息及进度信息。

        :param task_ids: 要查询的任务ID列表
        :type task_ids: list or tuple
        :param operate_type:
                            * 0：查任务信息
                            * 1：查进度信息，默认为1
        :param expires: 请求失效时间，如果有，则会校验。
        :type expires: int
        :return: Response 对象
        """

        params = {
            'task_ids': ','.join(map(str, task_ids)),
            'op_type': operate_type,
            'expires': expires,
        }
        return self._request('services/cloud_dl', 'query_task',
                             extra_params=params, **kwargs)

    def list_download_tasks(self, need_task_info=1, start=0, limit=10, asc=0,
                            create_time=None, status=None, source_url=None,
                            remote_path=None, expires=None, **kwargs):
        """查询离线下载任务ID列表及任务信息.

        :param need_task_info: 是否需要返回任务信息:

                               * 0：不需要
                               * 1：需要，默认为1
        :param start: 查询任务起始位置，默认为0。
        :param limit: 设定返回任务数量，默认为10。
        :param asc:

                   * 0：降序，默认值
                   * 1：升序
        :param create_time: 任务创建时间，默认为空。
        :type create_time: int
        :param status: 任务状态，默认为空。
                       0:下载成功，1:下载进行中 2:系统错误，3:资源不存在，
                       4:下载超时，5:资源存在但下载失败, 6:存储空间不足,
                       7:目标地址数据已存在, 8:任务取消.
        :type status: int
        :param source_url: 源地址URL，默认为空。
        :param remote_path: 文件保存路径，默认为空。

                            .. warning::
                                * 路径长度限制为1000；
                                * 径中不能包含以下字符：``\\\\ ? | " > < : *``；
                                * 文件名或路径名开头结尾不能是 ``.``
                                  或空白字符，空白字符包括：
                                  ``\\r, \\n, \\t, 空格, \\0, \\x0B`` 。
        :param expires: 请求失效时间，如果有，则会校验。
        :type expires: int
        :return: Response 对象
        """

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
        return self._request('services/cloud_dl', 'list_task',
                             data=data, **kwargs)

    def cancel_download_task(self, task_id, expires=None, **kwargs):
        """取消离线下载任务.

        :param task_id: 要取消的任务ID号。
        :type task_id: str
        :param expires: 请求失效时间，如果有，则会校验。
        :type expires: int
        :return: Response 对象
        """

        data = {
            'expires': expires,
            'task_id': task_id,
        }
        return self._request('services/cloud_dl', 'cancle_task',
                             data=data, **kwargs)

    def list_recycle_bin(self, start=0, limit=1000, **kwargs):
        """获取回收站中的文件及目录列表.

        :param start: 返回条目的起始值，缺省值为0
        :param limit: 返回条目的长度，缺省值为1000
        :return: Response 对象
        """

        params = {
            'start': start,
            'limit': limit,
        }
        return self._request('file', 'listrecycle',
                             extra_params=params, **kwargs)

    def restore_recycle_bin(self, fs_id, **kwargs):
        """还原单个文件或目录（非强一致接口，调用后请sleep 1秒读取）.

        :param fs_id: 所还原的文件或目录在PCS的临时唯一标识ID。
        :type fs_id: str
        :return: Response 对象
        """

        data = {
            'fs_id': fs_id,
        }
        return self._request('file', 'restore', data=data, **kwargs)

    def multi_restore_recycle_bin(self, fs_ids, **kwargs):
        """批量还原文件或目录（非强一致接口，调用后请sleep1秒 ）.

        :param fs_ids: 所还原的文件或目录在 PCS 的临时唯一标识 ID 的列表。
        :type fs_ids: list or tuple
        :return: Response 对象
        """

        data = {
            'param': json.dumps({
                'list': [{'fs_id': fs_id} for fs_id in fs_ids]
            }),
        }
        return self._request('file', 'restore', data=data, **kwargs)

    def clean_recycle_bin(self, **kwargs):
        """清空回收站.

        :return: Response 对象
        """

        data = {
            'type': 'recycle',
        }
        return self._request('file', 'delete', data=data, **kwargs)
