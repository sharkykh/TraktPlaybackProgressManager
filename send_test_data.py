# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import random
from time import sleep

from tppm import Application

from trakt import Trakt

TEST_DATA = {
    'movie': [
        {'tmdb': 404368},  # Ralph Breaks the Internet (2018)
    ],
    'episode': [
        {'tvdb': 5951173},  # Tá no Ar: A TV na TV: 4x04 Episode 4
        {'tvdb': 5950264},  # Democracy Now!: 2017x32 Tuesday, February 14, 2017
        {'tvdb': 5966778},  # All In with Chris Hayes: 2017x32 February 14, 2017
        {'tvdb': 5966780},  # All In with Chris Hayes: 2017x33 February 15, 2017
        {'tvdb': 5940102},  # Chicago Fire: 5x13 Trading in Scuttlebutt
        {'tvdb': 6636942},  # Westworld: 2x03 Virtù e Fortuna
    ]
}


def gen_progress():
    return random.uniform(0.0, 100.0)


def send_test_data():
    index = 1
    total = len(TEST_DATA['movie']) + len(TEST_DATA['episode'])
    for category, items in TEST_DATA.items():
        for item in items:
            params = {
                category: {
                    'ids': item
                },
                'progress': gen_progress()
            }
            print('Sending [%d/%d]: %s' % (index, total, item))
            Trakt['scrobble'].pause(**params)
            index += 1

            sleep(0.1)

    print('Test data sent.')


def main():
    root = Application()
    if not root.authorization:
        print('Authentication required.')
        return

    send_test_data()


if __name__ == '__main__':
    main()
