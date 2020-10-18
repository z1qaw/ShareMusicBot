import re


def duration_in_ms_to_str(duration_ms: int) -> str:
    duration_sec = int(duration_ms / 1000)
    mins = str(duration_sec // 60)
    secs = str(duration_sec % 60)
    if len(secs) < 2:
        secs = '0' + secs

    return mins + ':' + secs


def apple_music_artist_name_filter(artist_name: str) -> str:
    name_parts_to_remove = [r' \& [\s\w]+$']
    for name_part in name_parts_to_remove:
        artist_name = re.sub(name_part, '', artist_name)
    
    return artist_name


def apple_music_track_name_filter(track_name: str) -> str:
    name_parts_to_remove = [r' \- EP', r' \- Single', r' \(feat\. [\w\s]+\)']
    for name_part in name_parts_to_remove:
        track_name = re.sub(name_part, '', track_name)
    
    return track_name