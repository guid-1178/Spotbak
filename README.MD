# Spotbak

A simple app to query spotify API for a users playlists and save them as a CSV file.

Idea behind this was if there was a situation where spotify was no longer available, it would be benificial to have a backup of the users playlists so they can be recreated.

The other use case is that spotify created playlists such as 'Discover Weekly' and 'Release Radar'  get overwritten each week and there's no way to recover the old list of songs.

Spotbak will save the song information into a CSV to allow you to look at the playlist history.

## Setup

1. sign up for a spotify developer account.
2. create an App.
    1. set App Name and description.
    2. Set redirect URI to `http://localhost:5000/spotify/callback` (this is used for OAuth)
3. Clone this repo
4. setup a python virtual environment (optional but reccomended)
5. Install requirements `pip3 install -r requirements.txt`
6. Edit `config.yaml`. update `client ID` and `client secret` that was provided by spotify for your app. (dont edit CSV or DB paths, this is done during installation.)
7. Run the web-based setup wizard `flask --app setupwiz run` add the `--debug` switch if needed.
    1. Set the path for the database and CSV output.
    2. install DB.
    3. Authorize the app to access your spotify account.
8. installation complete, you're now ready to run the spotbak script.

**note: flask app is only used for setup, `spotbak.py` is a cli-only script**

## Running spotbak

`python3 spotback.py -u <user> -l <list users>`
### Listing users:
`python3 spotbak.py -l` will return a list of users registered with this app. 

User Names are sourced from the display name set on the spotify account.

example:
````
List of available users:
1. 'john smith' 
3. 'jane doe'
````
### Normal operation:
when specifying the user, use the name of the user in quotes.

` python3 spotback.py -u 'john smith'`

spotbak will query all the playlists the user has, save each track name, artist, albumn and timestamp when the track was saved into a CSV file with the playlist name.

Example:
````
Release_Radar.csv

Track,Album,Artist,Track_id,Snapshot_at
Witchcraft,Immersion,Pendulum,7gRdsfsvODt3453fKawyGmd,01/03/2020
````

### Folder structure
The csv will be ammended each time the script is run.
Run it weekly to capture release radar playlists before they're overwritten.

Each year spotbak will create a year folder for the playlists and start again.

example:

````
.
└── John Smith
    ├── 2018
    │   ├── Discover_Weekly.csv
    │   ├── Release_Radar.csv
    │   └── Repeat_Rewind.csv
    ├── 2019
    │   ├── Discover_Weekly.csv
    │   ├── Release_Radar.csv
    │   └── Repeat_Rewind.csv
    └── 2020
        ├── Discover_Weekly.csv
        ├── Release_Radar.csv
        └── Repeat_Rewind.csv

````


Script Descriptions:
* `setupwiz.py` - flask app for web-based setup
* `install.py` - contains supporting classes and functions for spotbak.
* `spotbak.py` main script that queries spotify API and writes data to CSV file.
* `mergecsv.py` legacy script that was used to merge duplicate csv files that were generated during testing
