import pytest
from django.urls import reverse, resolve


class TestUrls:
    def test_PlayerActions_url(self):
        path = reverse('PlayerActions', kwargs={'pk': 1})
        assert resolve(path).view_name == 'PlayerActions'
