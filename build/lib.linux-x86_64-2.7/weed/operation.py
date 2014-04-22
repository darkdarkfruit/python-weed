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
from conf import LOGGER
from util import *

from master import *
from volume import *



class WeedOperation(object):
    """ DO CRUD operations to weed-fs.

    You just need to supply weed master. The master will find a volume automaticlly.
    Currently, implement it with /* tornado and */ requests. Maybe mongrel2 + brubeck is better?

    """

    def __init__(self, master_host='127.0.0.1', master_port=9333):
        self.master = WeedMaster(master_host, master_port)




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



    def get_fid_full_url(self, fid):
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
        result = None
        volume_id = fid.split(',')[0]
        full_url = ''
        try:
            r = self.master.lookup(volume_id)
            locations = r['locations']

            # choose a random location
            location = locations[random.randint(0, len(locations) - 1)]
            full_url = 'http://%s/%s' % (location['url'], fid)
        except Exception as e:
            LOGGER.error('Could not get volume location of this fid: %s. Exception is: %s' % (fid, e))
            result = None
        return full_url




    ## -----------------------------------------------------------
    ##    weedfs operation: CRUD starts
    ## -----------------------------------------------------------
    def put(self, fp, fid=None, fname=''):
        """  put a file to weed-fs.

        if @fid provided, put @fp with @fid;
        if @fid not provided, generate a new fid for it.

        return a WeedOperationResponse instance
        """
        LOGGER.info('|--> Putting file@fid:%s, fname:%s' % (fid, fname) )
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

        try:
            LOGGER.info('Putting file with fid: %s, fid_full_url:%s for file: fp: %s, fname: %s'
                         % (_fid, fid_full_url, fp, fname))
            data = put_file(fp, fid_full_url, fname)
            LOGGER.info('%s' % data)
            data.fid = _fid
            return data
        except Exception as e:
            err_msg = 'Could not put file. fp: "%s", fname: "%s", fid_full_url: "%s", e: %s' % (fp, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None


    def get(self, fid, fname='', just_url=True):
        """
        read/get a file from weed-fs with @fid.

        @just_url:
          True -> just return fid_full_url (web-servers/browsers like nginx, chrome can get resource by this url)
          False -> return a http response of requests(package requests).

        return a WeedOperationResponse instance
        """
        LOGGER.debug('|--> Getting file. fid: %s, fname:%s, just_url: %s' % (fid, fname, just_url) )

        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Reading file(just_url:%s): fid: %s, fname: %s, fid_full_url: %s' % (just_url, fid, fname, fid_full_url))
            if just_url:
                _r = WeedOperationResponse()
                _r.fid = fid
                _r.fid_full_url = fid_full_url
                _r.fname = fname
                _r.storage_size = -1
                return _r
            else:
                rsp = requests.get(fid_full_url)
                return rsp
        except Exception as e:
            err_msg = 'Could not read file(just_url:%s): fid: %s, fname: %s, fid_full_url: %s, e: %s' % (just_url, fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None


    def rm(self, fid, fname=''):
        """ remove a file in weed-fs with @fid.

        if storage == 0, then @fid in weedfs is not exist.

        return a WeedOperationResponse instance
        """
        LOGGER.info('|--> Removing file@%s, fname: %s' % (fid, fname) )
        _r = WeedOperationResponse()
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Deleting file: fid: %s, fname: %s, fid_full_url: %s' % (fid, fname, fid_full_url))

            r = requests.delete(fid_full_url)
            _j = r.json()

            _r.fid = fid
            _r.fid_full_url = fid_full_url
            _r.fname = fname

            if _j.has_key('size'):
                _r.storage_size = _j['size']
                if _r.storage_size == 0:
                    LOGGER.error('Error: fid@%s is not exist.' % fid)
        except Exception as e:
            err_msg = 'Deleting file: fid: %s, fname: %s, fid_full_url: %s, e: %s' % (fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
        return _r


    def create(self, fp, fname=''):
        """
        create a file in weed-fs with @fid

        return a WeedOperationResponse instance
        """
        LOGGER.debug('--> Trying to create a file. fp:%s, fname:%s' % (fp, fname) )
        return self.put(fp, None, fname=fname)


    def read(self, fid, fname='', just_url=True):
        """
        read/get a file from weed-fs with @fid.

        @just_url:
          True -> just return fid_full_url (web-servers/browsers like nginx, chrome can get resource by this url)
          False -> return a http response of requests(package requests).

        return a WeedOperationResponse instance
        """
        LOGGER.debug('--> Trying to read a file. fid: %s, fname:%s, just_url: %s' % (fid, fname, just_url) )
        return self.get(fid, fname=fname, just_url=just_url)


    def update(self, fp, fid, fname=''):
        """
        update a file in weed-fs with @fid

        return a WeedOperationResponse instance
        """
        LOGGER.info('--> Trying to update a file@fid:%s, fname: %s' % (fid, fname) )

        return self.put(fp, fid=fid, fname=fname)


    def delete(self, fid, fname=''):
        """
        delete a file in weed-fs with @fid. return a integer representing the file storage in weedfs.

        return a WeedOperationResponse instance
        """
        LOGGER.info('--> Trying to delete file@%s, fname: %s' % (fid, fname) )
        return self.rm(fid, fname=fname)

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
            src_file_rsp = self.read(src_fid, fname=src_fname, just_url=False)
            fp = StringIO.StringIO(src_file_rsp.content)
            LOGGER.debug('Updating file: dst_fid: %s, src_fid: %s, src_fname: %s,  fp: %s' % (dst_fid, src_fid, src_fname, fp))
            return self.update(fp, dst_fid, src_fname)
        except Exception as e:
            err_msg = 'Could not Updating file: dst_fid: %s, src_fid: %s, src_fname: %s. e: %s' % (dst_fid, src_fid, src_fname, e)
            LOGGER.error(err_msg)
            return None


    def __repr__(self):
        return '<WeedOperation: @master(%s:%d)>' % (self.master.host, self.master.port)



