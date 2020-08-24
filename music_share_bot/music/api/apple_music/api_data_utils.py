from datetime import date
from music_share_bot.music.api.apple_music.data.song import Song
from .data.search_query import SearchAnswer
from .data.artist import Artist
from .data.album import Album
from .data.artwork import Artwork


def compare_amusic_artist(data_dict):
    return Artist(
            id=data_dict['id'],
            href=data_dict['href'],
            name=data_dict['attributes']['name'],
            artwork=Artwork(
                width=data_dict['attributes']['artwork']['width'],
                height=data_dict['attributes']['artwork']['height'],
                url=data_dict['attributes']['artwork']['url']
            ) if 'artwork' in data_dict['attributes'] else None,
            url=data_dict['attributes']['url'],
            genre_names=set([genre_name for genre_name in data_dict['attributes']['genreNames']])
        )


def compare_amusic_album(data_dict):
    release_year = list(map(int, data_dict['attributes']['releaseDate'].split('-')))[0]
    return Album(
        id=data_dict['id'],
        artwork=Artwork(
            width=data_dict['attributes']['artwork']['width'],
            height=data_dict['attributes']['artwork']['height'],
            url=data_dict['attributes']['artwork']['url']
        ),
        artist_name=data_dict['attributes']['artistName'],
        is_single=data_dict['attributes']['isSingle'],
        url=data_dict['attributes']['url'],
        is_complete=data_dict['attributes']['isComplete'],
        genre_names=set([genre_name for genre_name in data_dict['attributes']['genreNames']]),
        track_count=data_dict['attributes']['trackCount'],
        release_date=release_year,
        name=data_dict['attributes']['name']
    )


def compare_amusic_song(data_dict):
    release_date = list(map(int, data_dict['attributes']['releaseDate'].split('-'))) \
        if data_dict['attributes']['releaseDate'] else None
    return Song(
        id=data_dict['id'],
        href=data_dict['href'],
        artist_name=data_dict['attributes']['artistName'],
        url=data_dict['attributes']['url'],
        duration=data_dict['attributes']['durationInMillis'],
        release_date=date(
            year=release_date[0],
            month=release_date[1],
            day=release_date[2]
        ),
        name=data_dict['attributes']['name'],
        album_name=data_dict['attributes']['albumName'],
        genre_names=set([genre_name for genre_name in data_dict['attributes']['genreNames']]),
        artwork=Artwork(
            width=data_dict['attributes']['artwork']['width'],
            height=data_dict['attributes']['artwork']['height'],
            url=data_dict['attributes']['artwork']['url']
        )
    )


def compare_amusic_datatype(data_dict):
    assert data_dict['type'] in ['artists', 'albums', 'songs']

    if data_dict['type'] == 'artists':
        return compare_amusic_artist(data_dict)
    elif data_dict['type'] == 'albums':
        return compare_amusic_album(data_dict)
    elif data_dict['type'] == 'songs':
        return compare_amusic_song(data_dict)


def search_query_answer_json_dict_to_class(query_json_dict: dict):
    result_data = query_json_dict['results']
    answer = SearchAnswer(
        top_results=tuple(
            [compare_amusic_datatype(data_instanse) for data_instanse in result_data['top']['data']]
        ) if 'top' in result_data else set([]),
        songs=tuple(
            [compare_amusic_song(data_instanse) for data_instanse in result_data['song']['data']]
        ) if 'song' in result_data else set([]),
        albums=tuple(
            [compare_amusic_album(data_instanse) for data_instanse in result_data['album']['data']]
        ) if 'album' in result_data else set([]),
        artists=tuple(
            [compare_amusic_artist(data_instanse) for data_instanse in result_data['artist']['data']]
        ) if 'artist' in result_data else set([]),
        order=set(enumerate([type_order for type_order in query_json_dict['meta']['results']['order']]))
    )

    return answer