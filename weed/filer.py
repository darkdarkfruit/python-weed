# ** -- coding: utf-8 -- **
# !/usr/bin/env python
#
# Copyright (c) 2011 darkdarkfruit <darkdarkfruit@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
python interface of weed-fs filer service.
currently, weed-fs supports filer service from v0.52 and above.

in this module, default filer service port is set to: 27100
"""

__all__ = ['WeedFiler']

import io
import os
from urllib import parse

from weed.util import *


class WeedFiler(object):
    """ weed filer service.
    """

    def __init__(self, url_base='http://localhost:27100'):
        """ construct WeedFiler

        Arguments:
        - `host`: defaults to '127.0.0.1'
        - `port`: defaults to 27100
        :param url_base:
        """

        self.url_base = url_base
        self.uri = self.url_base.split('//')[-1]

    def get(self, remote_path) -> None or {}:
        """ put a file @fp to @remote_path on seaweedfs

        returns @remote_path if succeeds else None
        Arguments:
        - `self`:
        - `remote_path`:
        - `echo`: if True, print response
        """
        url = parse.urljoin(self.url_base, remote_path)
        try:
            rsp = requests.get(url)
            if rsp.ok:
                result = {'content_length': rsp.headers.get('content-length'),
                          'content_type': rsp.headers.get('content-type'),
                          'content': rsp.content}
                return result
            else:
                g_logger.error('%d GET %s' % (rsp.status_code, url))
                return None
        except Exception as e:
            g_logger.error('Error POSTing %s. e:%s' % (url, e))
            return None

    def put(self, fp, remote_path) -> None or str:
        """ put a file @fp to @remote_path on seaweedfs

        returns @remote_path if succeeds else None
        :arg
        - `fp`: either a file-handler by method open(with binary mode) or a str to the file-path.
        - `remote_path`:
        :returns
        None or str-of-remote-path

        """
        url = parse.urljoin(self.url_base, remote_path)
        is_our_responsibility_to_close_file = False
        if isinstance(fp, str):
            _fp = open(fp, 'rb')
            is_our_responsibility_to_close_file = True
        else:
            _fp = fp
        result = None
        try:
            rsp = requests.post(url, files={'file': _fp})
            if rsp.ok:
                result = remote_path
            else:
                g_logger.error('%d POST %s' % (rsp.status_code, url))
        except Exception as e:
            g_logger.error('Error POSTing %s. e:%s' % (url, e))

        # close fp if parameter fp is a str
        if is_our_responsibility_to_close_file:
            try:
                _fp.close()
            except Exception as e:
                g_logger.warning('Could not close fp: %s. e: %s' % (_fp, e))

        return result

    def delete(self, remote_path) -> bool:
        """ remove a @remote_path by http DELETE """
        url = parse.urljoin(self.url_base, remote_path)
        try:
            rsp = requests.delete(url)
            if not rsp.ok:
                g_logger.error('Error deleting file: %s. ' % remote_path)
            return rsp.ok
        except Exception as e:
            g_logger.error('Error deleting file: %s. e: %s' % (remote_path, e))
            return False

    def list(self, directory) -> None or {}:
        """ list sub folders and files of @dir. show a better look if you turn on @pretty

        returns a dict of "sub-folders and files'
        """
        d = directory if directory.endswith('/') else (directory + '/')
        url = parse.urljoin(self.url_base, d)
        headers = {'Accept': 'application/json'}
        try:
            rsp = requests.get(url, headers=headers)
            if not rsp.ok:
                g_logger.error('Error listing "%s". [HTTP %d]' % (url, rsp.status_code))
                return None
            return rsp.json()
        except Exception as e:
            g_logger.error('Error listing "%s". e: %s' % (url, e))
        return None

    def mkdir(self, directory) -> None or str:
        """ make dir on filer.

        eg:
           mkdir('/image/avatar').
           mkdir('/image/avatar/helloworld')

        We will post a file named '.info' to @_dir.
        """
        return self.put(io.StringIO('.info'), os.path.join(directory, '.info'))
