from django.test import TestCase, RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from catan.models import *
from catan.views.room_views import RoomList, RoomDetail
from catan.dices import *
from aux.generateBoard import *
from rest_framework.test import force_authenticate
from rest_framework_simplejwt.tokens import AccessToken
import pytest
import json


@pytest.mark.django_db
class TestView(TestCase):

    def setUp(self):
        self.username = 'test_user'
        self.email = 'test_user@example.com'
        self.user = User.objects.create_user(self.username, self.email)
        self.token = AccessToken()

    def test_listEmptyRoomAuthenticated(self):
        path = reverse('list_rooms')
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomList.as_view()
        response = view(request)
        response.render()
        assert response.status_code == 200
#        assert len(json.loads(response.content)) == 0

    def test_listRoomAuthenticated(self):
        path = reverse('list_rooms')
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user, token=self.token)
        room_1 = mixer.blend('catan.Room')
        room_2 = mixer.blend('catan.Room')
        view = RoomList.as_view()
        response = view(request)
        response.render()
        assert response.status_code == 200
#        assert len(json.loads(response.content)) == 2

    def test_listRoomNotAuthenticated(self):
        path = reverse('list_rooms')
        request = RequestFactory().get(path)
        room_1 = mixer.blend('catan.Room')
        view = RoomList.as_view()
        response = view(request)
        response.render()
        assert response.status_code == 401

    def test_viewRoom(self):
        room_1 = mixer.blend('catan.Room')
        path = reverse('join_room', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        response.render()
        assert response.status_code == 200

    def test_addtoManyPlayers(self):
        owner = mixer.blend(User, username="owner_test",
                            password="hola1234")
        player1 = mixer.blend(User, username="player_test1",
                              password="hola1234")
        player2 = mixer.blend(User, username="player_test2",
                              password="hola1234")
        player3 = mixer.blend(User, username="player_test3",
                              password="hola1234")
        room = mixer.blend('catan.Room', name="Test Room", max_players=4,
                           owner=owner)
        room.players.add(player1)
        room.players.add(player2)
        room.players.add(player3)
        path = reverse('join_room', kwargs={'pk': 1})
        request = RequestFactory().put(path)
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        response.render()
        assert len(room.players.all()) == 3
        assert response.status_code == 400

    def test_addPlayersInexistentRoom(self):
        path = reverse('join_room', kwargs={'pk': 1})
        request = RequestFactory().put(path)
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        response.render()
        assert response.status_code == 404

    def test_addPlayers(self):
        owner = mixer.blend(User, username="owner_test", password="hola1234")
        board = mixer.blend(Board, name="test_board")
        room = mixer.blend('catan.Room', name="Test Room", max_players=4,
                           owner=owner, board_id=board.id)
        path = reverse('join_room', kwargs={'pk': 1})
        request = RequestFactory().put(path)
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        response.render()
        assert room.players.filter(
            username=self.user.username).exists() is True
        assert response.status_code == 204

    def test_createRoomSuccess(self):
        user = User.objects.create_user(username='Nico', password='hola1234')
        board = Board.objects.create(name='Board 1')
        path = reverse('list_rooms')
        data = {'name': 'room1', 'owner': user.username,
                'players': [], 'board_id': board.id}
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomList.as_view()
        response = view(request)
        assert response.status_code == 201

    def test_createRoomWhitoutData(self):
        user = User.objects.create_user(username='Nico', password='hola1234')
        board = Board.objects.create(name='Board 1')
        path = reverse('list_rooms')
        data = {}
        request = RequestFactory().post(path, data,
                                        content_type='application/json')
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomList.as_view()
        response = view(request)
        assert response.status_code == 500

    def test_startGame(self):
        user1 = User.objects.create_user(username='user1', password='hola1234')
        user2 = User.objects.create_user(username='user2', password='hola1234')
        user3 = User.objects.create_user(username='user3', password='hola1234')
        user4 = User.objects.create_user(username='user4', password='hola1234')
        generateHexesPositions()
        generateVertexPositions()
        generateBoard("Board 1")
        room = Room.objects.create(
            name='Room1', owner=user1, board_id=1)
        room.players.add(user1)
        room.players.add(user2)
        room.players.add(user3)
        room.players.add(user4)
        path = reverse('join_room', kwargs={'pk': 1})
        request = RequestFactory().patch(path,
                                         content_type='application/json')
        force_authenticate(request, user=user1, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        assert response.status_code == 204

    def test_startGameWithoutAllPlayers(self):
        user1 = User.objects.create_user(username='user1', password='hola1234')
        user2 = User.objects.create_user(username='user2', password='hola1234')
        user3 = User.objects.create_user(username='user3', password='hola1234')
        board = Board.objects.create(name='Board 1')
        hexe_position = HexePosition.objects.create(level=1, index=2)
        hexe = Hexe.objects.create(board=board, terrain='desert',
                                   position=hexe_position)

        room = Room.objects.create(
            name='Room1', owner=user1, board_id=board.id)

        room.players.add(user2)
        room.players.add(user3)

        path = reverse('join_room', kwargs={'pk': 1})

        data = {}

        request = RequestFactory().patch(path, data,
                                         content_type='application/json')
        force_authenticate(request, user=self.user, token=self.token)
        view = RoomDetail.as_view()
        response = view(request, pk=1)
        assert response.status_code == 400

    def test_deleteRoom(self):
        user = User.objects.create_user(username='user1', password='hola1234')
        board = Board.objects.create(name='Board 1')
        room = Room.objects.create(name="Room 1", owner=user,
                                   board_id=board.id)
        path = reverse('join_room', kwargs={'pk': 1})

        request = RequestFactory().delete(path)

        force_authenticate(request, user=user, token=self.token)

        view = RoomDetail.as_view()
        response = view(request, pk=1)
        assert response.status_code == 204
        assert Room.objects.filter(id=1).exists() is False

    def test_deleteRoomNotOwner(self):
        user = User.objects.create_user(username='user1', password='hola1234')
        board = Board.objects.create(name='Board 1')
        room = Room.objects.create(name="Room 1", owner=user,
                                   board_id=board.id)
        path = reverse('join_room', kwargs={'pk': 1})

        request = RequestFactory().delete(path)

        force_authenticate(request, user=self.user, token=self.token)

        view = RoomDetail.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {
            "detail": "only the room's owner can delete it"}
        assert Room.objects.filter(id=1).exists() is True

    def test_deleteRoomHasStarted(self):
        user = User.objects.create_user(username='user1', password='hola1234')
        board = Board.objects.create(name='Board 1')
        room = Room.objects.create(name="Room 1", owner=user,
                                   board_id=board.id,
                                   game_has_started=True)
        path = reverse('join_room', kwargs={'pk': 1})

        request = RequestFactory().delete(path)

        force_authenticate(request, user=user, token=self.token)

        view = RoomDetail.as_view()
        response = view(request, pk=1)
        assert response.status_code == 403
        assert response.data == {
            "detail": "Can't delete the room once the game has started"}
        assert Room.objects.filter(id=1).exists() is True
