import argparse
import json
from scripts.randGenerator import SettingGenerator
import os

text_data_path = __file__.replace("generator.py", "/data/text")

def do_until_quit(func):
    while True:
        for s in func():
            print(s)
        instring = input()
        if instring == "q":
            return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--location", help="generate location", action="store_true")
    parser.add_argument("-s", "--settlement", help="generate settlement", action="store_true")
    parser.add_argument("-m", "--monster", help="generate monster", action="store_true")
    parser.add_argument("-c", "--character", help="generate character", action="store_true")
    parser.add_argument("-t", "--thing", help="generate thing", action="store_true")
    parser.add_argument("-x", "--conflict", help="generate conflict", action="store_true")
    parser.add_argument("-p", "--plot", help="generate plot", action="store_true")
    parser.add_argument("-r", "--price", help="generate a hefty price", action="store_true")
    args = parser.parse_args()
    config = json.load(open(text_data_path + "/config.json"))
    location_generator = SettingGenerator(config["locations"], text_data_path, default_quantity=3)
    settlement_generator = SettingGenerator(config["settlements"], text_data_path)
    monster_generator = SettingGenerator(config["monsters"], text_data_path)
    character_generator = SettingGenerator(config["characters"], text_data_path, default_quantity=1)
    thing_generator = SettingGenerator(config["things"], text_data_path, default_quantity=1)
    conflict_generator = SettingGenerator(config["conflict"], text_data_path, default_quantity=1)
    price_generator = SettingGenerator(config["price"], text_data_path, default_quantity=1)
    plot_generator = SettingGenerator(config["plot"], text_data_path, default_quantity=1)

    if args.location:
        do_until_quit(location_generator.generate)
    if args.settlement:
        do_until_quit(settlement_generator.generate)
    if args.monster:
        do_until_quit(monster_generator.generate)
    if args.character:
        do_until_quit(character_generator.generate)
    if args.thing:
        do_until_quit(thing_generator.generate)
    if args.conflict:
        do_until_quit(conflict_generator.generate)
    if args.price:
        do_until_quit(price_generator.generate)
    if args.plot:
        do_until_quit(plot_generator.generate)
