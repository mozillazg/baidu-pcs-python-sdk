Changelog
=========


0.3.2 (2014-03-23)
-------------------

* 新增：添加 ``tools.get_new_access_token`` 用于获取新的 Access Token 和 Refresh Token；
* 改进：解决上传大文件时的内存占用问题；
* 变更：去掉 ``verify=False`` 。如果有出现 ``SSLError`` 请参考 `此文`__ 。

__ https://github.com/mozillazg/baidu-pcs-python-sdk/wiki/%E5%87%BA%E7%8E%B0-SSLError-%E9%94%99%E8%AF%AF%EF%BC%9F


0.3.1 (2013-10-25)
------------------

* 改进：上传、下载部分的 api 改用加速域名 c.pcs.baidu.com 和 d.pcs.baidu.com


0.3.0 (2013-09-13)
------------------

* 新增：添加 ``baidupcs.InvalidToken`` 异常


0.2.0 (2013-09-12)
------------------

* 新增：支持 Python 3


0.1.0 (2013-09-09)
------------------

* 新增：第一版，封装了所有 `文件操作 RESET API`__ .

__ http://developer.baidu.com/wiki/index.php?title=docs/pcs/rest/file_data_apis_list
