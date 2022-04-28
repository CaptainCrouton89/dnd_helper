import os
import re
import random
import json

DATA_PATH = "data"

class SettingGenerator():

    def __init__(self, config, text_path, default_quantity=1):
        self.default_quantity = default_quantity
        if not config:
            print('no data found')
            return
        self.target = config["target"]
        data_path = os.path.join(text_path, config["path"])
        self.all_data = {}
        self.format = config["format"]

        self.log = []

        for file in os.listdir(data_path):
            if ".txt" not in file:
                continue
            with open(os.path.join(data_path, file)) as f:
                category = file[:-4]
                self.all_data[category] = set()
                for line in f:
                    self.all_data[category].add(line.strip())

        for category, s in self.all_data.items():
            self.all_data[category] = list(self.all_data[category])
        # print(self.all_data)
        save_path = self.target+"_data.json"
        # with open(save_path, "w+") as f:
        #     json.dump(self.all_data, f)
        
    def generate(self):
        print(f"""
        ======================
        Generating {self.target}
        ----------------------
        """)
        gen_text = []
        for _ in range(self.default_quantity):
            setting_object = self.format
            match = re.findall(r"<.+?>", self.format)

            for category in match:
                category_set = self.all_data[category.strip("<>")]
                for _ in range(len(category)):
                    category_instance = random.choice(tuple(category_set))
                    setting_object = setting_object.replace(category, category_instance, 1)
            setting_object = setting_object.replace("- ", "-")
            setting_object = setting_object.replace("\\n", "\n")
            setting_object = setting_object.replace("\\t", "\t")
            # setting_object = setting_object.replace("\n", "\n\t")
            # print(setting_object)
            gen_text.append(setting_object)
            self.log.append(setting_object)
        return gen_text
        
    def print_history(self):
        for setting_object in self.log:
            print(setting_object)