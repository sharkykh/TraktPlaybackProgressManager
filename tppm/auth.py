# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os.path


def save(path, data):
    with open(path, 'w') as data_file:
        json.dump(data, data_file, sort_keys=True,
                  indent=2, separators=(',', ': '))


def load(path):
    if not os.path.isfile(path):
        return False

    with open(path) as data_file:
        return json.load(data_file)
