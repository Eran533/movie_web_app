import requests

def trivia_game():
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
        "X-RapidAPI-Key": "234f5498c9msh8226e93fd4984d6p11b844jsn286c0f051d2e",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    question_and_choices = response.json()['choices'][0]['message']['content']
    return question_and_choices

def correct_answer(q):
    url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"{q}",
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "234f5498c9msh8226e93fd4984d6p11b844jsn286c0f051d2e",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']

def check(user_answer, c_answer):
    if user_answer.lower() in c_answer.lower():
        return True
    else:
        return False
