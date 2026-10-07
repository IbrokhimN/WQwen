from transformers import GenerationConfig, TextIteratorStreamer
from gptqmodel import GPTQModel, BACKEND
import torch
from threading import Thread
import logging

from ..core.messages import messages

logging.basicConfig(level=logging.ERROR)
logging.getLogger("gptqmodel").setLevel(logging.ERROR)

# для глобализации перемены
pipe = None

generation_config = GenerationConfig(
    max_new_tokens=256,
    do_sample=True,
    temperature = 0.7,
    top_k=50,
    top_p=0.8,
    repetition_penalty = 1.1,
    pad_token_id = 151643
)

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
    pipe.generation_config = generation_config

def memorize( who, data ):
    global messages
    if len(messages) > 10:
        del messages[1]
        del messages[1]

    if who == "user":
        messages.append({ "role": "user", "content": data })

    elif who == "model":
        messages.append({ "role": "assistant", "content": data })

    else:
        print(f"я не знаю никакого {who}, бака >-<")


def clear_mem():
    global messages
    messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]


def prompt(user_input):
    memorize("user", user_input)

    streamer = TextIteratorStreamer( pipe.tokenizer,
                                    skip_prompt = True,
                                    skip_special_tokens = True
                                    )

    inputs = pipe.tokenizer.apply_chat_template( messages,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.model.device)

    thread = Thread(
            target = pipe.generate,
            kwargs={
                "inputs": inputs,
                "max_new_tokens": 256, # КАК ЭТО СРАБОТАЛО? ПОЧЕМУ НАДО БЫЛО ЯВНО ЕГО УКАЗАТЬ ЧТО БЫ ЛОГ ПРОПАЛ
                "streamer": streamer
                }
            )
    # result = pipe.generate( inputs, generation_config=generation_config )
    thread.start()

    model_output = ""
    for text in streamer:
        print(text, end="", flush=True)
        model_output += text

    thread.join()

    memorize("model", model_output)
    # print(messages)
    return model_output

