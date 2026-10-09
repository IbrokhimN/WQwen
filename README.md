# WQwen

Wqwen - это проект который реализует обертку над опен соурс [qwen2.5](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4).
На данный момент проект на начальном этапе, вскоре планируются такие обновления как веб серчинг модели, RAG система, память о юзере
и многое другое

## Использованные модели

**LLM**: Qwen 2.5-7B-Instruct-GPTQ-Int4
**Embedding Model**: BAII/bge-m3

## Быстрый старт

Клонируйте репозиторий и установите модель.
```bash
git clone https://github.com/IbrokhimN/WQwen
cd WQwen
chmod +x models/qwen/download.sh
```

Установите зависимости проекта.
``` bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

Запустите инференс.
``` bash
python3 -m src.inference.cli
```
---

Лицензия [MIT](https://github.com/IbrokhimN/WQwen/blob/main/LICENSE)
