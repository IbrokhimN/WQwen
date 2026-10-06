from inference import load_model, prompt

load_model()
while True:
    user_input = input("> ")
    print(prompt(user_input))
