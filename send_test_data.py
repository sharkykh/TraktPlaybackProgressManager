# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from tppm import Application

from trakt import Trakt


def send_test_data(main_app):
    with Trakt.configuration.oauth.from_response(main_app.authorization):
        Trakt['scrobble'].pause(movie={'ids': {'tmdb': 118340}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5761493}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5951173}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5950264}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5966778}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5940102}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 6636942}})

    print('Test data sent.')


def main():
    root = Application()
    if not root._check_auth():
        print('Authentication required.')
        return

    send_test_data(root)


if __name__ == '__main__':
    main()
