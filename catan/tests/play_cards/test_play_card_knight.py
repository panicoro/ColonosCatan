from django.test import TestCase, RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from catan.models import *
from catan.views.players_views import PlayerActions, PlayerInfo
from catan.views.game_views import GameInfo
from aux.generateBoard import *
from rest_framework.test import force_authenticate
from rest_framework_simplejwt.tokens import AccessToken
import pytest


@pytest.mark.django_db
class TestViews(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.email = 'test_user@example.com'
        self.user = mixer.blend(User, username=self.username, email=self.email)
        self.token = AccessToken()
        self.expected_payload = {
            'payload': [
                {'players': ['user2'], 'position': {'level': 0, 'index': 0}},
                {'players': [], 'position': {'level': 1, 'index': 1}},
                {'players': [], 'position': {'level': 1, 'index': 2}},
                {'players': [], 'position': {'level': 1, 'index': 3}},
                {'players': ['user3'], 'position': {'level': 1, 'index': 4}},
                {'players': ['user2', 'user3'], 'position': {'level': 1,
                                                             'index': 5}},
                {'players': ['user2'], 'position': {'level': 2, 'index': 0}},
                {'players': [], 'position': {'level': 2, 'index': 1}},
                {'players': [], 'position': {'level': 2, 'index': 2}},
                {'players': [], 'position': {'level': 2, 'index': 3}},
                {'players': [], 'position': {'level': 2, 'index': 4}},
                {'players': [], 'position': {'level': 2, 'index': 5}},
                {'players': [], 'position': {'level': 2, 'index': 6}},
                {'players': [], 'position': {'level': 2, 'index': 7}},
                {'players': [], 'position': {'level': 2, 'index': 8}},
                {'players': [], 'position': {'level': 2, 'index': 9}},
                {'players': ['user3'], 'position': {'level': 2, 'index': 10}},
                {'players': ['user2'], 'position': {'level': 2, 'index': 11}}],
            'type': 'play_knight_card'
        }

    def createGame(self):
        self.user1 = mixer.blend(User, username='user1', password='1234')
        self.user2 = mixer.blend(User, username='user2', password='1234')
        self.user3 = mixer.blend(User, username='user3', password='1234')
        self.user4 = mixer.blend(User, username='user4', password='1234')
        self.board = mixer.blend('catan.Board', name='Board1')
        self.room = mixer.blend('catan.Room', name='Room1', owner=self.user1,
                                board_id=1)
        self.hexe = mixer.blend('catan.Hexe', terrain='ore', token=2,
                                board=self.board, level=1, index=0)
        self.game = mixer.blend('catan.Game', name='Game1', board=self.board,
                                robber=self.hexe)
        self.player1 = mixer.blend(Player, username=self.user1,
                                   game=self.game, colour='yellow')
        self.player2 = mixer.blend(Player, username=self.user2,
                                   game=self.game, colour='green')
        self.player3 = mixer.blend(Player, username=self.user3,
                                   game=self.game, colour='blue')
        self.player4 = mixer.blend(Player, username=self.user4,
                                   game=self.game, colour='red')

    def get_game_info(self, pk):
        path_game = reverse('GameInfo', kwargs={'pk': pk})
        request_game = RequestFactory().get(path_game)
        force_authenticate(request_game, user=self.user1, token=self.token)
        view_game = GameInfo.as_view()
        return view_game(request_game, pk=pk)

    def get_player_info(self, pk):
        path_player = reverse('PlayerInfo', kwargs={'pk': pk})
        request_player = RequestFactory().get(path_player)
        force_authenticate(request_player, user=self.user1, token=self.token)
        view_player = PlayerInfo.as_view()
        return view_player(request_player, pk=pk)

    def test_actions_not_in_turn(self):
        self.createGame()
        self.current_turn = mixer.blend(
            'catan.Current_Turn', user=self.user2, game=self.game)
        card = Card.objects.create(owner=self.player1,
                                   game=self.game,
                                   name='knight')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': ''
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {"detail": "Not in turn"}

    def test_position_invalid(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game,
            dices1=4, dices2=3)
        card = Card.objects.create(owner=self.player1,
                                   game=self.game,
                                   name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 6,
                        'index': 10
                    },
                    'player': ''
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {
            "detail": "There is no hexe in that position"}

    def test_move_robber_with_out_buildings(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)
        card = mixer.blend('catan.Card', owner=self.player1,
                           game=self.game,
                           name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                     'position': {
                        'level': 2,
                        'index': 10
                      },
                     'player': ''
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response.status_code == 204
        assert response_player.data['resources'] == []
        assert response_player.data['cards'] == []
        assert response_game.data['players'][0]['development_cards'] == 0
        assert response_game.data['robber'] == {'level': 2, 'index': 10}

    def test_move_robber_one_building(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)

        building_1 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player2, level=2, index=26)
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=11)
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': 'user2'
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response.status_code == 204
        assert response_player.data['resources'] == []
        assert response_player.data['cards'] == ['knight']
        assert response_game.data['players'][0]['development_cards'] == 1
        assert response_game.data['robber'] == {'level': 2, 'index': 10}
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='ore')
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {'detail':
                                 'You must enter a new hexe position'}
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response_player.data['resources'] == []
        assert response_player.data['cards'] == ['knight']
        assert response_game.data['players'][0]['development_cards'] == 1
        assert response_game.data['robber'] == {'level': 2, 'index': 10}
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 11
                    },
                    'player': 'user2'
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response_player.data['resources'] == ['ore']
        assert response_player.data['cards'] == []
        assert response_game.data['players'][0]['development_cards'] == 0
        assert response_game.data['robber'] == {'level': 2, 'index': 11}
        assert response.status_code == 204

    def test_move_robber_more_buildings(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)
        building1 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player2, level=2, index=26)
        building2 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player3, level=1, index=15)
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='ore')
        resources = Resource.objects.create(
            owner=self.player3, game=self.game, name='lumber')
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='brick')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': 'user2'
                }
                }

        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        gain_ore = 'ore' in response_player.data['resources']
        gain_brick = 'brick' in response_player.data['resources']
        assert gain_ore or gain_brick
        assert response_player.data['cards'] == []
        assert response_game.data['players'][0]['development_cards'] == 0
        assert response_game.data['robber'] == {'level': 2, 'index': 10}
        assert response.status_code == 204

    def test_player_without_buildings(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)
        building1 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player2, level=2, index=26)
        building2 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player3, level=1, index=15)
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='ore')
        resources = Resource.objects.create(
            owner=self.player3, game=self.game, name='lumber')
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='brick')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': 'user4'
                }
                }

        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response_player.data['resources'] == []
        assert response_player.data['cards'] == ['knight']
        assert response_game.data['players'][0]['development_cards'] == 1
        assert response_game.data['robber'] == {'level': 1, 'index': 0}
        assert response.status_code == 403
        assert response.data == {
            "detail": "You have to choose a player that has buildings"}

    def test_player_himself(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)
        building1 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player2, level=2, index=26)
        building2 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player3, level=1, index=15)
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='ore')
        resources = Resource.objects.create(
            owner=self.player3, game=self.game, name='lumber')
        resources = Resource.objects.create(
            owner=self.player2, game=self.game, name='brick')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': 'user1'
                }
                }

        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        response_game = self.get_game_info(1)
        response_player = self.get_player_info(1)
        assert response_player.data['resources'] == []
        assert response_player.data['cards'] == ['knight']
        assert response_game.data['players'][0]['development_cards'] == 1
        assert response_game.data['robber'] == {'level': 1, 'index': 0}
        assert response.status_code == 403
        assert response.data == {
            "detail": "You can't choose yourself"}

    def test_no_have_knight_cards(self):
        self.createGame()
        self.current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game)
        mixer.blend('catan.Hexe', terrain='ore', token=2,
                    board=self.board, level=2, index=10)
        building1 = Building.objects.create(
            name="settlement", game=self.game,
            owner=self.player2, level=2, index=26)
        path = reverse('PlayerActions', kwargs={'pk': 1})
        data = {'type': 'play_knight_card',
                'payload': {
                    'position': {
                        'level': 2,
                        'index': 10
                    },
                    'player': ''
                }
                }
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {"detail": "You have not knight cards"}

    def test_get_robber_positions(self):
        self.createGame()
        current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game,
            dices1=6, dices2=3, game_stage='FULL_PLAY')
        Building.objects.create(game=self.game,
                                owner=self.player1,
                                name='city',
                                level=2, index=5)
        Building.objects.create(game=self.game,
                                owner=self.player2,
                                name='city',
                                level=1, index=17)
        Building.objects.create(game=self.game,
                                owner=self.player2,
                                name='settlement',
                                level=0, index=0)
        Building.objects.create(game=self.game,
                                owner=self.player3,
                                name='settlement',
                                level=1, index=15)
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        self.expected_payload['type'] = 'play_knight_card'
        assert self.expected_payload in response.data
        assert response.status_code == 200

    def test_get_robber_positions_no_buildings(self):
        self.createGame()
        current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game,
            dices1=6, dices2=3, game_stage='FULL_PLAY')
        Card.objects.create(owner=self.player1,
                            game=self.game,
                            name='knight')
        path = reverse('PlayerActions', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        for item in self.expected_payload['payload']:
            item['players'] = []
        assert self.expected_payload in response.data
        assert {'type': 'end_turn'} in response.data
        assert response.status_code == 200

    def test_get_robber_positions_no_card(self):
        self.createGame()
        current_turn = mixer.blend(
            Current_Turn, user=self.user1, game=self.game,
            dices1=1, dices2=3, game_stage='FULL_PLAY')
        Building.objects.create(game=self.game,
                                owner=self.player1,
                                name='city',
                                level=2, index=5)
        Building.objects.create(game=self.game,
                                owner=self.player2,
                                name='city',
                                level=1, index=17)
        path = reverse('PlayerActions', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user1, token=self.token)
        view = PlayerActions.as_view()
        response = view(request, pk=1)
        assert response.data == [{"type": "end_turn"}]
        assert response.status_code == 200
