#!/Library/Frameworks/Python.framework/Versions/3.9/bin/python3

import os
import argparse
import json
import pickle

import randGenerator
import dice
import musicPlayer
# Necessary if being run on RaspberryPi
try:
    from gpiozero import Button
    from signal import pause
except:
    pass

DATA_PATH = "data"
CAMPAIGN_PATH = "campaigns"

def save_game(campaign, filename):
    with open(os.path.join(CAMPAIGN_PATH, filename), 'wb') as outp:
        pickle.dump(campaign, outp, pickle.HIGHEST_PROTOCOL)

class Campaign():

    def __init__(self):
        self.name = "Campaign"
        self.all_sessions = []
        self.musicPlayer = musicPlayer.MusicPlayer()

    def new_session(self):
        self.session = Session()
        self.all_sessions.append(self.session)
        

class Session():

    def __init__(self, config, pi=False, verbosity=0):
        self.location_generator = randGenerator.SettingGenerator(config["locations"], verbosity)
        self.settlement_generator = randGenerator.SettingGenerator(config["settlements"], verbosity)
        self.monster_generator = randGenerator.SettingGenerator(config["monsters"], verbosity)
        self.pi = pi

        

    def start(self):
        pass

    def start_generator(self):        
        if self.pi:
            location_button = Button(2)
            settlement_button = Button(3)

            location_button.when_released = self.location_generator.generate()
            settlement_button.when_released = self.settlement_generator.generate()
            
            pause()
        else:
            while True:
                k = input()
                if k == "l":
                    self.location_generator.generate()
                elif k == "s":
                    self.settlement_generator.generate()
                elif k == "m":
                    self.monster_generator.generate()



def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--raspberrypi', '-r', action='store_true', help='0 for computer, 1 for RaspberryPi')
    parser.add_argument('--verbosity', '-v', action='count', default=0, help='prints debug info')
    args=parser.parse_args()

    print("Welcome to the GENERATOR™\n\n\tType 's' or 'l' for random settlements or locations, respectively.\n")

    with open(os.path.join(DATA_PATH, "config.json")) as f:
        config = json.load(f)

    session = Session(config, args.raspberrypi, args.verbosity)

    session.start_generator()
    
if __name__ == '__main__':
    main()