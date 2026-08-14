# tools/media_control.py
import webbrowser

# Custom music dictionary for quick links
MUSIC_PLAYLIST = {
    "lofi": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "favorite": "https://www.youtube.com/results?search_query=favorite+songs",
}

def play_music(song_or_genre: str) -> str:
    """
    Plays music or searches for songs/genres on YouTube.
    :param song_or_genre: Name of song, artist, or genre (e.g. 'lofi', 'chill beats', 'rock').
    """
    query = song_or_genre.lower().strip()
    if query in MUSIC_PLAYLIST:
        webbrowser.open(MUSIC_PLAYLIST[query])
        return f"Playing preset '{query}' on YouTube."
    
    # Search and play on YouTube
    search_url = f"https://www.youtube.com/results?search_query={song_or_genre.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Opened YouTube search for '{song_or_genre}'."