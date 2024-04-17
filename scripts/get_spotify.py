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

    filter = ''
    if args.filter:
        filter = args.filter.lower()

    folder_path = "data/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    row_data = []
    duplicate_keys = set()

    ## Loop through the playlists
    for playlist in playlists['items']:
        #Filter by name
        if filter not in playlist['name'].lower():
            continue

        print("Playlist: " + playlist['name'])
        print("-------------------------------")

        tracks = get_playlist_tracks(sp, user_id, playlist['id'])

        ## Download the tracks
        for track in tracks:

            preview = get_track_preview(sp, track['track']['id'])
            if preview != "":
                track_name = track['track']['artists'][0]['name'].translate(str.maketrans('', '', string.punctuation))
                track_artist = track['track']['name'].translate(str.maketrans('', '', string.punctuation))

                file_name = track_artist.replace(' ', '_') + '_' + track_name.replace(' ', '_') + ".mp3"
                dest = folder_path + file_name
                download_mp3_from_cdn(preview, dest)
                if file_name not in duplicate_keys:
                    row_data.append((track['track']['name'], 
                                 track['track']['artists'][0]['name'], 
                                 track['track']['album']['release_date'][:4], 
                                 track['track']['album']['images'][0]['url'], 
                                 file_name))
                    duplicate_keys.add(file_name)
                
                print(dest)
        
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
        insert_query = 'INSERT INTO playlistle_song (song_name, artist, release_year, album_url, database_uri) VALUES %s'
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