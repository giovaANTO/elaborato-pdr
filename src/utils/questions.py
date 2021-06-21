import random
questions = {
    1: ["Question 1", "Answer1"],
    2: ["Question 2", "Answer2"],
    3: ["Question 3", "Answer3"],
    4: ["Question 4", "Answer4"],
    5: ["Question 5", "Answer5"],
    6: ["Question 6", "Answer6"],
}


def select_questions(n):
    """
    Select a random number of questions from the main list.
    If n is greater or equal to the dimension of the question dictionary all questions
    are returned.
    :param n: number of question to select
    :return: a list of select questions with relative answers.
    """
    if n >= len(questions):
        return questions
    _out = {}
    for k in random.sample(list(questions.keys()), 2):
        _out[k] = questions[k]
    return _out
