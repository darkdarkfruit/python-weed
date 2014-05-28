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

from urlparse import urljoin, urlunparse, ParseResult

__all__ = ['WeedMaster']


import time
import json
import urlparse
import requests
from conf import *
from util import *

from volume import WeedVolume


class WeedMaster(object):
    """
    Weed-FS's master server (relative to volume-server)
    """

    def __init__(self, host='127.0.0.1', port=9333, prefetch_volumeIds=False):
        """

        Arguments:
        - `host`:
        - `port`:
        - `prefetch_volumeIds`: if True, prefech volumeIds to cache: self.volumes_cache
        """
        self.host = host
        self.port = port
        self.url_base_parts = ParseResult(scheme='http', netloc='%s:%d' % (host, port),
                                          path='', params='', query='', fragment='')
        self.url_base = urlunparse(self.url_base_parts)
        self.url_assign = urljoin(self.url_base, '/dir/assign')
        self.url_lookup = urljoin(self.url_base, '/dir/lookup')
        self.url_vacuum = urljoin(self.url_base, '/vol/vacuum')
        self.url_status = urljoin(self.url_base, '/dir/status')

        # volumes usually do not move, so we cache it here for 1 minute.
        self.volumes_cache = {}

        if prefetch_volumeIds:
            LOGGER.info("prefetching volumeIds(['1' : '10'] into cache")
            for i in range(10):
                self.lookup(str(i + 1))


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
        try:
            r = requests.get(self.url_assign)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s'
                         % (self.url_status, e))
            result = None
        return result


    def get_assign_key(self):
        ''' deprecated. Please use acquie_new_assign_key function instead '''
        return self.acquire_assign_info()


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
        assign_key_url = urljoin(self.url_assign, '?count=' + str(count))
        dst_volume_url = None
        wak = WeedAssignKeyExtended()
        try:
            LOGGER.debug('Getting new dst_volume_url with master-assign-key-url: %s' % assign_key_url)
            r = requests.get(assign_key_url)
            key_dict = json.loads(r.content)
            # print(key_dict)
            wak.update(key_dict)
            # print(wak)
            wak.update_full_urls()
            # print(wak)

            LOGGER.info('Successfuly got weed_assign_key(wak): %s' % wak)
        except Exception as e:
            LOGGER.error('Could not get new assign key from the assign url: %s. Exception is: %s'
                         % (assign_key_url, e))
        return wak


    def lookup(self, volume_id_or_fid, cache_duration_in_seconds=VOLUME_CACHE_DURATION_IN_SECONDS):
        """
        lookup the locations of a volume@volume_id_or_fid.
        returns a dict like below if successful else None:
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
        if ',' in volume_id_or_fid:
            _volume_id = volume_id_or_fid.split(',')[0]
        elif '/' in volume_id_or_fid:
            _volume_id = volume_id_or_fid.split('/')[0]
        else:
            _volume_id = volume_id_or_fid
        result = None
        try:
            # LOGGER.warning('id(master): %x, cache should be hit: %s' % (id(self), self.volumes_cache.has_key(_volume_id)))
            # LOGGER.warning('self.volumes_cache: %s' % self.volumes_cache)
            ## try cache first
            if self.volumes_cache.has_key(_volume_id) and (time.time() - self.volumes_cache[_volume_id][1]) <= cache_duration_in_seconds:
                LOGGER.debug('volume_cache(lookup by volume_id) hits')
                return self.volumes_cache[_volume_id][0]
            else:
                r = requests.get(self.url_lookup + '?volumeId=%s' % _volume_id)
                if not r.ok:    # not HTTP-200, like HTTP-404, ...
                    return None
                result = json.loads(r.content)

                ## refresh cache
                self.volumes_cache.update({_volume_id : (result, time.time())})
                # LOGGER.warning('volume_cache(lookup by volume_id) not hit, dst: %s, keys: %s' % (_volume_id, self.volumes_cache.keys())

            # LOGGER.warning('after updating, self.volumes_cache: %s' % self.volumes_cache)

        except Exception as e:
            LOGGER.error("Could not get status of this volume: %s. "
                "Exception is: %s" % (self.url_status, e))
            result = None
        return result


    def get_volume(self, fid):
        ''' get an instance of WeedVolume by @fid'''
        lookup_dict = self.lookup(fid)
        if 'locations' in lookup_dict:
            locations_list = lookup_dict['locations']
        else:
            return None

        url_parts = ParseResult(scheme='http', netloc=locations_list[0]['publicUrl'],
            path='', params='', query='', fragment='')
        volume = WeedVolume(host=url_parts.hostname, port=url_parts.port)
        return volume


    def vacuum(self):
        """
        Force Garbage Collection

        If your system has many deletions, the deleted file's disk space will not be synchronously
        re-claimed. There is a background job to check volume disk usage. If empty space is more
        than the threshold, default to 0.3, the vacuum job will make the volume readonly, create a
        new volume with only existing files, and switch on the new volume. If you are impatient or
        doing some testing, vacuum the unused spaces this way.

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
        try:
            r = requests.get(self.url_vacuum)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error("Could not get status of this volume: %s. "
                "Exception is: %s" % (self.url_status, e))
            result = None
        return result

    def get_status(self):
        """
        get status of this volume

        Arguments:
        - `self`:
        """
        try:
            r = requests.get(self.url_status)
            result = json.loads(r.content)
        except Exception as e:
            LOGGER.error('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


    def __repr__(self):
        return '<WeedMaster: %s:%s>' % (self.host, self.port)

