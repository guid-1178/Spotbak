import csv
import getopt
import os
import re
import sys
import time

import yaml

from install import Database, spotify

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

db_fullpath = str(config["db"]["path"] + "/" + config["db"]["name"])
db = Database(db_fullpath)

client = spotify(config["spotify"])


# main menu, takes input from CLI aguments provided my the user.
def menu(argv):
    user = ""
    try:
        opts, args = getopt.getopt(argv, "hlu:o:", ["user=", "output="])
    except getopt.GetoptError:
        print("spotbak.py -u <user> -l <list users>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("spotbak.py -u <user> -o <outputfolder>")
            print("-h	help information")
            print("-l	--list		available users")
            print(
                '-u	--user=		set user (note: include commas with name, ie: "John Smith")'
            )
            sys.exit()
        elif opt in ("-l", "--list"):
            print("List of available users:")
            users = db.query("""select user from users_spotbak;""").fetchall()
            i = 0
            for a in users:
                i = i + 1
                print("{0}. '{1}'".format(i, a[0]))
            sys.exit()
        elif opt in ("-u", "--user"):
            user = arg
    return user.replace("%", ".")


# CSV writing function. checks if CSV file exists,  if not it creates CSV  and generates the title row
def write2csv(csvfile, track, album, artist, track_id, snapshot):
    try:
        file = open(csvfile, "r")
    except IOError:
        with open(csvfile, "w") as csv_file:
            track_writer = csv.writer(
                csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            track_writer.writerow(
                ["Track", "Album", "Artist", "Track_id", "Snapshot_at"]
            )

    with open(csvfile, mode="a") as csv_file:
        track_writer = csv.writer(
            csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        track_writer.writerow([track, album, artist, track_id, snapshot])


# function checks if path that was set by argument exists. if not creates path.
def foldercheck(path, user):
    path = "{0}/{1}/{2}".format(path, user, time.strftime("%Y"))
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def main():
    # get CLI arguments
    value = menu(sys.argv[1:])
    user = value
    outputfolder = config["csv"]["path"]
    # call folder check function to check if path exists. if not, it creates path
    outputfolder = foldercheck(outputfolder, user)
    # get the users ID from SQL

    userid = db.query(
        "select userid from users_spotbak where user = {0};".format(user)
    ).fetchone()[0]
    # get the refresh token from SQL ( if needed)
    tokens = db.query(
        """select refresh_token,access_token from users_spotbak where user = {0}""".format(
            user
        )
    ).fetchone()

    refresh_token = tokens[0]
    # query SQL for the access token based on Users display name
    access_token = tokens[1]
    # query spotify API for user profile information.
    # this is used primarily to check if the access_token has expired
    response = client.check_token(access_token)
    # if token has expired, it will  run through the If statement
    if "error" in response:
        if response["error"]["status"] == 401:
            # if token has expired,  renew token using refresh_token
            token = client.renew_token(refresh_token)
            # update sql with new token
            db.query(
                """ UPDATE users_spotbak SET 'access_token' = '{0}', last_updated= CURRENT_TIMESTAMP WHERE user = '{1}';""".format(
                    token["access_token"], user
                )
            )
            db._db_connection.commit()
            # update the access_token variable with new token
            access_token = token["access_token"]

        if response["error"]["status"] != 401:
            # if the error isn't 401,  something unknown has happened, print error
            print(response["error"])

    # get all users playlits from API
    pl_response = client.get_playlist(access_token, userid)
    playlist = {}  # INIT playlist dict
    # loop though JSON response and fill dict with playlist name as KEY,  playlist ID as value.
    for name in pl_response["items"]:
        playlist[name["name"]] = name["id"]

    # loop through playlist dict and get all tracks for each playlist
    for playlist_name in playlist:
        # save JSON payload from API to Value Variable
        value = client.get_tracks(access_token, playlist[playlist_name])

        # loop though value var to get each track info
        for a in range(0, len(value["items"])):
            # when looping, write each track to the row of the CSV with todays date stamp
            # each playlist gets its own CSV file named after the playlist
            playlist_name = re.sub("[^0-9a-zA-Z]+", "_", playlist_name)
            write2csv(
                "{0}/{1}.csv".format(outputfolder, playlist_name),
                value["items"][a]["track"]["name"],
                value["items"][a]["track"]["album"]["name"],
                value["items"][a]["track"]["album"]["artists"][0]["name"],
                value["items"][a]["track"]["id"],
                time.strftime("%d/%m/%Y"),
            )


main()
