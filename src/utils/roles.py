"""
Utility used for selecting a role in the game.
"""

import random


def random_role():
    """
    Select a random role from the list
    :return: Random string contained from a list of roles.
    """
    roles = ["Druid", "Wizard", "Warrior", "Thief", "Warlock", "Death King", "Demon Hunter", "Paladin", "Hunter",
             "Monk"]
    return random.SystemRandom().choice(roles)

if __name__ == "__main__":
    print(random_role())
