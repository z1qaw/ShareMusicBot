from .data.ym_objects_set import ObjectsSet
from .data.track import Track
from .data.album import Album
from .data.artist import Artist
from .data.search_query import SearchQuery


def compare_ym_track_dict(json_dist: dict) -> Track:
    return Track(
        id=json_dist['id'],
        album_id=json_dist['albums'][0]['id'],
        cover_uri=json_dist['albums'][0]['coverUri'] if 'coverUri' in json_dist['albums'][0] else '',
        release_year=json_dist['albums'][0]['originalReleaseYear'] if 'originalReleaseYear' in json_dist['albums'][0] else None,
        duration=json_dist['durationMs'],
        explicit=json_dist['explicit'],
        artist_id=json_dist['artists'][0]['id'],
        artist_name=json_dist['artists'][0]['name'],
        name=json_dist['title']
    )


def compare_ym_album_dict(json_dict: dict) -> Album:
    return Album(
        id=json_dict['id'],
        release_year=json_dict['originalReleaseYear'],
        cover_uri=json_dict['coverUri'],
        artist_name=json_dict['artists'][0]['name'],
        artist_id=json_dict['artists'][0]['id'],
        name=json_dict['title'],
        genre=json_dict['genre'] if 'genre' in json_dict else None
    )


def compare_ym_artist_dict(json_dict: dict) -> Artist:
    return Artist(
        id=json_dict['id'],
        name=json_dict['name'],
        cover_uri=json_dict['cover']['uri'] if 'cover' in json_dict else None,
        genres=set([genre for genre in json_dict['genres']])
    )


def compare_ym_objects_set_dict(objects_dict: dict, compare_object_func, object_type) -> ObjectsSet:
    return ObjectsSet(
            object_type=object_type,
            items=tuple([compare_object_func(object_dict) for object_dict in objects_dict['items']]),
            total=objects_dict['total'] if 'total' in objects_dict else None,
            per_page=objects_dict['perPage'] if 'perPage' in objects_dict else None,
            order=objects_dict['order'] if 'order' in objects_dict else None
        )


def compare_ym_search_query_dict(json_dict: dict) -> SearchQuery:
    return SearchQuery(
        text=json_dict['text'],
        albums=compare_ym_objects_set_dict(
            objects_dict=json_dict['albums'],
            compare_object_func=compare_ym_album_dict,
            object_type='album'
        ),
        artists=compare_ym_objects_set_dict(
            objects_dict=json_dict['artists'],
            compare_object_func=compare_ym_artist_dict,
            object_type='artist'
        ),
        tracks=compare_ym_objects_set_dict(
            objects_dict=json_dict['tracks'],
            compare_object_func=compare_ym_track_dict,
            object_type='track'
        ),
        counts={
            'artists': json_dict['counts']['artists'],
            'albums': json_dict['counts']['albums'],
            'tracks': json_dict['counts']['tracks']
        }
    )