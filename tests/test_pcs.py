#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcs import PCS

access_token = '3.3f56524f9e796191ce5baa84239feb15.2592000.1380728222.'
access_token += '570579779-1274287'
pcs = PCS(access_token)


def test_info():
    result = pcs.info()
    assert result


def test_upload():
    result = pcs.upload('/apps/test_sdk/test.txt', 'test')
    assert result


def test_superfile():
    f1_md5 = pcs.upload_tmpfile('abc')['md5']
    f2_md5 = pcs.upload_tmpfile('def')['md5']
    result = pcs.upload_superfile('/apps/test_sdk/super2.txt', [f1_md5, f2_md5])
    assert result
