""" Будем делить файл в формат

id: systemd.md
source: documents/systemd.md
text: "systemd is a system and service manager..."
type: markdown

"""
from pathlib import Path
from pprint import pprint

SUPPORTED_FORMATS = ["md", "txt"]

def find_format(filename):
    filename = filename.lower()
    i = len(filename) - 1       # поинтер в конец файлнейм
    form = ""
    while filename[i] != ".":
        form = form + filename[i]
        i -= 1
    return form[::-1]           # переворачиваем строку

def is_format_supported(filename):
    return find_format(filename) in SUPPORTED_FORMATS

def parse_knowledge():
    root_path = Path(__file__).resolve().parents[2] / "knowledge"
    # Получаем список путей только к файлам во всех подпапках
    files = [f for f in root_path.rglob('*') if f.is_file()]

    return files


def dictify(source):
    """
    id: name
    source: уже задан
    text: возьмем
    metadata:
        type:markdown
    """
    with open(source, "r", encoding="utf-8") as file:
        name = Path(file.name).name
        if is_format_supported(name):
            text = file.read()
            # TODO: сделать нормальный filetype счетчик
            # сейчас у меня захардкожено под маркдаун
            filetype = find_format(name)
            return {
                    "id": name,
                    "source": source,
                    "text": text,
                    "type": filetype
                    }


# file = open("../../knowledge/personal/IluminOS/README.md", "r")
# pprint(dictify("../../knowledge/personal/IluminOS/README.md"))
# parse_knowledge()

knowledge = parse_knowledge()
for i in knowledge:
    print("#################################################\n\n\n\n")
    print(dictify(i))
    print("\n\n\n\n#################################################")

