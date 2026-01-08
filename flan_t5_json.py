import json


config = {
    "model_name": "google/flan-t5-small",
    "prompt": {
        "instructions": [
            "List all fees and penalties.",
            "Summarize early termination and mileage clauses.",
            "Highlight anything unusual or important for the renter."
        ],
        "lease_text": "PASTE_THE_EXTRACTED_LEASE_TEXT_HERE"
    }
}

prompt_text = (
    "Please analyze the following car lease contract:\n\n"
    + config["prompt"]["lease_text"]
    + "\n\nTasks:\n"
    + "\n".join(config["prompt"]["instructions"])
)

print("\n--- Prompt Output ---")
print(prompt_text)