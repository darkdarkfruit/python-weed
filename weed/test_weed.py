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
jsend test
==========
You should have py.test installed first.
pip install -U pytest

Then, run
>> py.test  test_jsend.py


note:
    ensure weed master-server and at least one volume-server are up
    default:
        master-server: 127.0.0.1:9333
        volume-server: 127.0.0.1:8080

'''

from weed import *



def test_WeedMaster():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.acquire_assign_info()
    assert isinstance(assign_key_dict, dict)
    assert assign_key_dict.has_key('fid')
    assert assign_key_dict['fid'].replace(',', '') > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert lookup_dict.has_key('locations')
    locations_list = lookup_dict['locations']
    assert locations_list[0].has_key('url')
    assert locations_list[0].has_key('publicUrl')


    # vacuum
    vacuum_dict = master.vacuum()
    assert isinstance(vacuum_dict, dict)
    assert vacuum_dict.has_key('Topology')


    # status
    status_dict = master.get_status()
    assert isinstance(status_dict, dict)
    assert status_dict.has_key('Topology')


def test_WeedVolume():
    volume = WeedVolume()
    assert volume.__repr__()

    # status
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert status_dict.has_key('Version')
    assert status_dict.has_key('Volumes')
    assert isinstance(status_dict['Volumes'], list)





if __name__ == '__main__':
    test_WeedMaster()
    test_WeedVolume()
