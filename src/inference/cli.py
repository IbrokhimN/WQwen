from inference import load_model, prompt, clear_mem

load_model()
while True:
    user_input = input("> ")
    match user_input:
        case "exit":
            break
        case "/clearmem":
            clear_mem()
        case _:
            print(prompt(user_input))
