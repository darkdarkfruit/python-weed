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
configuration of python-weed
"""

import logging

# -----------------------------------------------------------
# log settings.

g_logger = logging.getLogger("python-weed")


def set_logger_level(logger, logging_level=logging.DEBUG):
    """ set logger level """
    logger.setLevel(logging_level)


# for production mode, you might set it to logging.WARNNING
# set_logger_level(g_logger, logging.WARNING)
def set_global_logger_level(logging_level=logging.DEBUG):
    return set_logger_level(g_logger, logging_level)


def silent_global_logger():
    """ silent the global logger """
    return set_global_logger_level(logging.CRITICAL)


# set_global_logger_level(logging.WARNING)
set_global_logger_level(logging.WARNING)  # for release
# set_global_logger_level(logging.DEBUG) # for development


# ## if we have tornado installed, we can use its pritty-print log
# try:
#     import tornado.options
#
#     tornado.options.parse_command_line()  # use log of tornado
# except Exception as _:
#     pass

# -----------------------------------------------------------


# caches volume_id to speed up lookup performance since volume_id will not change frequently
#  default is 60 seconds
g_volume_cache_duration_in_seconds = 60


def set_volume_cache_duration_in_seconds(seconds):
    global g_volume_cache_duration_in_seconds
    g_volume_cache_duration_in_seconds = seconds
