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
jsend test
==========
You should have py.test installed first.
pip install -U pytest

Then, run
>> py.test  test_jsend.py


note:
    ensure weed master-server and at least one volume-server are up
    default:
        master-server: localhost:9333
        volume-server: localhost:27000
        filer-server : localhost:27100

"""
# try:
#     print(f'__name__: {__name__}')
#     print(f'__file__: {__file__}')
#     import sys
#     import os
#     print(f'os.curdir: {os.curdir}')
#     print(f'os.curdir: {os.path.abspath(os.curdir)}')
#
#     current_dir = __file__.rsplit('/', 1)[0]
#     parent_dir = current_dir.rsplit('/', 1)[0]
#     print(f'current_dir: {current_dir}')
#     print(f'parent_dir: {parent_dir}')
#     if current_dir not in sys.path:
#         sys.path.append(current_dir)
#     if parent_dir not in sys.path:
#         sys.path.append(parent_dir)
#     if '.' not in sys.path:
#         sys.path.append('.')
#     wp = parent_dir + '/weed'
#     if wp not in sys.path:
#         sys.path.append(wp)
#     print(f'sys.path is: \n {sys.path}\n')
#     # import os
#     # sys.exit(1)
#
# except Exception as e:
#     print(e)

import gzip
import io
from urllib import parse

from env_test_env import *

try:
    import weed
except Exception as e:
    print(f'Could not import weed, err: {e}')
    import traceback

    traceback.print_exc()

# try:
#     import python_weed
# except Exception as e:
#     print(f'Could not import python_weed, err: {e}')
#     import traceback
#     traceback.print_exc()


# import weed
# print(weed)
from weed.conf import *
from weed.util import *
from weed.master import *
from weed.volume import *
from weed.operation import *
from weed.filer import WeedFiler

set_global_logger_level(logging.DEBUG)

WEED_MASTER_IP = 'localhost'
WEED_MASTER_PORT = 9333


# noinspection DuplicatedCode
def test_weed_master():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.acquire_assign_info()
    assert isinstance(assign_key_dict, dict)
    assert 'fid' in assign_key_dict
    assert int(assign_key_dict['fid'].replace(',', ''), 16) > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]
    assert len(volume_id) >= 1

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


def test_weed_master_2():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    wak = master.acquire_new_assign_key(10)
    assert isinstance(wak, dict)
    assert 'fid' in wak

    fid = wak['fid']

    fids = [fid] + [fid + '_' + str(i + 1) for i in range(10)]
    locations = []
    for i in fids:
        locations_dict = master.lookup(i)
        assert 'locations' in locations_dict
        locations.append(locations_dict['locations'])

    for i, l in enumerate(locations):
        if i < (len(l) - 1):
            assert l[i] == l[i + 1]


def test_weed_volume():
    volume = WeedVolume()
    assert volume.__repr__()

    # status
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert 'Version' in status_dict
    assert 'Volumes' in status_dict


def test_weed_assign_key():
    wak = WeedAssignKey()
    assert wak
    assert wak.__repr__()


def test_weed_assign_key_extended():
    wak = WeedAssignKeyExtended()
    assert wak
    assert wak.__repr__()


def test_weed_operation_response():
    wor = WeedOperationResponse()
    assert wor.status == Status.FAILED  # init is FAILED
    assert wor.__repr__()


# noinspection DuplicatedCode
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
    assert len(volume_id) >= 1

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert 'locations' in lookup_dict
    locations_list = lookup_dict['locations']
    assert 'url' in locations_list[0]
    assert 'publicUrl' in locations_list[0]

    volume_url = 'http://' + locations_list[0]['publicUrl']
    url = parse.urlparse(volume_url)
    assert url is not None

    # volume = WeedVolume(host=url_base.hostname, port=url_base.port)
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
    put_result = volume.put_file(os.path.abspath(file_to_post), fid)
    assert 'error' not in put_result
    assert 'size' in put_result

    data = volume.get_file(fid)
    assert data
    # print data
    with open(file_to_post, 'rb') as fd:
        file_data = fd.read()
    assert data == file_data

    delete_result = volume.delete_file(fid)
    assert delete_result
    assert b'error' not in delete_result
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
    file_name = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, file_name)
    assert op.put(open(fpath, 'rb'), fid, file_name)


def test_put_file():
    # test put_file in weed.util
    op = WeedOperation()
    # fid = ''
    file_name = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, file_name)
    master = WeedMaster()
    fid_full_url = master.acquire_new_assign_key()['fid_full_url']
    print(('test_weed.py, fid_full_url: %s, fpath: %s' % (fid_full_url, fpath)))
    with open(fpath, 'rb') as f:
        g_logger.info('fp position: %d' % f.tell())
        g_logger.info('fp info: length: %d' % len(f.read()))
        f.seek(0)

        rsp = put_file(f, fid_full_url, file_name)
        assert rsp.ok()
        assert rsp.storage_size > 0
        fid = os.path.split(fid_full_url)[1]

    # read
    wor = op.crud_read(fid, file_name)
    assert wor
    content = wor.content
    assert len(content) > 3
    with open(fpath, 'rb') as _:
        original_content = _.read()
    assert content == original_content


def test_file_operations():
    op = WeedOperation()
    assert op.__repr__()

    # create
    # fid = ''
    file_name = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, file_name)
    with open(fpath, 'rb') as f:
        rsp = op.crud_create(f, file_name)
        assert rsp.ok()
        assert len(rsp.fid) > 3
        fid = rsp.fid
        print(fid)
        assert len(fid) > 1
        assert os.path.split(op.get_fid_full_url(fid))[1] == fid
        assert rsp.fid.replace(',', '') > '01'
        assert rsp.url
        assert rsp.storage_size > 0

    # test exists
    assert op.exists(fid)
    assert op.exists(fid + 'wrong_fid') is False
    assert op.exists('wrong_fid') is False
    assert op.exists(fid.replace(',', '/')) is False

    # read
    content = op.get(fid, file_name).content
    content2 = op.get_content(fid, file_name)
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
        fid_2 = rsp.fid
        assert fid_2 == fid
        assert rsp.fid.replace(',', '') > '01'
        assert rsp.url
        assert rsp.storage_size > 0

    # delete
    rsp = op.crud_delete(fid)
    assert rsp.storage_size > 0
    rsp = op.crud_delete('3,20323023')  # delete an unexisted file, should return False
    assert rsp.storage_size == 0


def test_weed_filer():
    wf = WeedFiler()
    assert wf.uri == 'localhost:27100'
    assert wf.url_base == 'http://localhost:27100'

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
    file_names = []
    for f in entries:
        if 'FullPath' in f:
            file_names.append(f['FullPath'].split('/')[-1])

    assert 'hello.txt' in file_names

    # get f1
    wf_get = wf.get(f1_path)
    assert int(wf_get['content_length']) > 0
    if 'gzip' in wf_get['content_type']:
        content_gz = wf_get['content']
        content = gzip.open(io.BytesIO(content_gz)).read()
        assert content == f1_content
    elif 'text' in wf_get['content_type']:
        assert wf_get['content'] == str.encode(f1_content)
    else:
        pass

    # delete f1, f2
    assert wf.delete(f1_path)
    assert wf.delete(f2_path)


if __name__ == '__main__':
    test_weed_master()
    test_weed_volume()
    test_file_operations()
    test_volume_put_get_delete_file()
