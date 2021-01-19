#!/usr/bin/env python3

# import sys
# if '.' not in sys.path:
#    sys.path.append('.')
import logging

from weed import conf


def test_silent_global_logger():
    conf.silent_global_logger()
    assert conf.g_logger.getEffectiveLevel() == logging.CRITICAL
