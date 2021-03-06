#!/usr/bin/env python
import Image
from player import Player
from StringIO import StringIO
import base64
from flask import json
import requests
from werkzeug.contrib.cache import SimpleCache
import flask_app

BASE_REST = "http://localhost:7878/cterrachar/"

cache = SimpleCache()


def make_player(info):
    char = Player()
    char.load_data(info)
    return char


def fetch_actives():
    try:
        req = requests.get(flask_app.BASE_REST + 'active_players')
        parsed = json.loads(req.text)
    except requests.RequestException:
        return json.jsonify({'error': 'could not connect to server'})
    except ValueError as e:
        flask_app.app.logger.error('IOError fetch_actives ' + e.message)
        return json.jsonify({'error': 'value error in json'})
    if 'error' in parsed:
        return json.jsonify(parsed)
    return parsed


def fetch_player_data(name):
    try:
        req = requests.get(flask_app.BASE_REST + 'player', params={'name': name})
        parsed = json.loads(req.text)
    except requests.RequestException:
        return json.jsonify({'error': 'could not connect to server'})
    except ValueError as e:
        flask_app.app.logger.error('IOError fetch_player_data ' + e.message)
        return json.jsonify({'error': 'value error in json'})
    if 'error' in parsed:
        return json.jsonify(parsed)
    return parsed['player']


def fetch_player(name):
    return cache.get(name)


def cache_player(name, info):
    char = make_player(info)
    player = to_base64(draw_character(char))
    cache.set(key=name, value=player, timeout=5 * 60)  # timeout in 5 minutes
    return player


def to_base64(img):
    imgio = StringIO()
    img.save(imgio, 'PNG', quality=100)
    imgio.seek(0)
    b64 = base64.b64encode(imgio.getvalue())
    return b64

def draw_character(player):
    from palette import Palette
    return Palette.draw_player(player)
