# from transformers import pipeline
from gptqmodel import GPTQModel, BACKEND
import torch
# для глобализации перемены
pipe = None

def load_model():
    global pipe
    # Выбрал Qwtn2.5 7b квантонмизированную потому что я хочу
    # что бы на моем RTX 2080s ( 8GB VRAM ) модель полностью помещалась с запасом
    pipe = GPTQModel.load(
        "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
        backend=BACKEND.GPTQ_TORCH, # Marlin у меня не сработал по какой то причине поэтому оставил торч
        device_map = "auto" # TODO: im not sure that its working
                          # recheck it from documentation pls
        )



def prompt(user_input):
    # LLM role
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]
    inputs = pipe.tokenizer.apply_chat_template( messages,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.device)

    result = pipe.generate( inputs,
                           max_new_tokens = 256 )

    # taking only the new tokens from toe output
    new_tokens = result[0][inputs["input_ids"].shape[-1]:]

    return pipe.tokenizer.decode(new_tokens, skip_special_tokens=True)

