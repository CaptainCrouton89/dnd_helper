import os
import argparse
import random
import re
from gpiozero import Button
from signal import pause

DATA_PATH = "data"

class SettingGenerator():

    def __init__(self, config, verbosity):
        if not config:
            print('no data found')
            return
        self.verbosity = verbosity
        self.target = config["target"]
        data_path = os.path.join(DATA_PATH, config["path"])
        self.all_data = {}
        self.format = config["format"]

        self.log = []

        for file in os.listdir(data_path):
            with open(os.path.join(data_path, file)) as f:
                category = file[:-4]
                self.all_data[category] = set()
                for line in f:
                    self.all_data[category].add(line.strip())
        
    def generate(self):
        print(f"\nGenerating {self.target}")
        setting_object = self.format
        match = re.findall(r"<.+?>", self.format)

        for category in match:
            category_set = self.all_data[category.strip("<>")]
            category_instance = random.choice(tuple(category_set))
            setting_object = setting_object.replace(category, category_instance)
        setting_object = setting_object.replace("- ", "-")
        setting_object = setting_object.replace("\n", "\n\t")
        print(setting_object)
        self.log.append(setting_object)
        
    def print_history(self):
        for setting_object in self.log:
            print(setting_object)


class Session():

    def __init__(self, config, verbosity=0):
        self.location_generator = SettingGenerator(config["locations"], verbosity)
        self.settlement_generator = SettingGenerator(config["settlements"], verbosity)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--raspberrypi', '-r', action='store_true', help='0 for computer, 1 for RaspberryPi')
    parser.add_argument('--verbosity', '-v', action='count', default=0, help='prints debug info')
    args=parser.parse_args()

    config = {
        "locations": {
            "target": "location",
            "path": "locations",
            "format": "\n<structureDescription> <structure> <feature1> <feature2>"
        },
        "settlements": {
            "target": "settlement",
            "path": "settlements",
            "format": "\nFamous For: <prideOfTown> \nDomesticated Animal: <unusualDomesticatedAnimal> \nSubgroup: <groupWithinSettlement> \nMode of Dress: <modeOfDress>"
        }
    }

    print("Welcome to the GENERATOR™\n\n\tType 's' or 'l' for random settlements or locations, respectively.\n")

    session = Session(config, args.verbosity)

    if args.raspberrypi:
        location_button = Button(2)
        settlement_button = Button(3)

        location_button.when_released = session.location_generator.generate()
        settlement_button.when_released = session.settlement_generator.generate()
        
        pause()
    else:
        while True:
            k = input()
            if k == "l":
                session.location_generator.generate()
            elif k == "s":
                session.settlement_generator.generate()

if __name__ == '__main__':
    main()