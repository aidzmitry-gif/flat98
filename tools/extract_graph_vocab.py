import json
import re
from pathlib import Path


graph_path = Path("graphify-out/graph.json")
data = json.loads(graph_path.read_text(encoding="utf-8"))
vocab: set[str] = set()

for node in data["nodes"]:
    label = node.get("label", "") or ""
    for chunk in re.findall(r"[^\W\d_]+", label, re.UNICODE):
        parts = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+", chunk) or [chunk]
        for part in parts:
            token = part.lower()
            if 3 <= len(token) <= 30:
                vocab.add(token)

output_path = Path("graphify-out/.vocab.txt")
output_path.write_text("\n".join(sorted(vocab)), encoding="utf-8")
print(f"vocab: {len(vocab)} tokens")
