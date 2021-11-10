import random

class Dice():

    log = []

    

    # Can I use decorators to make these also spin the dial for the dice?
    @staticmethod
    def log_roll(dice, raw, results):
        Dice.log.append({"dice": dice, "raw": raw, "results": results})
        return Dice.log[-1]["results"], Dice.log[-1]
    
    @staticmethod
    def roll(*dice_list):
        results = [random.randint(1, die) for die in dice_list]
        return Dice.log_roll([dice_list], results, results)
   
    @staticmethod
    def roll_advg(*dice_list):
        results = [random.randint(1, die) for die in dice_list]
        return Dice.log_roll([dice_list], results, sorted(results, reverse=True)[:2])

    @staticmethod
    def roll_dsvg(*dice_list):
        results = [random.randint(1, die) for die in dice_list]
        return Dice.log_roll([dice_list], results, sorted(results, reverse=False)[:2])

def main():
    results, _ = Dice.roll_advg(8, 8, 8, 2, 8, 8)
    print(results)

if __name__ == '__main__':
    main()