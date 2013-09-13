API
===

.. .. autoclass:: requests.Response
..    :members:


错误和异常
----------

.. autoclass:: baidupcs.InvalidToken


PCS 类
------

.. autoclass:: baidupcs.PCS


关于各 api 方法的更多示例请参考 `测试用例 <https://github.com/mozillazg/baidu-pcs-python-sdk/tree/master/tests>`__ 。

关于各 api 方法的 ``response.json()`` 字典值的含义请查看 `百度 PCS 文档 <http://developer.baidu.com/wiki/index.php?title=docs/pcs/rest/file_data_apis_list>`__ 。


基本功能
--------

空间配额信息
~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.info

上传单个文件
~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.upload

分片上传—文件分片及上传
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.upload_tmpfile

分片上传—合并分片文件
~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.upload_superfile

下载单个文件
~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.download

创建目录
~~~~~~~~
.. automethod:: baidupcs.PCS.mkdir

获取单个文件/目录的元信息
~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.meta

批量获取文件/目录的元信息
~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.multi_meta

获取目录下的文件列表
~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.list_files

移动单个文件/目录
~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.move

批量移动单个文件/目录
~~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.multi_move

拷贝单个文件/目录
~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.copy

批量拷贝文件/目录
~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.multi_copy

删除单个文件/目录
~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.delete

批量删除文件/目录
~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.multi_delete

搜索
~~~~
.. automethod:: baidupcs.PCS.search


高级功能
--------

缩略图
~~~~~~
.. automethod:: baidupcs.PCS.thumbnail

增量更新查询
~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.diff

视频转码
~~~~~~~~
.. automethod:: baidupcs.PCS.video_convert

获取流式文件列表
~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.list_streams

下载流式文件
~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.download_stream

秒传文件
~~~~~~~~
.. automethod:: baidupcs.PCS.rapid_upload

添加离线下载任务
~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.add_download_task

精确查询离线下载任务
~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.query_download_tasks

查询离线下载任务列表
~~~~~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.list_download_tasks

取消离线下载任务
~~~~~~~~~~~~~~~~
.. automethod:: baidupcs.PCS.cancel_download_task


回收站
~~~~~~

查询回收站文件
++++++++++++++
.. automethod:: baidupcs.PCS.list_recycle_bin

还原单个文件或目录
++++++++++++++++++
.. automethod:: baidupcs.PCS.restore_recycle_bin

批量还原文件或目录
++++++++++++++++++
.. automethod:: baidupcs.PCS.multi_restore_recycle_bin

清空回收站
++++++++++
.. automethod:: baidupcs.PCS.clean_recycle_bin
