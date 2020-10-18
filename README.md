# Music Share Bot

<img src="music_share_bot/src/avatar/avatar-alpha.png" width="150"/>

## About 

ShareMusicBot helps people who use different streaming services for music. If your friend uses Spotify and you're used to Apple Music, use this bot!

## Installation
1. Get sources:  
`$ git clone https://github.com/s1q/ShareMusicBot`  
`$ cd ShareMusicBot`  
2. Install dependencies:  
`$ pip install -r requirements.txt`  
3. Export environment variables with your API keys:  
a) Export Telegram Bot API Key - you can get it from @botfather bot in Telegram:  
`$ export SHARE_MUSIC_BOT_TOKEN="YOUR_TELEGRAM_TOKEN"`  
b) Export Spotify app Client ID and Secret - you can get it from your [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).  
`$ export SPOTIPY_CLIENT_ID="YOU_CLIENT_ID"`  
`$ export SPOTIPY_CLIENT_SECRET="YOUR_CLIENT_SECRET"`  
4. Run:  
`$ python -m music_share_bot.__main__`  
  
App must start correctly.

## TODO

- Search by services link
- ChatBase integration