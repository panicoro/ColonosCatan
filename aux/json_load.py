from catan.models import *
import json
import os


MYDIR = os.path.dirname(__file__)


def HexagonInfo(level, index):
    with open(os.path.join(MYDIR, 'hexe_neighbors.json')) as file:
        data = json.load(file)

        for aux in data['data']:
            hexagon = aux['hexagono']
            if level == hexagon[0] and index == hexagon[1]:
                return aux['vecinos']


# get the neighbors of a given vertex
def VertexInfo(level, index):
    with open(os.path.join(MYDIR, 'vertex_neighbors.json')) as file:
        data = json.load(file)

        for aux in data["data"]:
            vertex = aux['vertice']
            if level == vertex[0] and index == vertex[1]:
                return aux['vecinos']
