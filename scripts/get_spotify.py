import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import os

import sys
import json
import argparse

from dotenv import load_dotenv
import requests

import psycopg2
import psycopg2.extras
from psycopg2 import Error
import time
import string

import re


# Source: https://github.com/rexdotsh/spotify-preview-url-workaround
def get_spotify_preview_url(spotify_track_id: str):
    """
    Get the preview URL for a Spotify track using the embed page workaround.

    Args:
        spotify_track_id (str): The Spotify track ID

    Returns:
        Optional[str]: The preview URL if found, else None
    """
    try:
        embed_url = f"https://open.spotify.com/embed/track/{spotify_track_id}"
        response = requests.get(embed_url)
        response.raise_for_status()

        html = response.text
        match = re.search(r'"audioPreview":\s*{\s*"url":\s*"([^"]+)"', html)
        return match.group(1) if match else None

    except Exception as e:
        print(f"Failed to fetch Spotify preview URL: {e}")
        return None


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))

def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_items(playlist_id, additional_types=('track',))
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def download_mp3_from_cdn(url, save_path):
    try:
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading MP3: {e}")


if __name__ == '__main__':
    #Get arguments
    parser = argparse.ArgumentParser(description='Get MP3 data')
    parser.add_argument('--filter', type=str, help='Filter on playlists')
    parser.add_argument('--env', type=str, help='.env file')
    args = parser.parse_args()

    if args.env:
        load_dotenv(dotenv_path=args.env)

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

    filters = []
    if args.filter:
        filters = [f.strip().lower() for f in args.filter.split(',')]
        
    print(filters)
    
    folder_path = "data/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    row_data = []
    duplicate_keys = set()

    ## Loop through the playlists
    for playlist in playlists['items']:
        #Filter by name
        playlist_name_lower = playlist['name'].lower()
        if filters and not any(f in playlist_name_lower for f in filters):
            continue

        print("Playlist: " + playlist['name'])
        print("-------------------------------")

        tracks = get_playlist_tracks(sp, playlist['id'])

        ## Download the tracks
        for track in tracks:
            try:
                preview = get_spotify_preview_url(track['track']['id'])
                if preview != "":
                    track_name = track['track']['artists'][0]['name'].translate(str.maketrans('', '', string.punctuation))
                    track_artist = track['track']['name'].translate(str.maketrans('', '', string.punctuation))

                    file_name = track_artist.replace(' ', '_') + '_' + track_name.replace(' ', '_') + ".mp3"
                    song_identifier = track['track']['artists'][0]['name'] + " - " + track['track']['name']

                    dest = folder_path + file_name
                    download_mp3_from_cdn(preview, dest)

                    if song_identifier not in duplicate_keys:
                        row_data.append((track['track']['name'], 
                                    track['track']['artists'][0]['name'], 
                                    track['track']['album']['release_date'][:4], 
                                    track['track']['album']['images'][0]['url'],
                                    file_name,
                                    playlist['name'],
                                    song_identifier))
                        duplicate_keys.add(song_identifier)
                    
                    print(dest)
            except:
                print("Failed to download track")
        
    ##Write to database:
    try:
        connection = psycopg2.connect(user = os.getenv('POSTGRES_USER'),
                                        password = os.getenv('POSTGRES_PASSWORD'),
                                        host = os.getenv('POSTGRES_HOST'),
                                        port = os.getenv('POSTGRES_PORT'),
                                        database = os.getenv('POSTGRES_DB'))

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        #Insert into database
        insert_query = 'INSERT INTO playlistle_song (song_name, artist, release_year, album_url, database_uri, playlist, song_identifier) VALUES %s ON CONFLICT (song_identifier) DO NOTHING'
        psycopg2.extras.execute_values (
            cursor, insert_query, row_data, template=None, page_size=100
        )
        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into table")

    except (Exception, Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")