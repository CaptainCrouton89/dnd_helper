# Outline

## MVP2 Goals
- Make monsters generate automatically from basic templates. Give the campaign the player levels, let it work the magic
- Automatically name the monsters/number them upon duplication
- Fix the dimensions of the windows
- Quit and reopen spotify to get it to work?
- Make it so windows don't just randomly open up when you switch screens
- Autosave functionality?
- More generators!
- More/better playlists
- Better hotkey bindings

### Story Generator Overhaul
- Story-level encounter generation: What does this settlment not have enough of?
- What does this group have an excess of?
- What conflicts does this group face (not necessarily violent, just difficulties)
- Government organization, view of outsiders, key people
- This is a change

## Initial Goals (MVP)
- Should be as general purpose as possible, replacing the things most obnoxious about using computer
- Need to lean into it's portability: Going somewhere, and can only bring one thing? Bring this.
    - Music ability: Selecting the right music quickly, and being portable and working without wifi
    - Random Generator: Not system specific--always useful
    - Quick die roller

## Local Run?
- App like my monster tracker app
- Has all my features wrapped into one
- Not as convenient as phone, but more tools, more powerful, faster development

## Hardware
- Raspberry Pi Zero W, wifi and bluetooth support
- Scrolling LCD screen mounted above
- Battery powered
- Array of buttons
    - Require different functionality based on current "app"?
    - Up/Down keys to change app, allows any number of apps
    - Each app gets 8 buttons (4 under each thumb), along with 2 modifier keys?
    - Power switch
    - Restart button?
- Should be robust, and pocket sized

## Campaign Tracker
- Keep track of saved objects from Random Generator app
- Gets notes uploaded from computer about things happening in game (session plans/notes)

## Random Generator
- Get random locations, settlements, NPCs, etc

## Music Player
- Can play music directly from phone, or stream from phone to RPI, less automation however
- Download a bunch of music to Pi and automate into playlists
    - Start playlist with press of a button
        - Choose playlist
        - Skip button
        - Volume
        - Power
- "Smart" player
    - Choose "flavor" and "intensity"
        - "mysterious" > "ominous" > "horror" > "horror battle" 
        - "calm" > "serious" > "somber" > "melancholy" > "tragedy"
        - "exploration" > "magestic exploration"
        - All locations:
            - Forest > Jungle > Rainforest
    - Easy song loop button

## Mob Tracking
- Can upload mobs from my computer to device remotely
- Can do rudimentary things with mob on RPI
    - Need quite a few buttons to do stuff
        - Scroll/tab, modkey1, modkey2, hotkey[1-6]
        - Maybe just number keys? Plug in values manually

## Plot Mapper
- Some tool for keeping track of everythign going on in campaign?
- Includes notes written up on laptop, loaded?
    - I rarely need to write stuff down during session except to...
        - Edit mobs
        - Write down names
        - Take session notes for things I need to do prep on?

## Die Roller
- Would be cool if it was digital clock style, and numbers "spun"
    - 1 > 2 > 3 > 4 > 5 > 6 > 1... slower and slower, till "coming to a rest" on a number
- Voice-over! "That's a 4! You suck!"