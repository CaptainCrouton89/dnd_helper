# dnd_helper

__Main should always be stable release__

This app is a helping tool for running RPG games. Although it was designed specifically for Heart Rush, I think anyone running a fantasy RPG game will find this tool useful. It allows a GM to track games, play music, roll dice, generate ideas, and all in one workplace. Download it and try it out. Just download the repo and run dndHelper.py. You may have to download some packages.

## Features
5 primary tools built into the app:
* Music player
  * Play different moods or ambient tracks
  * Mood can be controlled with up and down arrow keys to adjust music along spectrum of music
* Die roller
  * Roll any number of dice. Just use the number keys
* Random idea generator
  * Names, locations, settlements, NPCs, and monsters! Uses databases of hundreds to thousands of high-quality items
* Monster stat tracker
  * Useful for keeping track of monster stats during a game of Heart Rush
* Session notes
  * Keep track of session and world notes in several different tool bars
  * Tool bars are persistent across sessions, so your notes will be saved
  * Encounters and specific items can be saved and loaded back into a session at a later date

## Installation Notes
* After downloading the code, try to run dndHelper.py
  * You will likely get a lot of `module not found` errors. Install whatever packages you are missing, either on your local machine or in a virtual environment
  * Keep trying to run until it works!
* The music app only works if you set up a spotify key. Go here https://developer.spotify.com/dashboard/login and log in.
  * Create new app
  * Edit settings
    * Go to `Redirect URIs` and change the website to https://google.com
  * Change the name of the local file `example-spotifykey.json` to `spotifykey.json` and change the CID and SECRET fields in the json to those found on the dashboard.
  * It should now work.
* If the music app randomly stops working, manually open spotify, start playing a few different playlists, then quit the app. 
* The app will try to manually open spotify if it's not open already. If you want the spotify functionality to work, you should give it permissions.
