def duration_in_ms_to_str(duration_ms: int) -> str:
    duration_sec = int(duration_ms / 1000)
    mins = str(duration_sec // 60)
    secs = str(duration_sec % 60)
    if len(secs) < 2:
        secs = '0' + secs

    return mins + ':' + secs