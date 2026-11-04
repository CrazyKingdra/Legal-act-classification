from collections import Counter
from urllib.request import urlopen
import json

from datasets import load_dataset


# Load Croatian MultiEURLEX with EUROVOC Level 2 labels
dataset = load_dataset(
    "coastalcph/multi_eurlex",
    "hr",
    trust_remote_code=True,
    label_level="level_2"
)

# Get EUROVOC IDs
label_names = dataset["train"].features["labels"].feature.names

# Count label occurrences
label_counts = Counter()

for example in dataset["train"]:
    label_counts.update(example["labels"])


# Download official EUROVOC descriptions
url = "https://raw.githubusercontent.com/nlpaueb/multi-eurlex/master/data/eurovoc_descriptors.json"

with urlopen(url) as response:
    eurovoc_descriptors = json.load(response)


# Print all labels with their English names and frequencies
print("\nEUROVOC LEVEL 2 LABELS")
print("-" * 65)

for label_index, count in label_counts.most_common():
    eurovoc_id = label_names[label_index]

    descriptor = eurovoc_descriptors.get(eurovoc_id, {})
    english_name = descriptor.get("en", "NOT FOUND")

    print(f"{eurovoc_id} | {english_name} | {count}")

print("\nTotal unique labels:", len(label_counts))
print("Total training documents:", len(dataset["train"]))