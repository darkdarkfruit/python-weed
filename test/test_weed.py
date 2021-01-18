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
        volume-server: 127.0.0.1:27000
        filer-server : 127.0.0.1:27100

'''
import gzip
import io
import urllib
from urllib import parse

from env_test_env import *


import weed
print(weed)
from weed import master
from weed.conf import *
from weed.util import *
from weed.master import *
from weed.volume import *
from weed.operation import *
from weed.filer import WeedFiler

set_global_logger_level(logging.DEBUG)

WEED_MASTER_IP = '127.0.0.1'
WEED_MASTER_PORT = 9333


def test_WeedMaster():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.acquire_assign_info()
    assert isinstance(assign_key_dict, dict)
    assert 'fid' in assign_key_dict
    assert int(assign_key_dict['fid'].replace(',', ''), 16) > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert 'locations' in lookup_dict
    locations_list = lookup_dict['locations']
    assert 'url' in locations_list[0]
    assert 'publicUrl' in locations_list[0]

    # vacuum
    vacuum_dict = master.vacuum()
    assert isinstance(vacuum_dict, dict)
    assert 'Topology' in vacuum_dict


    # status
    status_dict = master.get_status()
    assert isinstance(status_dict, dict)
    assert 'Topology' in status_dict


def test_WeedMaster2():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    wak = master.acquire_new_assign_key(10)
    assert isinstance(wak, dict)
    assert 'fid' in wak

    fid = wak.fid

    fids = [fid] + [fid + '_' + str(i + 1) for i in range(10)]
    locations = []
    for i in fids:
        l = master.lookup(i)
        assert 'locations' in l
        locations.append(l)

    for i, l in enumerate(locations):
        if i < (len(locations) - 1):
            assert locations[i] == locations[i + 1]



def test_WeedVolume():
    volume = WeedVolume()
    assert volume.__repr__()

    # status
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert 'Version' in status_dict
    assert 'Volumes' in status_dict


def test_WeedAssignKey():
    wak = WeedAssignKey()
    assert wak
    assert wak.__repr__()


def test_WeedAssignKeyExtended():
    wak = WeedAssignKeyExtended()
    assert wak
    assert wak.__repr__()


def test_WeedOperationResponse():
    wor = WeedOperationResponse()
    assert wor
    assert wor.__repr__()


def test_volume_put_get_delete_file():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.get_assign_key()
    assert isinstance(assign_key_dict, dict)
    assert 'fid' in assign_key_dict
    assert int(assign_key_dict['fid'].replace(',', ''), 16) > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert 'locations' in lookup_dict
    locations_list = lookup_dict['locations']
    assert 'url' in locations_list[0]
    assert 'publicUrl' in locations_list[0]

    volume_url = 'http://' + locations_list[0]['publicUrl']
    url = parse.urlparse(volume_url)

    #volume = WeedVolume(host=url.hostname, port=url.port)
    volume = master.get_volume(fid)
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert 'Version' in status_dict
    assert 'Volumes' in status_dict
    assert isinstance(status_dict['Volumes'], list)

    # file_to_post = './test_file_to_post_to_weed.xml'
    file_to_update = 'test_file_to_post_to_weed.xml'
    file_to_post = os.path.join(TEST_PATH, file_to_update)

    with open(file_to_post, 'wb') as tmp_file:
        # tmp_file.write(b"nonsense " * 1024 * 256)
        tmp_file.write(b"nonsense " * 8)
    put_result = volume.put_file(os.path.abspath(file_to_post),fid)
    assert not 'error' in put_result
    assert 'size' in put_result

    data = volume.get_file(fid)
    assert data
    # print data
    with open(file_to_post, 'rb') as fd:
        file_data = fd.read()
    assert data == file_data

    delete_result = volume.delete_file(fid)
    assert delete_result
    assert not b'error' in delete_result
    assert b'size' in delete_result


def test_accquire_new_fid():
    op = WeedOperation()
    fids = op.acquire_new_fids()
    assert isinstance(fids, (tuple, list))
    assert ',' in fids[0]
    count = 5
    fids = op.acquire_new_fids(count)
    for i in range(count):
        assert ',' in fids[i]


def test_put_a_file_with_fid():
    op = WeedOperation()
    fid = op.acquire_new_fids()[0]
    fname = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, fname)
    assert op.put(open(fpath, 'r'), fid, fname)



def test_put_file():
    # test put_file in weed.util
    op = WeedOperation()
    fid = ''
    fname = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, fname)
    master = WeedMaster()
    fid_full_url = master.acquire_new_assign_key()['fid_full_url']
    print(('test_weed.py, fid_full_url: %s, fpath: %s' % (fid_full_url, fpath)))
    with open(fpath, 'rb') as f:
        LOGGER.info('fp position: %d' % f.tell())
        LOGGER.info('fp info: length: %d' % len(f.read()))
        f.seek(0)

        rsp = put_file(f, fid_full_url, fname)
        assert rsp
        assert rsp.status == 'success'
        assert 'url' in rsp and rsp.url
        assert rsp.storage_size > 0
        fid = os.path.split(fid_full_url)[1]

    # read
    content = op.crud_read(fid, fname).content
    with open(fpath, 'rb') as _:
        original_content = _.read()
    assert content == original_content



def test_file_operations():
    op = WeedOperation()
    assert op.__repr__()

    # create
    fid = ''
    fname = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, fname)
    with open(fpath, 'rb') as f:
        rsp = op.crud_create(f, fname)
        assert rsp
        assert 'fid' in rsp
        fid = rsp['fid']
        print(fid)
        assert len(fid) > 1
        assert os.path.split(op.get_fid_full_url(fid))[1] == fid
        assert rsp['fid'].replace(',', '') > '01'
        assert rsp['url']
        assert rsp['storage_size'] > 0

    # test exists
    assert op.exists(fid)
    assert op.exists(fid + 'wrong_fid') == False
    assert op.exists('wrong_fid') == False
    assert op.exists(fid.replace(',', '/')) == False


    # read
    content = op.get(fid, fname).content
    content2 = op.get_content(fid, fname)
    assert content == content2
    with open(fpath, 'rb') as f:
        original_content = f.read()
    assert content == original_content

    # update
    file_to_update = 'test_file_to_post_to_weed.xml'
    fpath = os.path.join(TEST_PATH, file_to_update)
    with open(fpath, 'rb+') as tmp_file:
        tmp_file.write(b"testdata " * 1024 * 256)
        tmp_file.seek(0)
        rsp = op.crud_update(tmp_file, fid)
        assert rsp
        assert 'fid' in rsp
        fid_2 = rsp['fid']
        assert fid_2 == fid
        assert rsp['fid'].replace(',', '') > '01'
        assert rsp['url']
        assert rsp['storage_size'] > 0

    # delete
    rsp = op.crud_delete(fid)
    assert rsp.storage_size > 0
    rsp = op.crud_delete('3,20323023') # delete an unexisted file, should return False
    assert rsp.storage_size == 0


def test_WeedFiler():
    wf = WeedFiler()
    assert wf.host == '127.0.0.1'
    assert wf.port == 27100
    assert wf.uri == '127.0.0.1:27100'
    assert wf.url == 'http://127.0.0.1:27100'

    d = '/test/'
    new_d = '/test/new_dir/'

    # put f1
    f1_content = 'hello, how are you'
    f1 = io.StringIO(f1_content)
    f1_path = d + 'test.txt'
    assert wf.put(f1, f1_path) == f1_path

    # mkdir
    assert wf.mkdir(new_d)

    # put f2
    f2_content = 'hello, how are you?'
    f2 = io.StringIO(f2_content)
    f2_path = new_d + 'hello.txt'
    assert wf.put(f2, f2_path) == f2_path

    # list
    j = wf.list(new_d)
    assert isinstance(j, dict)
    # print(j)

    if 'Directory' in j:
        assert j['Directory'] == '/test/new_dir/'
    if 'Path' in j:
        assert j['Path'] == '/test/new_dir'
    assert j['Entries']
    entries = j['Entries']
    fnames = []
    for f in entries:
        if 'FullPath' in f:
            fnames.append(f['FullPath'].split('/')[-1])

    assert 'hello.txt' in fnames

    # get f1
    wf_get = wf.get(f1_path)
    assert int(wf_get['content_length']) > 0
    if 'gzip' in wf_get['content_type']:
        content_gz = wf_get['content']
        content = gzip.open(io.StringIO(content_gz)).read()
        assert content == f1_content
    elif 'text' in wf_get['content_type']:
        assert wf_get['content'] == str.encode(f1_content)
    else:
        pass

    # delete f1, f2
    assert wf.delete(f1_path)
    assert wf.delete(f2_path)



if __name__ == '__main__':
    test_WeedMaster()
    test_WeedVolume()
    test_file_operations()
    test_volume_put_get_delete_file()
