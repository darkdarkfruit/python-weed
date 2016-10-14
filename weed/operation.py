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
operations to weedfs.
'''


__all__ = ['WeedOperation']


import json
import random
import StringIO
import urlparse
import requests
from conf import *
from util import *

from master import *
from volume import *



class WeedOperation(object):
    """ DO CRUD operations to weed-fs.

    Arguments you need to supply is just weed master.
    The master will find a volume automaticlly.
    Currently, implement it with requests. Maybe *tornado or  *mongrel2 + brubeck* is better?

    """

    def __init__(self, master_host='127.0.0.1', master_port=9333, prefetch_volumeIds=False):
        self.master = WeedMaster(master_host, master_port, prefetch_volumeIds=prefetch_volumeIds)


    def get_volume_fid_full_url(self, fid):
        ''' return a random fid_full_url of volume by @fid

        eg: (randomly choosed from locations)
          return:  'http://127.0.0.1:27000/3,1234101234'  or
          return:  'http://127.0.0.1:27001/3,1234101234'  or
          return:  'http://127.0.0.1:27002/3,1234101234'
        '''


    def acquire_new_fids(self, count=1):
        """
        get a new avalable fid or a fid list
        return:
          ['3,12301234'] or
          ['3,12301234', '3,12301234_1', '3,12301234_2',  '3,12301234_3', etc..]

        ----------

        """
        wak = self.master.acquire_new_assign_key(count=count)
        # print(wak)
        fid = wak.fid

        if count == 1:
            return [fid]
        else:
            fids = [fid] + [fid + ('_%d' % (i + 1)) for i in range(count)]
            return fids


    def get_fid_full_url(self, fid, get_public=False):
        ''' return a random fid_full_url of volume by @fid

        eg: (randomly choosed from locations)
          return:  'http://127.0.0.1:27000/3,1234101234'  or
          return:  'http://127.0.0.1:27001/3,1234101234'  or
          return:  'http://127.0.0.1:27002/3,1234101234'

        tip: WeedMaster.looup returns a dict like below:
        -----------
        {
          "locations": [
            {
              "publicUrl": "localhost:8080",
              "url": "localhost:8080"
            }
          ]
        }
        -----------

        return something like: 'http://127.0.0.1:8080/3,0230203913'
        '''
        volume_id = fid.split(',')[0]
        full_url = None
        try:
            r = self.master.lookup(volume_id)
            locations = r['locations']

            # choose a random location
            location = locations[random.randint(0, len(locations) - 1)]
            if get_public is False:
                full_url = 'http://%s/%s' % (location['url'], fid)
            else:
                full_url = 'http://%s/%s' % (location['publicUrl'], fid)
        except Exception as e:
            LOGGER.error('Could not get volume location of this fid: %s. Exception is: %s' % (fid, e))
        return full_url


    ## -----------------------------------------------------------
    ##    weedfs operation: get/put/delete, and CRUD-aliases starts
    ## -----------------------------------------------------------
    def get(self, fid, fname=''):
        """
        read/get a file from weed-fs with @fid.

        @just_url(default is False):
          if True -> just return an object of WeedOperationResponse(web-servers/browsers like nginx, chrome can get resource by this url( WeedOperationResponse.fid_full_url ))
          if False -> return a http response of requests(package requests) if @just_content is False else return file_content

        @just_content(default is True):
          if True -> just return the file's content
          if False -> return a response of requests.Respond object. (eg: You can get content_type of the file being get)

        return a WeedOperationResponse instance
        """
        LOGGER.debug('|--> Getting file. fid: %s, fname:%s' % (fid, fname))

        fid_full_url = 'wrong_url'
        wor = WeedOperationResponse()
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Reading file fid: %s, fname: %s, fid_full_url: %s' % (fid, fname, fid_full_url))
            rsp = self.get_http_response(fid_full_url)
            wor.status = 'success'
            wor.fid = fid
            wor.url = fid_full_url
            wor.name = fname
            wor.content = rsp.content
            wor.content_type = rsp.headers.get('content-type')
        except Exception as e:
            err_msg = 'Could not read file fid: %s, fname: %s, fid_full_url: %s, e: %s' % (fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            wor.status = 'fail'
            wor.message = err_msg

        return wor


    def get_url(self, fid):
        ''' return a random fid_full_url of volume by @fid, alias to get_fid_full_url(fid)

        eg: (randomly choosed from locations)
          return:  'http://127.0.0.1:27000/3,1234101234'  or
          return:  'http://127.0.0.1:27001/3,1234101234'  or
          return:  'http://127.0.0.1:27002/3,1234101234'

        return something like: 'http://127.0.0.1:8080/3,0230203913'
        '''
        return self.get_fid_full_url(fid)


    def get_http_response(self, fid_full_url):
        ''' return a "requests.Response" if we want whole info of the http request '''
        return requests.get(fid_full_url)


    def get_content(self, fid, fname=''):
        ''' return just file's content. use method "get" to get more file's info '''
        return self.get(fid, fname).content


    def put(self, fp, fid=None, fname=''):
        """  put a file to weed-fs.

        if @fid provided, put @fp with @fid;
        if @fid not provided, generate a new fid for it.

        return a WeedOperationResponse instance
        """
        LOGGER.info('|--> Putting file@fid:%s, fname:%s' % (fid, fname))
        fid_full_url = 'wrong_url'
        _fid = fid
        try:
            if not fid:
                wak = self.master.acquire_new_assign_key()
                # print(wak)
                _fid = wak.fid
                LOGGER.debug('no fid. accquired new one: "%s"' % _fid)
                fid_full_url = wak.fid_full_url
            else:
                fid_full_url = self.get_fid_full_url(fid)
        except Exception as e:
            err_msg = 'Could not put file. fp: "%s", fname: "%s", fid_full_url: "%s", e: %s' % (fp, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None

        wor = WeedOperationResponse()
        try:
            _fp = open(fp, 'r') if isinstance(fp, str) else fp

            LOGGER.info('Putting file with fid: %s, fid_full_url:%s for file: fp: %s, fname: %s'
                         % (_fid, fid_full_url, fp, fname))
            wor = put_file(_fp, fid_full_url, fname)
            LOGGER.info('%s' % wor)
            wor.fid = _fid
        except Exception as e:
            err_msg = 'Could not put file. fp: "%s", fname: "%s", fid_full_url: "%s", e: %s' % (fp, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            wor.status = 'fail'
            wor.message = err_msg

        # close fp if parameter fp is a str
        if isinstance(fp, str):
            try:
                _fp.close()
            except Exception as e:
                LOGGER.warning('Could not close fp: %s. e: %s' % (_fp, e))

        return wor


    def delete(self, fid, fname=''):
        """ remove a file in weed-fs with @fid.

        if storage == 0, then @fid in weedfs is not exist.

        return a WeedOperationResponse instance
        """
        LOGGER.debug('|--> Deleting file@%s, fname: %s' % (fid, fname))
        wor = WeedOperationResponse()
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Deleting file: fid: %s, fname: %s, fid_full_url: %s' % (fid, fname, fid_full_url))

            r = requests.delete(fid_full_url)
            rsp_json = r.json()

            wor.status = 'success'
            wor.fid = fid
            wor.url = fid_full_url
            wor.name = fname

            if rsp_json.has_key('size'):
                wor.storage_size = rsp_json['size']
                if wor.storage_size == 0:
                    err_msg = ('Error: fid@%s is not exist.' % fid)
                    wor.status = 'fail'
                    wor.message = err_msg
                    LOGGER.error(err_msg)
        except Exception as e:
            err_msg = 'Deleting file: fid: %s, fname: %s, fid_full_url: %s, e: %s' % (fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            wor.status = 'fail'
            wor.message = err_msg
            LOGGER.error(err_msg)

        return wor


    def exists(self, fid):
        ''' detects @fid's existence '''
        if ',' not in fid:      # fid should have a volume_id
            return False
        try:
            volume_id = fid.split(',')[0]
        except Exception as e:
            LOGGER.error('Invalid fid:"%s". e: %s' % (fid, e))
            return False

        if not self.master.lookup(volume_id):
            return False
        fid_full_url = self.get_fid_full_url(fid)
        try:
            rsp = requests.head(fid_full_url, allow_redirects=True)
            if not rsp.ok:
                return False
            else:
                return True
        except Exception as e:
            LOGGER.error('Error occurs while requests.head. e: %s' % e)
            return False



    def crud_create(self, fp, fname=''):
        """  CREATE of CRUD(C). Alias to method: "put"
        """
        LOGGER.debug('--> Trying to create a file. fp:%s, fname:%s' % (fp, fname))
        return self.put(fp, fname=fname)


    def crud_read(self, fid, fname=''):
        """  READ of CRUD(R). Alias to method: "get"
        """
        LOGGER.debug('--> Trying to read a file. fid: %s, fname:%s' % (fid, fname))
        return self.get(fid, fname=fname)


    def crud_update(self, fp, fid, fname=''):
        """ UPDATE of CRUD(U). Alias to method: "put" but giving parameter: @fid
        """
        LOGGER.info('--> Trying to update a file@fid:%s, fname: %s' % (fid, fname))
        return self.put(fp, fid=fid, fname=fname)

    def crud_delete(self, fid, fname=''):
        """ DELETE of CRUD(U). Alias to method: "put" but giving parameter: @fid
        """
        LOGGER.info('--> Trying to delete a file@fid:%s, fname: %s' % (fid, fname))
        return self.delete(fid=fid, fname=fname)



    ## -----------------------------------------------------------
    ##    weedfs operation: CRUD ends
    ## -----------------------------------------------------------


    def create_multiple(self, fp_array):
        ''' create/save multiple files '''
        pass


    def cp(self, src_fid, dst_fid, src_fname=''):
        """ cp src_fid dst_fid

        replace file@dst_fid with file@src_fid
        """
        try:
            src_file_rsp = self.crud_read(src_fid, fname=src_fname, just_url=False)
            fp = StringIO.StringIO(src_file_rsp.content)
            LOGGER.debug('Updating file: dst_fid: %s, src_fid: %s, src_fname: %s,  fp: %s' % (dst_fid, src_fid, src_fname, fp))
            return self.crud_update(fp, dst_fid, src_fname)
        except Exception as e:
            err_msg = 'Could not Updating file: dst_fid: %s, src_fid: %s, src_fname: %s. e: %s' % (dst_fid, src_fid, src_fname, e)
            LOGGER.error(err_msg)
            return None


    def __repr__(self):
        return '<WeedOperation: @master(%s:%d)>' % (self.master.host, self.master.port)



