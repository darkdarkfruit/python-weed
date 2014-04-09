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
python interface of weed-fs.
(https://code.google.com/p/weed-fs/)

note:
    ensure weed master-server and at least one volume-server are up
    default:
        master-server: 127.0.0.1:9333
        volume-server: 127.0.0.1:8080


'''


__all__ = ['WeedMaster', 'WeedVolume']


import json
import random
import StringIO
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
        self['full_url'] = urlparse.urljoin('http://', self['url'])
        self['full_publicUrl'] = urlparse.urljoin('http://', self['publicUrl'])
        self['fid_full_url'] = urlparse.urljoin(self['full_url'], self['fid'])
        self['fid_full_publicUrl'] = urlparse.urljoin(self['full_publicUrl'], self['fid'])
        for k, v in self.items():
            setattr(self, k, v)


    def update_full_urls(self):
        ''' update "full_url" and "full_publicUrl" '''
        self['full_url'] = urlparse.urljoin('http://', self['url'])
        self['full_publicUrl'] = urlparse.urljoin('http://', self['publicUrl'])
        self['fid_full_url'] = urlparse.urljoin(self['full_url'], self['fid'])
        self['fid_full_publicUrl'] = urlparse.urljoin(self['full_publicUrl'], self['fid'])



class WeedMaster(object):
    """
      Weed-FS's master server(relative to volume-server)
    """

    def __init__(self, host='127.0.0.1', port=9333):
        """

        Arguments:
        - `host`:
        - `port`:
        """
        self.host = host
        self.port = port
        self.url_base = 'http://' + self.host + ':' + str(self.port)
        self.url_assign = self.url_base + '/dir/assign'
        self.url_lookup = self.url_base + '/dir/lookup'
        self.url_vacuum = self.url_base + '/vol/vacuum'
        self.url_status = self.url_base + '/dir/status'


    def acquire_assign_info(self):
        """
        acquire an assign key from master-server.
        assign_key is in json format like below:
        -----------
        {"count":1,"fid":"3,01637037d6","url":"127.0.0.1:8080","publicUrl":"localhost:8080"}
        -----------

        Arguments:
        - `self`:
        """
        result = None
        try:
            r = requests.get(self.url_assign)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s'
                         % (self.url_status, e))
            result = None
        return result


    def acquire_new_assign_key(self, count=1):
        """
        get a new avalable new volume-file-location from from weed-master by getting a new-assign-key
        Arguments:
        - `self`:

        assign_key is in json format like below:
        -----------
        {"count":1,"fid":"3,01637037d6","url":"127.0.0.1:8080","publicUrl":"localhost:8080"}
        -----------

        return a tuple(dst_file_fid, dst_volume_url) like below:
        ----------
        (dst_file_fid, http://{volume-url})
        (3,20392030920, http://127.0.0.1:8080)
        ----------

        """
        assign_key_url = self.url_assign + '?count=' + str(count)
        dst_volume_url = None
        wak = WeedAssignKeyExtended()
        try:
            LOGGER.debug('Getting new dst_volume_url with master-assign-key-url: %s' % assign_key_url)
            r = requests.get(assign_key_url)
            key_dict = json.loads(r.content)

            wak.update(key_dict)
            wak.update_full_urls()

            LOGGER.info('Successfuly got dst_volume_url: %s' % dst_volume_url)
        except Exception as e:
            LOGGER.error('Could not get new assign key from the assign url: %s. Exception is: %s'
                         % (assign_key_url, e))
        return wak



    def lookup(self, volume_id):
        """
        lookup the urls of a volume
        return a json like below:
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

        Arguments:
        - `self`:
        """
        result = None
        try:
            r = requests.get(self.url_lookup + '?volumeId=%s' % volume_id)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


    def vacuum(self):
        """
        Force Garbage Collection

        If your system has many deletions, the deleted file's disk space will not be synchronously re-claimed. There is a background job to check volume disk usage. If empty space is more than the threshold, default to 0.3, the vacuum job will make the volume readonly, create a new volume with only existing files, and switch on the new volume. If you are impatient or doing some testing, vacuum the unused spaces this way.

        > curl "http://localhost:9333/vol/vacuum"
        > curl "http://localhost:9333/vol/vacuum?garbageThreshold=0.4"

        return a json of refreshed status like below:
        -----------
        {
          "Topology": {
            "DataCenters": [
              {
                "Free": 93,
                "Max": 100,
                "Racks": [
                  {
                    "DataNodes": [
                      {
                        "Free": 93,
                        "Max": 100,
                        "PublicUrl": "127.0.0.1:8080",
                        "Url": "127.0.0.1:8080",
                        "Volumes": 7
                      }
                    ],
                    "Free": 93,
                    "Max": 100
                  }
                ]
              }
            ],
            "Free": 93,
            "Max": 100,
            "layouts": [
              {
                "replication": "000",
                "writables": [
                  2,
                  3,
                  5,
                  6,
                  7,
                  1,
                  4
                ]
              }
            ]
          },
          "Version": "0.37"
        }

                {
                  "locations": [
                    {
                      "publicUrl": "localhost:8080",
                      "url": "localhost:8080"
                    }
                  ]
                }
        -----------

        Arguments:
        - `self`:
        """
        result = None
        try:
            r = requests.get(self.url_vacuum)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


    def get_status(self):
        """
        get status of this volume

        Arguments:
        - `self`:
        """
        result = None
        try:
            r = requests.get(self.url_status)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


    def __repr__(self):
        return '<WeedMaster: %s:%s>' % (self.host, self.port)



class WeedVolume(object):
    """
      Weed-FS's volume server(relative to master-server)
    """

    def __init__(self, host='127.0.0.1', port=8080):
        """

        Arguments:
        - `host`:
        - `port`:
        """
        self.host = host
        self.port = port
        self.url_base = 'http://' + self.host + ':' + str(self.port)
        self.url_status = self.url_base + '/status'


    def get_status(self):
        """
        get status of this volume

        Arguments:
        - `self`:
        """
        r = requests.get(self.url_status)
        try:
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


    def __repr__(self):
        return '<WeedVolume: %s:%s>' % (self.host, self.port)




class WeedOperation(object):
    """
    do CRUD operations to weed-fs.
    Currently, implement it with /* tornado and */ requests. Maybe mongrel2 + brubeck is better?

    """

    def __init__(self, master_host='127.0.0.1', master_port='9333'):
        self.master = WeedMaster(master_host, master_port)


    def get_fid_full_url(self, fid):
        """
        get operatable full_url by fid.
        lookup info returns:
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
        """
        result = None
        volume_id = fid.split(',')[0]
        full_url = ''
        try:
            r = self.master.lookup(volume_id)
            # _url = WEEDFS_MASTER_URL + '/dir/lookup?volumeId=%s' % volume_id
            # LOGGER.debug('lookup volume by url: %s' % _url)
            # r = requests.get(_url)
            result = json.loads(r.content)
            locations = result['locations']

            # choose a random location
            location = locations[random.randint(0, len(locations) - 1)]
            full_url = 'http://%s/%s' % (location['url'], fid)
        except Exception as e:
            LOGGER.error('Could not get volume location of this fid: %s. Exception is: %s' % (fid, e))
            result = None
        return full_url


    @staticmethod
    def save_file_to_weed(self, fp, fid_full_url, fname=''):
        """
        save fp(file-pointer, file-description) to remote weed
        """
        tmp_uploading_file_name = fname or 'a.unknown'
        rsp = requests.post(fid_full_url, files={'file' : (tmp_uploading_file_name, fp)})
        # LOGGER.debug(rsp.request.headers)
        if not rsp.json().has_key('size'): # post new file fails
            err_msg = 'Could not save file on weed-fs with fid_full_url: %s' % (fid_full_url)
            LOGGER.error(err_msg)
            return (False, err_msg)
        data = {
            'fid_full_url' : fid_full_url,
            'fname' : fname,
            'storage_size' : rsp.json().get('size', 0),
            }
        return (True, data)


    ## -----------------------------------------------------------
    ##    weedfs operation: CRUD starts
    ## -----------------------------------------------------------
    def create(self, fp, fname=''):
        """
        create a file in weed-fs with @fid
        """
        fid_full_url = 'wrong_url'
        try:
            wak = self.master.acquire_new_assign_key()
            LOGGER.debug('Creating file: fp: %s, fname: %s, fid_full_url: %s'
                         % (fp, fname, fid_full_url))
            return WeedOperation.save_file_to_weed(fp, wak.fid_full_url, fname)
        except Exception as e:
            err_msg = 'Could not create file: fp: %s, fname: %s, fid_full_url: %s, e: %s' % (fp, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None


    def read(self, fid, fname='', just_url=True):
        """
        read/get a file from weed-fs with @fid.

        @just_url:
          True -> just return fid_full_url (web-servers/browsers like nginx, chrome can get resource by this url)
          False -> return a http response of requests(package requests).
        """
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Reading file(just_url:%s): fid: %s, fname: %s, fid_full_url: %s' % (just_url, fid, fname, fid_full_url))
            if just_url:
                return fid_full_url
            else:
                rsp = requests.get(fid_full_url)
                return rsp
        except Exception as e:
            err_msg = 'Could not read file(just_url:%s): fid: %s, fname: %s, fid_full_url: %s, e: %s' % (just_url, fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None


    def update(self, fp, fid, fname=''):
        """
        update a file in weed-fs with @fid
        """
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Updating file: fp: %s, fname: %s, fid_full_url: %s' % (fp, fname, fid_full_url))
            return WeedOperation.save_file_to_weed(fp, fid_full_url, fname)
        except Exception as e:
            err_msg = 'Could not Updating file: fp: %s, fname: %s, fid_full_url: %s, e: %s' % (fp, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return None


    def delete(self, fid, fname=''):
        """
        delete a file in weed-fs with @fid
        """
        fid_full_url = 'wrong_url'
        try:
            fid_full_url = self.get_fid_full_url(fid)
            LOGGER.debug('Deleting file: fid: %s, fname: %s, fid_full_url: %s' % (fid, fname, fid_full_url))

            r = requests.delete(fid_full_url)
            if r.json().has_key('size'):
                return True
        except Exception as e:
            err_msg = 'Deleting file: fid: %s, fname: %s, fid_full_url: %s, e: %s' % (fid, fname, fid_full_url, e)
            LOGGER.error(err_msg)
            return False
        return False
    ## -----------------------------------------------------------
    ##    weedfs operation: CRUD ends
    ## -----------------------------------------------------------


    def create_multiple(self, fp_array):
        ''' create/save multiple files '''
        # try:
        #     wak = self.master.acquire_new_assign_key(count)
        #     waks.append(wak)
        #     fnames.append(fname)
        #     for i in range(count - 1):
        #         _w = {}
        #         _w.update(wak)
        #         seq = '_%d' % (i + 1)
        #         _w.update({'fid' : wak.fid + seq})
        #         _w.update_full_urls()
        #         waks.append(_w)
        #         fname.append(fname + seq)

        #     for (i, w) in sequence(waks):
        #         return WeedOperation.save_file_to_weed(fp, waks[i], fnames[i])

        pass


    def update_by_fid(self, dst_fid, src_fid, src_fname=''):
        """
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



