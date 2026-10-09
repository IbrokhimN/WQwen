from transformers import GenerationConfig, TextIteratorStreamer
from gptqmodel import GPTQModel, BACKEND
import torch
from threading import Thread
import logging

from ..core.messages import messages, memorize, clear_mem
from ..memory.manager import *

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

def prompt(user_input):
    memorize("user", user_input)

    streamer = TextIteratorStreamer( pipe.tokenizer,
                                    skip_prompt = True,
                                    skip_special_tokens = True
                                    )
    available_categories = categories()
    handler_input = [
        {
            "role": "system",
            "content": f"""
You are a Memory Router. Your only task is to select the memory categories needed to answer the user's question.

Available categories:

{categories()}

Rules:
1. You MUST select one or more categories from the available categories.
2. You MUST NEVER create, rename, translate, or modify a category.
3. If the question clearly matches a category, select that category.
4. If the question does not clearly match a category, select the most semantically relevant category.
5. You MUST always select at least one category.
6. Return ONLY the exact category names, one per line.
7. Do NOT answer the user's question.
8. Do NOT explain your choice.
9. "communication" is NOT a valid category. Questions about how the user prefers to communicate belong to "preferences".

Examples:

User question: What programming language does the user prefer?
Output:
programming

User question: How does the user want me to communicate with them?
Output:
preferences

User question: What project is the user currently working on?
Output:
projects

User question: What operating system does the user use?
Output:
environment

Available categories:
{available_categories}

User question:
{user_input}
            """ }
    ]


    handler = pipe.tokenizer.apply_chat_template( handler_input,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.model.device)

    thread = Thread(
            target = pipe.generate,
            kwargs={
                "inputs": handler,
                "max_new_tokens": 256, # КАК ЭТО СРАБОТАЛО? ПОЧЕМУ НАДО БЫЛО ЯВНО ЕГО УКАЗАТЬ ЧТО БЫ ЛОГ ПРОПАЛ
                "streamer": streamer
                }
            )
    # result = pipe.generate( inputs, generation_config=generation_config )
    thread.start()

    model_output = ""
    for text in streamer:
        # print(text, end="", flush=True)
        model_output += text

    thread.join()

    # делаем из двойных и более строк с категориями - список катигорий
    selected_categories = model_output.strip().splitlines()

    facts = []

    for category in selected_categories:
        facts = facts + get_category_fact(category)


    memory_text = "\n".join(
        f"- {fact[1]}"
        for fact in facts
    )

    # print("FACTS:", facts)
    # print("MEMORY TEXT:", memory_text)

    temp_messages = messages.copy()

    temp_messages.insert(
        1,
        {
            "role": "system",
            "content": f"""
        Relevant user memory:

        {memory_text}
"""
        }
)

    streamer = TextIteratorStreamer(
        pipe.tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )


    inputs = pipe.tokenizer.apply_chat_template( temp_messages,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.model.device)

    thread = Thread(
            target = pipe.generate,
            kwargs={
                "inputs": inputs,
                "max_new_tokens": 256,
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
    return model_output

