from transformers import GenerationConfig
from gptqmodel import GPTQModel, BACKEND
import torch
# для глобализации перемены
pipe = None

# LLM role
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
    # {
    #    "role": "user",
    #    "content": user_input
    # }
]

generation_config = GenerationConfig(
    max_new_tokens=256, do_sample=True, temperature = 0.7, top_k=50,top_p=0.8, repetition_penalty = 1.1
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


def memorize( who, data ):
    # TODO: При увеличении чата, условно до 200 сообщений, окно становится овер огромным и модель
    # будет кушать слишком огромный промпт, это не очень оптимизированно, так что нужно сделать
    # передачу максимум 10-20 сообщений последних ( в паре user - assistant )
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

    inputs = pipe.tokenizer.apply_chat_template( messages,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.model.device)
    result = pipe.generate( inputs, generation_config=generation_config )

    # taking only the new tokens from toe output
    new_tokens = result[0][inputs["input_ids"].shape[-1]:]

    model_output = pipe.tokenizer.decode(new_tokens, skip_special_tokens=True)

    memorize("model", model_output)
    print(messages)
    return model_output

