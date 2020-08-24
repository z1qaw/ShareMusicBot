import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyApi:
    def __init__(self):
        self.client_id = '812f76008d0140d38dd8d90725d8fd84'
        self.client_secret = 'd03340f008c84d5ea0c72a271e18ecc9'
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())


if __name__ == '__main__':
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    results = spotify.search('дорн стыца')
    print(results)
