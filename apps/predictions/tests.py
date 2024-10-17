from django.test import TestCase
from .models import YourModelName

class YourModelTestCase(TestCase):
    def setUp(self):
        YourModelName.objects.create(field1='value1', field2='value2')

    def test_model_creation(self):
        obj = YourModelName.objects.get(field1='value1')
        self.assertEqual(obj.field2, 'value2')
