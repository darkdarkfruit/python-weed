# ** -- coding: utf-8 -- **
#!/usr/bin/env python
#
#Copyright (c) 2011 darkdarkfruit <darkdarkfruit@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#

'''
python interface of weed-fs filer service.
currently, weed-fs supports filer service from v0.52 and above.

in this module, default filer service port is set to: 27100
'''

__all__ = ['WeedFiler']

import os
import StringIO

import requests
from conf import *
from util import *


class WeedFiler(object):
    """ weed filer service.
    """

    def __init__(self, host='127.0.0.1', port=27100, protocol='http'):
        """ construct WeedFiler

        Arguments:
        - `host`:
        - `port`:
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.uri = '%s:%d' % (host, port)
        self.url = '%s://' % self.protocol + self.uri


    def put(self, fp, remote_path, echo=False):
        """ put a file @fp to @remote_path on weedfs

        returns @remote_path if succeeds else None
        Arguments:
        - `self`:
        - `remote_path`:
        - `echo`: if True, print response
        """
        url = urlparse.urljoin(self.url, remote_path)
        try:
            if echo:
                LOGGER.debug('http POST %s' % url)
            rsp = requests.post(url, files={'file' : fp if not isinstance(fp, str) else open(fp, 'rb')})
            if rsp.ok:
                return remote_path
            else:
                LOGGER.error('%d POST %s' % (rsp.status_code, url))
        except Exception as e:
            LOGGER.error('Error POSTing %s. e:%s' % (url, e))

        return None


    def rm(self, remote_path):
        ''' remove a @remote_path by http DELETE '''
        try:
            rsp = requests.delete(remote_path)
            if not rsp.ok:
                LOGGER.error('Error deleting file: %s. ' % (remote_path))
            return rsp.ok
        except Exception as e:
            LOGGER.error('Error deleting file: %s. e: %s' % (remote_path, e))


    def list(self, dir, pretty=False):
        ''' list sub folders and files of @dir. show a better look if you turn on @pretty

        returns a dict of "sub-folders and files'
        '''
        d = dir if dir.endswith('/') else (dir + '/')
        url = urlparse.urljoin(self.url, d)
        try:
            rsp = requests.get(url)
            if not rsp.ok:
                LOGGER.error('Error listing "%s". [HTTP %d]' % (url, rsp.status_code))
            return rsp.json()
        except Exception as e:
            LOGGER.error('Error listing "%s". e: %s' % (url, e))
        return None


    def mkdir(self, _dir):
        ''' make dir on filer.

        eg:
           mkdir('/image/avatar').
           mkdir('/image/avatar/helloworld')

        We will post a file named '.info' to @_dir.
        '''
        return self.put(StringIO.StringIO('.info'), os.path.join(_dir, '.info'))

