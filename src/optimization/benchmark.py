from transformers import GenerationConfig, TextIteratorStreamer
from gptqmodel import GPTQModel, BACKEND
import time

# TODO: сейчас у нас всего 1 тест с промптом идет
# Нужно сделать несколько что бы Tokens/sec был более точным

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Что такое Qwen?"
    }
]

generation_config = GenerationConfig(
    max_new_tokens=256,
    do_sample=True,
    temperature = 0.7,
    top_k=50,
    top_p=0.8,
    repetition_penalty = 1.1,
    pad_token_id = 151643
)



pipe = GPTQModel.load(
        "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
        backend=BACKEND.GPTQ_TORCH,
        device_map = "auto"
        )
pipe.generation_config = generation_config

inputs = pipe.tokenizer.apply_chat_template( messages,
                                                add_generation_prompt=True,
                                                return_tensors = "pt" ).to(pipe.model.device)



start = time.time()
output = pipe.generate( inputs )
end = time.time()

gen_time = end - start
generated_tokens = output.shape[-1] - inputs.input_ids.shape[-1]

tok_per_sec = generated_tokens / gen_time

print("BENCHMARK: ")
print(f"\ttokens per second: {tok_per_sec}")
print(f"\tgenerated tokens: {generated_tokens}")
print(f"\tgeneration time: {gen_time}")

# git commit -m "feat: added benchmark counter"

# BENCHMARK:
#  	tokens per second: 3.6291858670847743
#  	generated tokens: 20
# 	generation time: 5.510877847671509
