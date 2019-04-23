# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

from .app import Application

def main():
    root = Application()
    root.main()
