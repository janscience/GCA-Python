#!/usr/bin/env python
__author__ = 'gicmo'

from setuptools import setup


setup(name             = 'gca',
      version          = 0.1,
      author           = 'Christian Kellner',
      author_email     = 'kellner@bio.lmu.de',
      packages         = ['gca'],
      scripts          = ['gca-client', 'gca-filter', 'gca-lint',
                          'gca-select', 'gca-sort', 'gca-tex'])