import psycopg2
import os
import datetime
from psycopg2 import Error
import time

def reset_daily():
    while True:
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

            cursor.execute("SELECT * FROM playlistle_songofday ORDER BY date_added DESC LIMIT 1")
            latest_song = cursor.fetchone()
            last_date = latest_song[0]
            today_date = datetime.datetime.now().date()
            song_date = datetime.datetime.fromtimestamp(last_date).date()
            print(f"Last date: {song_date}")
            print(f"Today date: {today_date}")
            if today_date != song_date:
                cursor.execute("SELECT * FROM playlistle_song ORDER BY RANDOM() LIMIT 1")
                random_song = cursor.fetchone()
                insert_query = 'INSERT INTO playlistle_songofday (date_added, song_id) VALUES (%s, %s)'
                cursor.execute(insert_query, (datetime.datetime.now().date(), random_song[6]))
                connection.commit()
                print(f"Song of the day {random_song[6]} inserted successfully")

        except (Exception, Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        time.sleep(15 * 60)

if __name__ == '__main__':
    reset_daily()