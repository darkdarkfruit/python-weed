version 0.1.4 released @Tue Apr 22 03:10:41 UTC 2014
changelog:
    Modify "method: get" of WeedOperation. Change default Parameter
    "just_url" to False and add Parameter "just_content"(defaults to
    True).

    So,
      when you do "get" by default, you will get file content as normally expected;

      set "just_url" to True you will get an object of WeedResponse
      whose "property: fid_full_url" can serve as a full url for
      backend servers like nginx, ...;

      set "just_content" to True will just return the file's content
      else will return a full object of requests.Response(includes all
      info, like content-type, headers, ...)


VERSION 0.1.0 released @Wed Apr  9 04:10:05 UTC 2014
changelog:
    add put/get/rm, create/read/update/delete operations




version 0.0.1 released @Tue Aug  6 14:20:42 UTC 2013
changelog:
  the basic version done.
