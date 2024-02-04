import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import os

import sys
import json
import argparse

import psycopg2
from psycopg2 import Error


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))

def get_playlist_tracks(sp, username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_track_preview(sp, track_id):
    track_info = sp.track(track_id)
    if track_info and track_info['preview_url']:
        return track_info['preview_url']
    else:
        return ""


if __name__ == '__main__':

    #Get arguments
    parser = argparse.ArgumentParser(description='Get Spotify data')
    parser.add_argument('--filter', type=str, help='Filter on playlists')
    args = parser.parse_args()

    # Set up Spotify API credentials
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    
    # Create a Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10, retries=10)

    # Get the user's playlists
    user_id = '97mi316dq36dfamaknfag208q'
    playlists = sp.user_playlists(user_id)

    #pretty_print(playlists)

    filter = ''
    if args.filter:
        filter = args.filter.lower()
    # Print the playlist names
    
    count = 0
    count_not_present = 0
    for playlist in playlists['items']:
        #Filter by name
        if filter not in playlist['name'].lower():
            continue

        print("Playlist: " + playlist['name'])
        print("-------------------------------")

        tracks = get_playlist_tracks(sp, user_id, playlist['id'])

        #Print the track names
        for track in tracks:
            count += 1

            preview = get_track_preview(sp, track['track']['id'])
            if preview == "":
                count_not_present += 1
            print(track['track']['name'] + " - " 
                  + track['track']['artists'][0]['name'] + " - " 
                  + track['track']['album']['release_date'][:4] + " - " 
                  + get_track_preview(sp, track['track']['id']))
        
    print("Count: " + str(count))
    print("Count not present: " + str(count_not_present))