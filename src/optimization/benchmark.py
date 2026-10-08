from transformers import GenerationConfig, TextIteratorStreamer
from gptqmodel import GPTQModel, BACKEND
import time

# TODO: сейчас тесты не совсем точные ибо идет сугубо среднее арифм.
# И токенов токо 20 генерируется, надо сделать чтоб генерило не фиксированно 20

messages = [
    [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Что такое Qwen?"
        }
    ],

    [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Что такое Large Language Model?"
        }
    ],

    [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Расскажи мне об OpenAI."
        }
    ],

    [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Расскажи мне об Antropic."
        }
    ],

    [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Кто такие хакеры и чем они занимаются?"
        }
    ],
]

generation_config = GenerationConfig(
    max_new_tokens=256,
    do_sample=False,
    temperature = 0.7,
    top_k=50,
    top_p=0.8,
    repetition_penalty = 1.1,
    pad_token_id = 151643
)

# что бы найти среднюю арифметическую
tok_per_sec_avg = 0
gen_tok_avg = 0
gen_time_avg = 0

pipe = GPTQModel.load(
        "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
        backend=BACKEND.GPTQ_TORCH,
        device_map = "auto"
        )
pipe.generation_config = generation_config
for i in range(0, len(messages)):
    inputs = pipe.tokenizer.apply_chat_template( messages[i],
                                                    add_generation_prompt=True,
                                                    return_tensors = "pt" ).to(pipe.model.device)



    start = time.time()
    output = pipe.generate( inputs )
    end = time.time()

    gen_time = end - start
    generated_tokens = output.shape[-1] - inputs.input_ids.shape[-1]

    tok_per_sec = generated_tokens / gen_time

    tok_per_sec_avg += tok_per_sec
    gen_tok_avg     += generated_tokens
    gen_time_avg    += gen_time
    # print("BENCHMARK: ")
    # print(f"\ttokens per second: {tok_per_sec}")
    # print(f"\tgenerated tokens: {generated_tokens}")
    # print(f"\tgeneration time: {gen_time}")

# Выводим среднее арифметическое
print("AVG BENCHMARKS: ")
print(f"\ttokens per second: {tok_per_sec_avg / len(messages)}")
print(f"\tgenerated tokens: {gen_tok_avg / len(messages)}")
print(f"\tgeneration time: {gen_time_avg / len(messages)}")



# BENCHMARK template:
#  	tokens per second: 3.6291858670847743
#  	generated tokens: 20
# 	generation time: 5.510877847671509


