from main import Application
# noinspection PyPackageRequirements
from trakt import Trakt


def send_test_data(main_app):
    if not main_app.authorization:
        print 'Authentication required.'
        return False

    with Trakt.configuration.oauth.from_response(main_app.authorization):
        Trakt['scrobble'].pause(movie={'ids': {'tmdb': 118340}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5761493}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5951173}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5950264}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5966778}})
        Trakt['scrobble'].pause(episode={'ids': {'tvdb': 5940102}})
    print 'test data sent'


def main():
    root = Application()
    if root._check_auth():
        send_test_data(root)
    else:
        print 'Authentication required.'

if __name__ == '__main__':
    main()
