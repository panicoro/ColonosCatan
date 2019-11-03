"""
Random Board Generator
"""
from catan.models import Hexe, HexePosition, Board, VertexPosition
from random import randint

TYPE_RESOURCE = ['brick', 'wool', 'grain', 'ore', 'lumber']


def generateHexesPositions():
    """
    A method to generate all the positions of the hexagons in the board:
    Generate only one time.
    """
    top_ranges = [1, 6, 12]
    for i in range(0, 3):
        for j in range(0, top_ranges[i]):
            new_hexe_position = HexePosition(level=i, index=j)
            new_hexe_position.save()


def generateVertexPositions():
    """
    A method to generate all the positions of the vertex in the board:
    Generate only one time.
    """
    top_ranges = [6, 18, 30]
    for i in range(0, 3):
        for j in range(0, top_ranges[i]):
            new_vertex_position = VertexPosition(level=i, index=j)
            new_vertex_position.save()


def generateBoard(name):
    """
    A method to generate a random board (with one desert).
    Args:
    name: name of the board to create.
    """
    new_board = Board(name=name)
    new_board.save()
    hexes_positions = HexePosition.objects.all()
    # Choise one hexe_position for desert...
    position_for_desert = randint(0, 18)
    hexe_position_desert = hexes_positions[position_for_desert]
    hexes_positions = hexes_positions.exclude(id=(position_for_desert + 1))
    new_token = randint(2, 12)
    hexe_desert = Hexe(board=new_board, token=new_token,
                       terrain='desert', position=hexe_position_desert)
    hexe_desert.save()
    for i in range(0, len(hexes_positions)-1):
        new_terrain = TYPE_RESOURCE[randint(0, 4)]
        new_token = randint(2, 12)
        new_hexe = Hexe(board=new_board, token=new_token,
                        terrain=new_terrain, position=hexes_positions[i])
        new_hexe.save()


def generateBoardTest():
    new_board = Board(name="test_board")
    new_board.save()
    hexes_positions = HexePosition.objects.all()
    tokens = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(0, len(hexes_positions)):
        new_terrain = TYPE_RESOURCE[2]
        new_token = tokens[i]
        new_hexe = Hexe(board=new_board, token=new_token,
                        terrain=new_terrain, position=hexes_positions[i])
        new_hexe.save()
    return new_board