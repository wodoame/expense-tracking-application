from django.test import SimpleTestCase
from django.conf import settings

class SettingsTest(SimpleTestCase):
    def test_debug_is_false(self):
        self.assertFalse(settings.DEBUG, 'Debug must be false in production')
        
    