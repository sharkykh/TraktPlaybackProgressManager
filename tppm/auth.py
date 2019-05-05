# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import json
import os.path


def save(path, data):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        # Must NOT use `json.dump` due to a Python 2 bug:
        # https://stackoverflow.com/a/14870531/7597273
        fh.write(json.dumps(
            data, sort_keys=True, ensure_ascii=False,
            indent=2, separators=(',', ': ')
        ))


def load(path):
    if not os.path.isfile(path):
        return None

    with io.open(path, 'r', encoding='utf-8') as fh:
        try:
            return json.load(fh)
        except ValueError:
            return None


def remove(path):
    if not os.path.isfile(path):
        return False

    try:
        os.remove(path)
    except OSError:
        return False
    return True


class NotAuthenticatedError(Exception):
    pass
