#!/usr/bin/env python
__author__ = 'gicmo'

from setuptools import setup


setup(name             = 'gca',
      version          = 0.1,
      author           = 'Christian Kellner',
      description     = 'Python client for the G-Node Conference Application Suite.',
      author_email     = 'kellner@bio.lmu.de',
      url              = 'https://github.com/G-Node/GCA-Python',
      packages         = ['gca'],
      scripts          = ['gca-client', 'gca-filter', 'gca-lint',
                          'gca-select', 'gca-sort', 'gca-tex'])
