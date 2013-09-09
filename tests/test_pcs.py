#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import os
import pdb
# from PIL import Image
# from StringIO import StringIO

from baidupcs import PCS
from utils import content_md5, content_crc32, slice_md5

logging.basicConfig(level=logging.WARN,
                    format='\n%(funcName)s - %(lineno)d\n%(message)s')
logger = logging.getLogger(__name__)

access_token = '3.3f56524f9e796191ce5baa84239feb15.2592000.1380728222.'
access_token += '570579779-1274287'
pcs = PCS(access_token)


def test_info():
    response = pcs.info()
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload():
    response = pcs.upload('/apps/test_sdk/test.txt', 'test', ondup='overwrite')
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload_tmpfile():
    response = pcs.upload_tmpfile('abc')
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload_superfile():
    f1_md5 = pcs.upload_tmpfile('abc').json()['md5']
    f2_md5 = pcs.upload_tmpfile('def').json()['md5']
    time.sleep(1)
    response = pcs.upload_superfile('/apps/test_sdk/super2.txt',
                                    [f1_md5, f2_md5], ondup='overwrite')
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_download():
    response = pcs.download('/apps/test_sdk/super2.txt')
    logger.warn(response.status_code)
    assert response.ok
    assert 'abc' in response.content


def test_download_range():
    headers = {'Range': 'bytes=0-2'}
    response = pcs.download('/apps/test_sdk/super2.txt', headers=headers)
    assert response.content == 'abc'
    headers = {'Range': 'bytes=3-5'}
    response = pcs.download('/apps/test_sdk/super2.txt', headers=headers)
    assert response.content == 'def'


def test_mkdir():
    response = pcs.mkdir('/apps/test_sdk/testmkdir')
    logger.warn(response.status_code)
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061
    logger.warn(response.json())


def test_meta():
    response = pcs.meta('/apps/test_sdk/super2.txt')
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_multi_meta():
    response = pcs.multi_meta(['/apps/test_sdk/super2.txt',
                              '/apps/test_sdk/testmkdir'])
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_list_files():
    response = pcs.list_files('/apps/test_sdk/testmkdir')
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_move():
    response = pcs.move('/apps/test_sdk/test.txt',
                        '/apps/test_sdk/testmkdir/a.txt')
    logger.warn(response.status_code)
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061
    logger.warn(response.json())


def test_multi_move():
    pcs.upload('/apps/test_sdk/test.txt', 'test')
    pcs.upload('/apps/test_sdk/b.txt', 'test')
    path_list = [
        ('/apps/test_sdk/test.txt', '/apps/test_sdk/testmkdir/b.txt'),
        ('/apps/test_sdk/b.txt', '/apps/test_sdk/testmkdir/a.txt'),
    ]
    response = pcs.multi_move(path_list)
    logger.warn(response.status_code)
    assert response.json()
    logger.warn(response.json())
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_copy():
    pcs.upload('/apps/test_sdk/test.txt', 'test')
    response = pcs.copy('/apps/test_sdk/test.txt',
                        '/apps/test_sdk/testmkdir/c.txt')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_multi_copy():
    pcs.upload('/apps/test_sdk/test.txt', 'test')
    pcs.upload('/apps/test_sdk/b.txt', 'test')
    path_list = [
        ('/apps/test_sdk/test.txt', '/apps/test_sdk/testmkdir/b.txt'),
        ('/apps/test_sdk/b.txt', '/apps/test_sdk/testmkdir/a.txt'),
    ]
    response = pcs.multi_copy(path_list)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', 'test')
    response = pcs.delete('/apps/test_sdk/testmkdir/e.txt')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    assert response.ok


def test_multi_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', 'test')
    pcs.upload('/apps/test_sdk/testmkdir/d.txt', 'test')
    response = pcs.multi_delete(['/apps/test_sdk/testmkdir/e.txt',
                                '/apps/test_sdk/testmkdir/d.txt'])
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    assert response.ok


def test_search():
    response = pcs.search('/apps/test_sdk/', 'test')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    assert response.ok


def test_thumbnail():
    response = pcs.thumbnail('/apps/test_sdk/testmkdir/404.png', 100, 100)
    logger.warn(response.status_code)
    logger.warn(repr(response.content[:10]))
    # im = Image.open(StringIO(response.content))
    # im.show()
    assert response.ok


def test_diff():
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', 'testabc', ondup='overwrite')
    response = pcs.diff()
    new_cursor = response.json()['cursor']
    time.sleep(5)
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', str(time.time()),
               ondup='overwrite')
    response = pcs.diff(cursor=new_cursor)
    new_cursor = response.json()['cursor']
    time.sleep(5)
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', str(time.time()),
               ondup='overwrite')
    response = pcs.diff(cursor=new_cursor)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.json()
    assert response.ok


def test_video_convert():
    response = pcs.video_convert('/apps/test_sdk/testmkdir/test.mp4',
                                 'M3U8_320_240')
    logger.warn(response.status_code)
    logger.warn(response.content)
    assert response.ok


def test_list_streams():
    response = pcs.list_streams('image')
    logger.warn(response.json())
    response = pcs.list_streams('doc', filter_path='/apps/test_sdk/test')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_download_stream():
    result = pcs.stream_download('/apps/test_sdk/testmkdir/404.png')
    logger.warn(result[:10])
    assert True


def test_rapid_upload():
    content = 'a' * 1024 * 1024
    pcs.upload('/apps/test_sdk/testmkdir/upload.txt', content,
               ondup='overwrite')
    time.sleep(3)
    result = pcs.rapid_upload('/apps/test_sdk/testmkdir/rapid.txt',
                              len(content), content_md5(content),
                              content_crc32(content),
                              slice_md5(content[:1024 * 256]),
                              ondup='overwrite')
    logger.warn(result)
    assert True


def test_add_offline_download_task():
    url = 'http://bcscdn.baidu.com/netdisk/BaiduYunGuanjia_4.1.0.exe'
    remote_path = '/apps/test_sdk/testmkdir/BaiduYunGuanjia_4.1.0.exe'
    result = pcs.add_offline_download_task(url, remote_path)
    logger.warn(result)
    assert True


def test_query_offline_download_task():
    url1 = 'http://yy.client.fwdl.kingsoft.com/Moon-V051770.rar'
    url2 = 'http://bcscdn.baidu.com/netdisk/BaiduYunGuanjia_4.1.0.exe'
    remote_path = '/apps/test_sdk/testmkdir/%s'
    task1 = pcs.add_offline_download_task(url1,
                                          remote_path % os.path.basename(url1))
    task2 = pcs.add_offline_download_task(url2,
                                          remote_path % os.path.basename(url2))
    task_ids = [task1['task_id'], task2['task_id']]
    result = pcs.query_offline_download_task(task_ids)
    logger.warn(result)
    assert True


def test_list_offline_download_task():
    result = pcs.list_offline_download_task()
    logger.warn(result)
    assert True


def test_cancel_offline_download_task():
    task_info = pcs.list_offline_download_task()['task_info']
    if not task_info:
        logger.warn('\n')
        assert True
    else:
        task_id = task_info[0]['task_id']
        result = pcs.cancel_offline_download_task(task_id)
        logger.warn(result)
        assert True


def test_recycle_bin_list():
    result = pcs.recycle_bin_list()
    logger.warn(result)
    assert True


def test_recycle_bin_restore():
    fs_id = pcs.recycle_bin_list()['list'][0]['fs_id']
    result = pcs.recycle_bin_restore(fs_id)
    logger.warn(result)
    assert True


def test_recycle_bin_multi_restore():
    pcs.upload('/apps/test_sdk/testmkdir/1.txt', 'test', ondup='overwrite')
    pcs.delete('/apps/test_sdk/testmkdir/1.txt')
    pcs.upload('/apps/test_sdk/testmkdir/2.txt', 'test', ondup='overwrite')
    pcs.delete('/apps/test_sdk/testmkdir/2.txt')
    time.sleep(1)
    fs_ids = [x['fs_id'] for x in pcs.recycle_bin_list()['list'][:1]]
    result = pcs.recycle_bin_multi_restore(fs_ids)
    logger.warn(result)
    assert True


def test_recycle_bin_clean():
    result = pcs.recycle_bin_clean()
    logger.warn(result)
    assert True
