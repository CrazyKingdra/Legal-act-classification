
from datasets import load_dataset
from collections import Counter
from src.eurovoc_mapping import get_majority_area


# Load the Croatian part of MultiEURLEX
dataset = load_dataset(
    "coastalcph/multi_eurlex",
    "hr",
    trust_remote_code=True,
    label_level="level_2"
)

# Show dataset structure
print(dataset)

# Show available columns
print(dataset["train"].column_names)


# Show the first example
example = dataset["train"][0]

print("\nFirst example:")
print(example)


# Inspect label information
print("\nLabel features:")
print(dataset["train"].features["labels"])

print("\nAll dataset features:")
print(dataset["train"].features)


# Count how often each EUROVOC label appears
label_counts = Counter()

for example in dataset["train"]:
    label_counts.update(example["labels"])

print("\nEUROVOC label counts:")

label_names = dataset["train"].features["labels"].feature.names

for label_index, count in sorted(label_counts.items()):
    eurovoc_id = label_names[label_index]
    print(f"{eurovoc_id}: {count}")


# Assign one majority legal area to each document
def add_majority_area(example):
    return {
        "majority_area": get_majority_area(
            example["labels"],
            label_names
        )
    }


# Apply the mapping to all dataset splits
dataset = dataset.map(add_majority_area)


# Count legal areas in the training split
area_counts = Counter(dataset["train"]["majority_area"])

print("\nMajority legal area distribution (train):")

# Exclude None values before sorting
mapped_counts = {
    area: count
    for area, count in area_counts.items()
    if area is not None
}

for area, count in sorted(mapped_counts.items()):
    print(f"{area}: {count}")


# Show the number of unmapped or tied documents
print("\nUnmapped or tied documents:", area_counts.get(None, 0))

# Show the total number of training documents
print("Total training documents:", len(dataset["train"]))

import json
from urllib.request import urlopen

# Download official EUROVOC descriptors
url = "https://raw.githubusercontent.com/nlpaueb/multi-eurlex/master/data/eurovoc_descriptors.json"

with urlopen(url) as response:
    eurovoc_descriptors = json.load(response)

print("\nOfficial EUROVOC descriptors:")

for eurovoc_id in label_names:
    descriptor = eurovoc_descriptors.get(eurovoc_id, "NOT FOUND")
    print(f"{eurovoc_id}: {descriptor}")

from datasets import load_dataset_builder

builder = load_dataset_builder(
    "coastalcph/multi_eurlex",
    "hr",
    trust_remote_code=True,
    label_level="level_2"
)

print("\nChecking dataset configuration:")

for key, value in vars(builder.config).items():
    if "label" in key.lower() or "level" in key.lower():
        print(key, ":", value)
