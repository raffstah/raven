# -*- coding: utf-8 -*-

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import raven
from raven.utils import get_versions


class GetVersionsTest(TestCase):
    def test_exact_match(self):
        versions = get_versions(['raven'])
        self.assertEquals(versions.get('raven'), raven.VERSION)

    def test_parent_match(self):
        versions = get_versions(['raven.contrib.django'])
        self.assertEquals(versions.get('raven'), raven.VERSION)
