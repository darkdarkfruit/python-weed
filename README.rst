python-weed. What is it?
========================

A python module for weed-fs (https://code.google.com/p/weed-fs/).


Install
=======

    pip install python-weed

Or if you want the latest version:

    pip install https://github.com/rwuerfel/python-weed/archive/master.zip


Test
====

    python setup.py test

note: it may show the warning messages like something below:

"test.pytest.py/_pytest.core:147: UserWarning: Module _pytest was already
imported from test.pytest.py/_pytest, but /usr/local/lib/python2.6/dist-packages
is being added to sys.path"

It does no harm, just ommit it.


Shortely
========

Weed-FS is a simple and highly scalable distributed file system. There are two
objectives:

* to store billions of files!
* to serve the files fast! 

Instead of supporting full POSIX file system semantics, Weed-FS choose to
implement only a key-file mapping. Similar to the word "NoSQL", you can call it
as "NoFS".  see detail in (https://code.google.com/p/weed-fs/)

And this is a python module for weed-fs.

Usage (sample)
===============

::

    In [1]: from weed import *

    In [2]: master = WeedMaster()

    In [3]: master
    Out[3]: <WeedMaster: 127.0.0.1:9333>

    In [4]: master.
    master.get_assign_key  master.lookup          master.url_base        master.url_vacuum      
    master.get_status      master.port            master.url_lookup      master.vacuum          
    master.host            master.url_assign      master.url_status      

    In [4]: master.get_assign_key()
    Out[4]: 
    {u'count': 1,
     u'fid': u'4,024a042190cca9',
     u'publicUrl': u'127.0.0.1:8080',
     u'url': u'127.0.0.1:8080'}

    In [5]: master.lookup(4)
    Out[5]: {u'locations': [{u'publicUrl': u'127.0.0.1:8080', u'url': u'127.0.0.1:8080'}]}

    In [6]: master.get_status()
    Out[6]: 
    {u'Topology': {u'DataCenters': [{u'Free': 93,
        u'Max': 100,
        u'Racks': [{u'DataNodes': [{u'Free': 93,
            u'Max': 100,
            u'PublicUrl': u'127.0.0.1:8080',
            u'Url': u'127.0.0.1:8080',
            u'Volumes': 7}],
          u'Free': 93,
          u'Max': 100}]}],
      u'Free': 93,
      u'Max': 100,
      u'layouts': [{u'replication': u'000', u'writables': [2, 3, 5, 6, 7, 1, 4]}]},
     u'Version': u'0.37'}

    In [7]: volume = master.get_volume()

    In [8]: volume
    Out[8]: <WeedVolume: 127.0.0.1:8080>

    In [9]: volume.get_status()
    Out[9]: 
    {u'Version': u'0.37',
     u'Volumes': [{u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 1,
       u'Id': 1,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 126481,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 0,
       u'Id': 2,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 0,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 2,
       u'Id': 3,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 438228,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 0,
       u'Id': 4,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 0,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 0,
       u'Id': 5,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 0,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 0,
       u'Id': 6,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 0,
       u'Version': 2},
      {u'DeleteCount': 0,
       u'DeletedByteCount': 0,
       u'FileCount': 0,
       u'Id': 7,
       u'ReadOnly': False,
       u'RepType': u'000',
       u'Size': 0,
       u'Version': 2}]}
