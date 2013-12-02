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

'''

from urlparse import urlparse, urlunparse, ParseResult

__all__ = ['WeedMaster', 'WeedVolume']

import os
import json
import requests

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


    def get_assign_key(self):
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
            print('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result


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
            print('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result

    def get_volume(self, fid):
        lookup_dict = self.lookup(fid)
        if 'locations' in lookup_dict:
            locations_list = lookup_dict['locations']
        else:
            return None

        # create a url from the parts and parse it to get to the hostname and port
        url_parts = ParseResult(scheme='http', netloc='%s' % locations_list[0]['publicUrl'], path='', params='', query='', fragment='')
        volume_url = urlunparse(url_parts)
        #volume_url = 'http://' + locations_list[0]['publicUrl']
        url = urlparse(volume_url)

        volume = WeedVolume(host=url.hostname, port=url.port)
        return volume

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
            print('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
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
            print('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
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
            print('Could not get status of this volume: %s. Exception is: %s' % (self.url_status, e))
            result = None
        return result

    def put_file(self, absolute_file_path, fid):
        url_parts = ParseResult(scheme='http', netloc='%s:%s' % (self.host,int(self.port)), path='%s' %(fid), params='', query='', fragment='')
        url = urlunparse(url_parts)
        print url
        headers = {'content-type': 'text/xml'}
        files = {'file': (os.path.basename(absolute_file_path), open(absolute_file_path, 'rb'))}
        try:
            r = requests.post(url, files=files);
        except Exception as e:
            print('Could not post file. Exception is: %s' % e)
            return None

        # weed-fs returns a 200 but the content may contain an error
        result = json.loads(r.content)
        if r.status_code == 200:
            print r.status_code
            if 'error' in result:
                print result['error']
            else:
                print result

        return result

    def get_file(self,fid):
        url_parts = ParseResult(scheme='http', netloc='%s:%s' % (self.host,int(self.port)), path='%s' %(fid), params='', query='', fragment='')
        url = urlunparse(url_parts)
        print url

        try:
            r = requests.get(url);
        except Exception as e:
            print('Could not get file. Exception is: %s' % e)

        if r.status_code == 200:
            return r.content
        elif r.status_code == 404:
            print 'file with fid %s not found' % fid
            return None
        else:
            return None

    def delete_file(self,fid):
        url_parts = ParseResult(scheme='http', netloc='%s:%s' % (self.host,int(self.port)), path='%s' %(fid), params='', query='', fragment='')
        url = urlunparse(url_parts)
        print url

        try:
            r = requests.delete(url);
        except Exception as e:
            print('Could not delete file. Exception is: %s' % e)

        return r.content

    def __repr__(self):
        return '<WeedVolume: %s:%s>' % (self.host, self.port)

