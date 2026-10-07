from .inference import load_model, prompt, clear_mem

load_model()
while True:
    user_input = input("\n> ")
    match user_input:
        case "exit":
            break
        case "/clearmem":
            clear_mem()
        case _:
            prompt(user_input)
