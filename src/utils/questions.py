import random
questions = {
    1: ["Question 1", "Answer1"],
    2: ["Question 2", "Answer2"],
    3: ["Question 3", "Answer3"],
    4: ["Question 4", "Answer4"],
    5: ["Question 5", "Answer5"],
    6: ["Question 6", "Answer6"],
}


def select_question():
    return random.choice(list(questions.items()))


if __name__ == "__main__":
    print(select_question())