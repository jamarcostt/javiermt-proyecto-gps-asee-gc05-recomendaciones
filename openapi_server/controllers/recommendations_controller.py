import connexion
from typing import Dict, Tuple, Union, List

from openapi_server.models.like import Like
from openapi_server.models.play import Play
from openapi_server.models.track import Track
from openapi_server import util

# ==============================================================================
#  BASE DE DATOS TEMPORAL (Paso 1)
# ==============================================================================
_PLAYS_DB = []
_LIKES_DB = []

# ==============================================================================
#  ESCRITURA (PLAYS & LIKES)
# ==============================================================================

def add_play(body):
    """Registrar una reproducción"""
    if connexion.request.is_json:
        play_obj = body 
        # TODO: MongoDB implementation pending
        # db.plays.insert_one(play_obj.to_dict())
        
        _PLAYS_DB.append(play_obj)
        print(f"--> Play registrada: User {play_obj.user_id}")
    return "Play registered", 201

def add_like(body):
    """Registrar un like"""
    if connexion.request.is_json:
        like_obj = body
        # TODO: MongoDB implementation pending
        # db.likes.insert_one(like_obj.to_dict())
        
        _LIKES_DB.append(like_obj)
        print(f"--> Like registrado: User {like_obj.user_id}")
    return "Like registered", 201

# ==============================================================================
#  LECTURA BÁSICA
# ==============================================================================

def get_user_plays(id_user):
    return [p for p in _PLAYS_DB if p.user_id == id_user]

def get_user_likes(id_user):
    return [l for l in _LIKES_DB if l.user_id == id_user]

def get_track_plays(id_track):
    return [p for p in _PLAYS_DB if p.track_id == id_track]

def get_track_likes(id_track):
    return [l for l in _LIKES_DB if l.track_id == id_track]

# STUBS (Resto vacío por ahora)
def get_artist_plays(id_artist): return []
def get_artist_top_tracks(id_artist): return []
def get_recommended_tracks(id_user, type=None): return []
def get_top_tracks(): return []