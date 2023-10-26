import requests

class TriviaGame:
    def __init__(self):
        self.game_q = 0
        self.score = 0
        self.question = ""
        self.answer_choices = []

    def trivia_game(self):
        url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": "ask me a movie trivia question and show me 4 options(Print the question for me in this format Question:), (I would like to present in the way I wrote without adding things!)",
                }
            ]
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "d73f442011msh63871ecf2dde8bap143fadjsne460c0fb111c",
            "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)
        question_and_choices = response.json()['choices'][0]['message']['content']
        return question_and_choices

    def correct_answer(self, q, a):
        url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": f"If the answer: {a} to the question: {q} is correct, return yes, if not, return no",
                }
            ]
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "d73f442011msh63871ecf2dde8bap143fadjsne460c0fb111c",
            "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']

    def check(self, q, a):
        print(self.correct_answer(q, a).lower())
        return "yes" in self.correct_answer(q, a).lower()

    def reset_game(self):
        self.score = 0
        self.game_q = 0
        question_and_choices = self.trivia_game().split('?')
        self.question = question_and_choices[0].strip()
        self.answer_choices = question_and_choices[1].strip().split("\n")
