![test](https://github.com/darkdarkfruit/python-weed/workflows/Python%20package/badge.svg)
[![Build Status](https://travis-ci.com/darkdarkfruit/python-weed.svg?branch=master)](https://travis-ci.com/darkdarkfruit/python-weed)
# python-weed

## What is it?
A python module for seaweedfs(https://github.com/chrislusf/seaweedfs.git)
(Old name is: weed-fs (https://code.google.com/p/weed-fs/)).


## Python version
* python3.7+ 
* Note: For old python2.7 version, use the branch: `v0.2.3-suited-for-python2.7` or use tag: `python2.7`(or `v0.2.3`) of master
* Note: We always refer python to python3.7+(also, pip to pip3) in the doc as python2 has been deprecated.
* Info: 
    * python3.6+ supports F-Strings: https://www.python.org/dev/peps/pep-0498/
    * python3.7 supports dataclass

## Install(pip means pip3)
> pip install python-weed

Or if you want the latest version:
> pip install https://github.com/darkdarkfruit/python-weed/archive/master.zip

## Wiki
[wiki](https://github.com/darkdarkfruit/python-weed/wiki)

## Examples
look at the test files:
[test_weed.py](./test/test_weed.py)

## How to test?
```shell script
# Set up seaweedfs env
# Download weedfs(https://github.com/chrislusf/seaweedfs.git) binary and install it. (eg: v2.21)
> wget --quiet https://github.com/chrislusf/seaweedfs/releases/download/2.21/linux_amd64.tar.gz
# Start weedfs servers: master server, volume server, filer server.
> weed master             # start master server in terminal 1, listens on port:9333 by default. 
> weed volume -port=27000 # start volume server in terminal 2, listens on 27000
> weed filer -port=27100  # start filer server in terminal 3, listens on 27100

# start testing python-weed.
> pip install pytest
> pytest .

```
    
## Build
```shell script
python sdist    
# or using make
make sdist    
```

## Async support?
Not yet. (todo: integrate httpx: https://github.com/encode/httpx)


## Short introduction to seaweedfs
SeaWeedFs is a simple and highly scalable distributed file system. There are two
objectives:

* to store billions of files!
* to serve the files fast! 

Instead of supporting full POSIX file system semantics, Weed-FS choose to
implement only a key-file mapping. Similar to the word "NoSQL", you can call it
as "NoFS".  see detail in (https://code.google.com/p/weed-fs/)

And this is a python module for seaweedfs.


## Sample log by using ipython(ipython3.9)
```jupyterpython
    #----------------------------------------------------------- 
    In [1]: from weed.master import WeedMaster
    
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

    In [5]: master.lookup('4')
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
    #----------------------------------------------------------- 



    #----------------------------------------------------------- 
    def omit_printing_content(d):
        ''' not showing large content on content '''
        for k,v in d.items():
            _v = v
            if k == 'content' and v and len(v) > 10:
                _v = v[:10] + '...(comment: size: %d, only show: 10). ' % len(v)
            print(k,_v)

    from weed import operation
    wo = operation.WeedOperation()
    
    # put
    wor = wo.put('1.txt')
    print(wor)
    
    # get
    wor = wo.get(wor.fid)
    def omit_printing_content(d):
        for k,v in d.items():
            _v = v
            if k == 'content' and v and len(v) > 10:
                _v = v[:10] + '...(comment: size: %d, only show: 10). ' % len(v)
            print(k,_v)
    omit_printing_content(wor)
    
    # delete
    wor = wo.delete(wor.fid)
    print(wor)
    #----------------------------------------------------------- 
    

    #----------------------------------------------------------- 
    # crud aliases
    wop = operation.WeedOperation()
    #
    # create
    wor = wop.crud_create('1.txt')
    print(wor)
    
    # read
    wor = wop.crud_read(wor.fid)
    omit_printing_content(wor)
    
    # update
    wor = wop.crud_update('1.jpg', wor.fid)
    print(wor)
    wor = wop.crud_get(wor.fid)
    wor = wop.crud_read(wor.fid)
    omit_printing_content(wor)
    
    # delete
    wor = wop.delete(wor.fid)
    print(wor)
    #----------------------------------------------------------- 


    #----------------------------------------------------------- 
    # filer
    from weed import filer
    wf = filer.WeedFiler()
    
    # put
    f = wf.put('1.txt')
    f = wf.put('1.txt', '/helloworld/')
    print(f)
    
    # get
    f_get = wf.get('/helloworld/1.txt')
    print(f_get)
    omit_printing_content(f_get)
    
    # delete
    f_delete = wf.delete('/helloworld/1.txt')
    print(f_delete)
    #----------------------------------------------------------- 
```