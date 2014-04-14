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
utils of python-weed like adaption of weed response, etc..
'''
import json
import urlparse
import requests
from conf import LOGGER


class WeedAssignKey(dict):
    ''' represent this json in dict and object:

    {"count":1,"fid":"3,01637037d6","url":"127.0.0.1:8080","publicUrl":"localhost:8080"}

    '''
    def __init__(self, json_of_weed_response=None):

        self['fid'] = ''
        self['count'] = 0
        self['url'] = ''
        self['publicUrl'] = ''

        if json_of_weed_response:
            try:
                d = json.loads(json_of_weed_response)
                self.update(d)
            except Exception as e:
                LOGGER.error('Error for json.loads "%s".\nException: %s'
                             % (json_of_weed_response, e))

        for k, v in self.items():
            setattr(self, k, v)
        super(WeedAssignKey, self).__init__()



class WeedAssignKeyExtended(WeedAssignKey):
    ''' extend weed-assign-key for adding these keys:

      'full_url', 'full_public_url', 'fid_full_url', 'fid_full_publicUrl':

      represents:
        self['full_url'] = 'http://' + self['url']
        self['full_publicUrl'] = 'http://' + self['publicUrl']
        self['fid_full_url'] = self['full_url'] + '/' + self['fid']
        self['fid_full_publicUrl'] = self['full_publicUrl'] + '/' + self['fid']

    '''
    def __init__(self, json_of_weed_response=None):
        super(WeedAssignKeyExtended, self).__init__(json_of_weed_response)
        self.update_full_urls()


    def update_full_urls(self):
        ''' update "full_url" and "full_publicUrl" '''
        self['full_url'] = 'http://' + self['url']
        self['full_publicUrl'] = 'http://' + self['publicUrl']
        self['fid_full_url'] = urlparse.urljoin(self['full_url'], self['fid'])
        self['fid_full_publicUrl'] = urlparse.urljoin(self['full_publicUrl'], self['fid'])
        for k, v in self.items():
            setattr(self, k, v)
        # self['full_url'] = urlparse.urljoin('http://', self['url'])
        # self['full_publicUrl'] = urlparse.urljoin('http://', self['publicUrl'])
        # self['fid_full_url'] = urlparse.urljoin(self['full_url'], self['fid'])
        # self['fid_full_publicUrl'] = urlparse.urljoin(self['full_publicUrl'], self['fid'])



class WeedOperationResponse(dict):
    ''' represent this json in dict and object:

    {"count":1,"fid":"3,01637037d6","url":"127.0.0.1:8080","publicUrl":"localhost:8080"}

    '''
    def __init__(self, *args, **kws):
        super(WeedOperationResponse, self).__init__(*args, **kws)
        self['fid'] = ''
        self['storage_size'] = 0
        self['fid_full_url'] = ''
        self['fname'] = ''

        ## http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
        self.__dict__ = self
        # for k, v in self.items():
        #     setattr(self, k, v)



def put_file(fp, fid_full_url, fname='', http_headers=None):
    """
    save fp(file-pointer, file-description) to a remote weed volume.
    eg:
       PUT http://127.0.0.1:8080/3,20392030920

    addtional fname and http_headers can help weed-server to decide content-type and other infos.

    eg:
       @fname = 'hello.txt' or 'abc.jpg' or 'youknow.png',

       @http_headers = {'content-type' : 'image/png'} or
       @http_headers = {'content-type' : 'image/jpeg'} or
       @http_headers = {'content-type' : 'text/xml'} or
       @http_headers = {'content-type' : 'application/json'}


    """
    pos = fp.tell()
    tmp_uploading_file_name = fname or 'a.unknown'
    # print('fid_full_url is: "%s"' % fid_full_url)
    # print('fp position: %d' % fp.tell())
    # print('fp info: length: %d' % len(fp.read()))
    # fp.seek(0)
    if http_headers:
        rsp = requests.post(fid_full_url, files={tmp_uploading_file_name : fp}, headers=http_headers)
    else:
        rsp = requests.post(fid_full_url, files={tmp_uploading_file_name : fp})

    # recove position of fp
    fp.seek(pos)

    # LOGGER.debug(rsp.request.headers)
    _j = rsp.json()
    _r = WeedOperationResponse()
    _r['fid_full_url'] = fid_full_url
    _r.fname = fname
    _r.storage_size = rsp.json().get('size', 0)
    LOGGER.info('_r is: %s' % _r)

    if 'error' in _j:
        LOGGER.error('Put file fails. Error returns from weedfs: "%s"' % _j['error'])
    if not _j.has_key('size') or _j['size'] == 0: # post new file fails
        err_msg = 'Could not save file on weed-fs with fid_full_url: %s' % (fid_full_url)
        LOGGER.error(err_msg)

    return _r

