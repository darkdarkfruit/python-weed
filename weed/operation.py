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
operations to weedfs.
"""

__all__ = ['WeedOperation']

import io
import random

from weed.master import *
from weed.util import *


class WeedOperation(object):
    """ DO CRUD operations to weed-fs.

    Arguments you need to supply is just weed master.
    The master will find a volume automaticlly.
    Currently, implement it with requests. Maybe *tornado or  *mongrel2 + brubeck* is better?

    """

    def __init__(self, master_url_base='http://localhost:9333', prefetch_volume_ids=False):
        self.master_url_base = master_url_base
        self.master = WeedMaster(url_base=master_url_base, prefetch_volume_ids=prefetch_volume_ids)

    # def get_volume_fid_full_url(self, fid):
    #     ''' (deprecated, use get_fid_full_url instead) return a random fid_full_url of volume by @fid
    #
    #     eg: (randomly choosed from locations)
    #       return:  'http://127.0.0.1:27000/3,1234101234'  or
    #       return:  'http://127.0.0.1:27001/3,1234101234'  or
    #       return:  'http://127.0.0.1:27002/3,1234101234'
    #     '''

    def acquire_new_fids(self, count=1) -> [str]:
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

    def get_fid_full_url(self, fid, use_public_url=False) -> None or str:
        """ return a random fid_full_url of volume by @fid

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
              "url_base": "localhost:8080"
            }
          ]
        }
        -----------

        return something like: 'http://127.0.0.1:8080/3,0230203913'
        """
        volume_id = fid.split(',')[0]
        full_url = None
        try:
            r = self.master.lookup(volume_id)
            locations = r['locations']

            # choose a random location
            location = locations[random.randint(0, len(locations) - 1)]
            if not use_public_url:
                full_url = 'http://%s/%s' % (location['url'], fid)
            else:
                full_url = 'http://%s/%s' % (location['publicUrl'], fid)
        except Exception as e:
            g_logger.error('Could not get volume location of this fid: %s. Exception is: %s' % (fid, e))
        return full_url

    # -----------------------------------------------------------
    #    weedfs operation: get/put/delete, and CRUD-aliases starts
    # -----------------------------------------------------------
    def get(self, fid, file_name='') -> WeedOperationResponse:
        """
        read/get a file from weed-fs with @fid.

        @just_url(default is False):
          if True -> just return an object of WeedOperationResponse(web-servers/browsers like nginx, chrome can get resource by this url_base( WeedOperationResponse.fid_full_url ))
          if False -> return a http response of requests(package requests) if @just_content is False else return file_content

        @just_content(default is True):
          if True -> just return the file's content
          if False -> return a response of requests.Respond object. (eg: You can get content_type of the file being get)

        return a WeedOperationResponse instance
        """
        g_logger.debug('|--> Getting file. fid: %s, file_name:%s' % (fid, file_name))

        fid_full_url = 'wrong_url'
        wor = WeedOperationResponse()
        try:
            fid_full_url = self.get_fid_full_url(fid)
            g_logger.debug('Reading file fid: %s, file_name: %s, fid_full_url: %s' % (fid, file_name, fid_full_url))
            rsp = self.get_http_response(fid_full_url)
            wor.status = Status.SUCCESS
            wor.fid = fid
            wor.url = fid_full_url
            wor.name = file_name
            wor.content = rsp.content
            wor.content_type = rsp.headers.get('content-type')
        except Exception as e:
            err_msg = 'Could not read file fid: %s, file_name: %s, fid_full_url: %s, e: %s' % (
                fid, file_name, fid_full_url, e)
            g_logger.error(err_msg)
            wor.status = Status.FAILED
            wor.message = err_msg

        return wor

    def get_url(self, fid) -> None or str:
        """ return a random fid_full_url of volume by @fid, alias to get_fid_full_url(fid)

        eg: (randomly choosed from locations)
          return:  'http://127.0.0.1:27000/3,1234101234'  or
          return:  'http://127.0.0.1:27001/3,1234101234'  or
          return:  'http://127.0.0.1:27002/3,1234101234'

        return something like: 'http://127.0.0.1:8080/3,0230203913'
        """
        return self.get_fid_full_url(fid)

    @staticmethod
    def get_http_response(fid_full_url) -> requests.Response:
        """ return a "requests.Response" if we want whole info of the http request """
        return requests.get(fid_full_url)

    def get_content(self, fid, file_name='') -> bytes:
        """ return just file's content. use method "get" to get more file's info """
        return self.get(fid, file_name).content

    def put(self, fp, fid=None, file_name='') -> None or WeedOperationResponse:
        """  put a file to weed-fs.

        if @fid provided, put @fp with @fid;
        if @fid not provided, generate a new fid for it.

        return a WeedOperationResponse instance
        """
        g_logger.info('|--> Putting file@fid:%s, file_name:%s' % (fid, file_name))
        fid_full_url = 'wrong_url'
        _fid = fid
        try:
            if not fid:
                wak = self.master.acquire_new_assign_key()
                # print(wak)
                _fid = wak.fid
                g_logger.debug('no fid. accquired new one: "%s"' % _fid)
                fid_full_url = wak.fid_full_url
            else:
                fid_full_url = self.get_fid_full_url(fid)
        except Exception as e:
            err_msg = 'Could not put file. fp: "%s", file_name: "%s", fid_full_url: "%s", e: %s' % (
                fp, file_name, fid_full_url, e)
            g_logger.error(err_msg)
            return None

        wor = WeedOperationResponse()
        is_our_responsibility_to_close_file = False
        if isinstance(fp, str):
            _fp = open(fp, 'rb')
            is_our_responsibility_to_close_file = True
        else:
            _fp = fp

        try:
            g_logger.info('Putting file with fid: %s, fid_full_url:%s for file: fp: %s, file_name: %s'
                          % (_fid, fid_full_url, fp, file_name))
            wor = put_file(_fp, fid_full_url, file_name)
            g_logger.info('%s' % wor)
            wor.fid = _fid
        except Exception as e:
            err_msg = 'Could not put file. fp: "%s", file_name: "%s", fid_full_url: "%s", e: %s' % (
                fp, file_name, fid_full_url, e)
            g_logger.error(err_msg)
            wor.status = Status.FAILED
            wor.message = err_msg

        # close fp if parameter fp is a str
        if is_our_responsibility_to_close_file:
            try:
                _fp.close()
            except Exception as e:
                g_logger.warning('Could not close fp: %s. e: %s' % (_fp, e))

        return wor

    def delete(self, fid, file_name='') -> WeedOperationResponse:
        """ remove a file in weed-fs with @fid.

        if storage == 0, then @fid in weedfs is not exist.

        return a WeedOperationResponse instance
        """
        g_logger.debug('|--> Deleting file@%s, file_name: %s' % (fid, file_name))
        wor = WeedOperationResponse()
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            g_logger.debug('Deleting file: fid: %s, file_name: %s, fid_full_url: %s' % (fid, file_name, fid_full_url))

            r = requests.delete(fid_full_url)
            rsp_json = r.json()

            wor.status = Status.SUCCESS
            wor.fid = fid
            wor.url = fid_full_url
            wor.name = file_name

            if 'size' in rsp_json:
                wor.storage_size = rsp_json['size']
                if wor.storage_size == 0:
                    err_msg = ('Error: fid@%s is not exist.' % fid)
                    wor.status = Status.FAILED
                    wor.message = err_msg
                    g_logger.error(err_msg)
        except Exception as e:
            err_msg = 'Deleting file: fid: %s, file_name: %s, fid_full_url: %s, e: %s' % (
                fid, file_name, fid_full_url, e)
            g_logger.error(err_msg)
            wor.status = Status.FAILED
            wor.message = err_msg
            g_logger.error(err_msg)

        return wor

    def exists(self, fid) -> bool:
        """ detects @fid's existence """
        if ',' not in fid:  # fid should have a volume_id
            return False
        try:
            volume_id = fid.split(',')[0]
        except Exception as e:
            g_logger.error('Invalid fid:"%s". e: %s' % (fid, e))
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
            g_logger.error('Error occurs while requests.head. e: %s' % e)
            return False

    def crud_create(self, fp, file_name='') -> None or WeedOperationResponse:
        """  CREATE of CRUD(C). Alias to method: "put"
        """
        g_logger.debug('--> Trying to create a file. fp:%s, file_name:%s' % (fp, file_name))
        return self.put(fp, file_name=file_name)

    def crud_read(self, fid, file_name='') -> WeedOperationResponse:
        """  READ of CRUD(R). Alias to method: "get"
        """
        g_logger.debug('--> Trying to read a file. fid: %s, file_name:%s' % (fid, file_name))
        return self.get(fid, file_name=file_name)

    def crud_update(self, fp, fid, file_name='') -> None or WeedOperationResponse:
        """ UPDATE of CRUD(U). Alias to method: "put" but giving parameter: @fid
        """
        g_logger.info('--> Trying to update a file@fid:%s, file_name: %s' % (fid, file_name))
        return self.put(fp, fid=fid, file_name=file_name)

    def crud_delete(self, fid, file_name='') -> WeedOperationResponse:
        """ DELETE of CRUD(U). Alias to method: "put" but giving parameter: @fid
        """
        g_logger.info('--> Trying to delete a file@fid:%s, file_name: %s' % (fid, file_name))
        return self.delete(fid=fid, file_name=file_name)

    # -----------------------------------------------------------
    #    weedfs operation: CRUD ends
    # -----------------------------------------------------------

    # def create_multiple(self, fp_array):
    #     ''' create/save multiple files '''
    #     pass

    def cp(self, src_fid, dst_fid, src_file_name='') -> None or WeedOperationResponse:
        """ cp src_fid dst_fid

        replace file@dst_fid with file@src_fid
        """
        try:
            src_file_rsp = self.crud_read(src_fid, file_name=src_file_name)
            fp = io.BytesIO(src_file_rsp.content)
            g_logger.debug(
                'Updating file: dst_fid: %s, src_fid: %s, src_file_name: %s,  fp: %s' % (
                    dst_fid, src_fid, src_file_name, fp))
            return self.crud_update(fp, dst_fid, src_file_name)
        except Exception as e:
            err_msg = 'Could not Updating file: dst_fid: %s, src_fid: %s, src_file_name: %s. e: %s' % (
                dst_fid, src_fid, src_file_name, e)
            g_logger.error(err_msg)
            return None

    def __repr__(self):
        return f'<WeedOperation: @master({self.master_url_base}>'
