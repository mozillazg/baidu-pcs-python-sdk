#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hashlib import md5
from zlib import crc32


def content_md5(content):
    """待秒传的文件的MD5."""
    return md5(content).hexdigest()


def content_crc32(content):
    """待秒传文件CRC32."""
    return '%x' % (crc32(content, 0) & 0xffffffff)


def slice_md5(content):
    """待秒传文件校验段的MD5."""
    return md5(content[:1024 * 256]).hexdigest()
