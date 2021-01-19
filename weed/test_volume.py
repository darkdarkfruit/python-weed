#!/usr/bin/env python3

# import sys
# if '.' not in sys.path:
#    sys.path.append('.')
from weed.volume import WeedVolume


def test_get_status():
    volume = WeedVolume()
    assert volume.get_status()
