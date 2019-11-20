from django.test import TestCase, RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from catan.models import *
from catan.views.players_views import PlayerActions
from catan.views.game_views import GameInfo
from rest_framework.test import force_authenticate
from rest_framework_simplejwt.tokens import AccessToken
import pytest
import json


@pytest.mark.django_db
class TestView(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("user1")
        self.user2 = User.objects.create_user("user2")
        self.user3 = User.objects.create_user("user3")
        self.user4 = User.objects.create_user("user4")
        self.token = AccessToken()
        self.hexe_position = HexePosition.objects.create(level=2, index=11)
        self.board = Board.objects.create(name='Colonos')
        self.game = Game.objects.create(name='Juego1', board=self.board,
                                        robber=self.hexe_position)
        self.player1 = Player.objects.create(turn=1, username=self.user1,
                                             colour='red', game=self.game)
        self.player2 = Player.objects.create(turn=2, username=self.user2,
                                             colour='blue', game=self.game)
        self.player3 = Player.objects.create(turn=3, username=self.user3,
                                             colour='yellow', game=self.game)
        self.player4 = Player.objects.create(turn=4, username=self.user4,
                                             colour='green', game=self.game)
        self.turn = Current_Turn.objects.create(game=self.game,
                                                user=self.user1,
                                                dices1=3,
                                                dices2=3)

    def test_endTurn(self):
        """
        A test to see the change of users in turn according
        to the user requesting the end of their shift
        """
        self.turn.dices1 = 2
        self.turn.dices2 = 2
        self.turn.save()
        url = reverse('PlayerActions', kwargs={'pk': 1})
        data = {"type": "end_turn",
                "payload": None}
        request = RequestFactory().post(url, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view_actions = PlayerActions.as_view()
        response = view_actions(request, pk=1)
        response.render()
        assert response.status_code == 204
        url = reverse('GameInfo', kwargs={'pk': 1})
        request = RequestFactory().get(url)
        force_authenticate(request, user=self.user1, token=self.token)
        view_game = GameInfo.as_view()
        response = view_game(request, pk=1)
        response.render()
        assert response.data['current_turn']['user'] == "user2"

    def test_endTurn4(self):
        """
        A test to see the change of users in turn according
        to the user requesting the end of their shift
        """
        self.turn.dices1 = 2
        self.turn.dices2 = 2
        self.turn.user = self.user4
        self.turn.save()
        url = reverse('PlayerActions', kwargs={'pk': 1})
        data = {"type": "end_turn",
                "payload": None}
        request = RequestFactory().post(url, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user4, token=self.token)
        view_actions = PlayerActions.as_view()
        response = view_actions(request, pk=1)
        response.render()
        assert response.status_code == 204
        url = reverse('GameInfo', kwargs={'pk': 1})
        request = RequestFactory().get(url)
        force_authenticate(request, user=self.user4, token=self.token)
        view_game = GameInfo.as_view()
        response = view_game(request, pk=1)
        response.render()
        assert response.data['current_turn']['user'] == "user1"

    def test_endTurn_NotInTurn(self):
        """
        If the user requesting the end of his shift is not in
        his turn, then he must indicate prohibited
        """
        url = reverse('PlayerActions', kwargs={'pk': 1})
        data = {"type": "end_turn",
                "payload": None}
        request = RequestFactory().post(url, data,
                                        content_type='application/json')
        # Set the user to make the post as self.user2,
        # but the user in turn is user1
        force_authenticate(request, user=self.user2, token=self.token)
        view_actions = PlayerActions.as_view()
        response = view_actions(request, pk=1)
        response.render()
        assert response.status_code == 403
        assert response.data['detail'] == 'Not in turn'
        url = reverse('GameInfo', kwargs={'pk': 1})
        request = RequestFactory().get(url)
        force_authenticate(request, user=self.user2, token=self.token)
        view_game = GameInfo.as_view()
        response = view_game(request, pk=1)
        response.render()
        assert response.data['current_turn']['user'] == 'user1'

    def test_endTurnNotMoveRobber(self):
        """
        A test to see the change of users in turn according
        to the user requesting the end of their shift
        """
        self.turn.dices1 = 3
        self.turn.dices2 = 4
        self.turn.save()
        url = reverse('PlayerActions', kwargs={'pk': 1})
        data = {"type": "end_turn",
                "payload": None}
        request = RequestFactory().post(url, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view_actions = PlayerActions.as_view()
        response = view_actions(request, pk=1)
        response.render()
        assert response.status_code == 403
        assert response.data == {"detail": "you have to move the thief"}
