import pytest
from catan.models import *
from django.contrib.auth.models import User
from mixer.backend.django import mixer


@pytest.mark.django_db
class TestModels:
    def test_card(self):
        user1 = mixer.blend(User, username='Nico', password='minombrenico')
        player1 = mixer.blend(Player, username=user1, colour='Rojo',
                              development_cards=1, resources_cards=2)
        card = mixer.blend(Card, player=player1, card_name='monopoly')
        resource = mixer.blend(Resource, resource_name='wool', owner=player1)
        assert card.card_name == 'monopoly'
        assert resource.resource_name == 'wool'
        assert card.player == player1
        assert player1.username == user1

    def test__str__(self):
        user1 = mixer.blend(User, username='Nico', password='minombrenico')
        player1 = mixer.blend(Player, username=user1, colour='Rojo',
                              development_cards=1, resources_cards=2)
        assert str(player1) == str(player1.username)
        card = mixer.blend(Card, player=player1, card_name='monopoly')
        assert str(card) == card.card_name
        resource = mixer.blend(Resource, resource_name='wool', owner=player1)
        assert str(resource) == resource.resource_name