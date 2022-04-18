import re
"""
adjectives = set()
nouns = set()
mods = set()
with open("locations.txt", "r") as a_file:
    for line in a_file:
        stripped_line = line.strip()
        stripped_line = stripped_line.split(" ")
        try:
            of_index = stripped_line.index("of")
            mods.add(" ".join(stripped_line[of_index:]))
        except:
            continue
        if len(stripped_line[:of_index]) > 1:
            adjectives.add(stripped_line[0])
            nouns.add(stripped_line[1])
        else:
            nouns.add(stripped_line[0])
with open("locationNoun.txt", "w+") as a_file:
    for adj in adjectives:
        a_file.write(adj + "\n")
with open("locationAdjective.txt", "w+") as a_file:
    for noun in nouns:
        a_file.write(noun + "\n")
with open("locationMod.txt", "w+") as a_file:
    for mod in mods:
        a_file.write(mod + "\n")
"""

nouns = set()
with open("fantasyItemsOld.txt", "r") as a_file:
    for line in a_file:
        stripped_line = re.sub(r"(\w)([A-Z])", r"\1\n\2", line)
        stripped_line = stripped_line.split("\n")
        for sentence in stripped_line:
            nouns.add(sentence)
with open("fantasyItems.txt", "w+") as a_file:
    for noun in nouns:
        a_file.write(noun + "\n")