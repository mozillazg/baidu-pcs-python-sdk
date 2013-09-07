#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pdb
import time
import os

from baidupcs import PCS
from utils import content_md5, content_crc32, slice_md5

logging.basicConfig(level=logging.WARN,
                    format='\n%(funcName)s - %(lineno)d\n%(message)s')
logger = logging.getLogger(__name__)

access_token = '3.3f56524f9e796191ce5baa84239feb15.2592000.1380728222.'
access_token += '570579779-1274287'
pcs = PCS(access_token)


def test_info():
    result = pcs.info()
    logger.warn(result)
    assert True


def test_upload():
    result = pcs.upload('/apps/test_sdk/test.txt', 'test')
    logger.warn(result)
    assert True


def test_superfile():
    f1_md5 = pcs.upload_tmpfile('abc')['md5']
    f2_md5 = pcs.upload_tmpfile('def')['md5']
    result = pcs.upload_superfile('/apps/test_sdk/super2.txt',
                                  [f1_md5, f2_md5])
    logger.warn(result)
    assert True


def test_download():
    result = pcs.download('/apps/test_sdk/super2.txt')
    logger.warn(result)
    assert 'abc' in result
    assert 'def' in result


def test_mkdir():
    result = pcs.mkdir('/apps/test_sdk/testmkdir')
    logger.warn(result)
    assert True


def test_meta():
    result = pcs.meta('/apps/test_sdk/superfile.txt')
    logger.warn(result)
    assert True


def test_multi_meta():
    result = pcs.multi_meta(['/apps/test_sdk/superfile.txt',
                            '/apps/test_sdk/testmkdir'])
    logger.warn(result)
    assert True


def test_file_list():
    result = pcs.file_list('/apps/test_sdk/testmkdir')
    logger.warn(result)
    assert True


def test_move():
    result = pcs.move('/apps/test_sdk/test.txt',
                      '/apps/test_sdk/testmkdir/a.txt')
    logger.warn(result)
    assert True


def test_multi_move():
    pcs.upload('/apps/test_sdk/test.txt', 'test')
    path_list = [
        {
            'from': '/apps/test_sdk/test.txt',
            'to': '/apps/test_sdk/testmkdir/b.txt',
        },
        {
            'from': '/apps/test_sdk/testmkdir/b.txt',
            'to': '/apps/test_sdk/testmkdir/a.txt',
        }
    ]
    result = pcs.multi_move(path_list)
    logger.warn(result)
    assert True


def test_copy():
    pcs.upload('/apps/test_sdk/test.txt', 'test')
    result = pcs.copy('/apps/test_sdk/test.txt',
                      '/apps/test_sdk/testmkdir/c.txt')
    logger.warn(result)
    assert True


def test_multi_copy():
    path_list = [
        {
            'from': '/apps/test_sdk/test.txt',
            'to': '/apps/test_sdk/testmkdir/d.txt',
        },
        {
            'from': '/apps/test_sdk/testmkdir/c.txt',
            'to': '/apps/test_sdk/testmkdir/e.txt',
        }
    ]
    result = pcs.multi_copy(path_list)
    logger.warn(result)
    assert True


def test_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', 'test')
    result = pcs.delete('/apps/test_sdk/testmkdir/e.txt')
    logger.warn(result)
    assert True


def test_multi_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', 'test')
    result = pcs.multi_delete(['/apps/test_sdk/testmkdir/e.txt',
                              '/apps/test_sdk/testmkdir/d.txt'])
    logger.warn(result)
    assert True


def test_search():
    result = pcs.search('/apps/test_sdk/testmkdir', 'a')
    logger.warn(result)
    assert True


def test_thumbnail():
    result = pcs.thumbnail('/apps/test_sdk/testmkdir/404.png', 20, 20)
    logger.warn(result[:10])
    assert True


def test_diff():
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', 'testabc', ondup='overwrite')
    result = pcs.diff()
    logger.warn(result)
    logger.warn('\n')
    new_cursor = result['cursor']
    time.sleep(60)
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', str(time.time()),
               ondup='overwrite')
    result = pcs.diff(cursor=new_cursor)
    logger.warn(result)
    assert True


def test_video_convert():
    result = pcs.video_convert('/apps/test_sdk/testmkdir/test.mp4',
                               'M3U8_320_240')
    logger.warn(result)
    assert True


def test_stream_list():
    result = pcs.stream_list('image')
    logger.warn(result)
    result = pcs.stream_list('doc', filter_path='/apps/test_sdk/test')
    logger.warn(result)
    assert True


def test_stream_download():
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
    pdb.set_trace()
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
    task_id = pcs.list_offline_download_task()['task_info'][0]['task_id']
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
