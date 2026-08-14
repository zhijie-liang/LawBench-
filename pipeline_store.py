import json

def save_stage(stage, data):
    with open(f"data/{stage}.json", "w", encoding="utf-8") as f:
        json.dump(
            data, f,
            ensure_ascii=False,
            default=str
        )

def load_stage(stage):
    with open(f"data/{stage}.json", encoding="utf-8") as f:
        return json.load(f)
