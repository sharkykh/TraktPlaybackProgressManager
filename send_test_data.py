# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import random

from tppm import Application

from trakt import Trakt


def gen_progress():
    return random.uniform(0.0, 100.0)


def send_test_data():
    Trakt['scrobble'].pause(movie={'ids': {'tmdb': 404368}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5761493}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5951173}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5950264}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5966778}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5966780}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5940102}}, progress=gen_progress())
    Trakt['scrobble'].pause(episode={'ids': {'tvdb': 6636942}}, progress=gen_progress())

    print('Test data sent.')


def main():
    root = Application()
    if not root.authorization:
        print('Authentication required.')
        return

    send_test_data()


if __name__ == '__main__':
    main()
