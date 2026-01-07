
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

model_name = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

# Prompt text 
prompt = """
Please analyze this car lease contract and:
1. List all fees and penalties.
2. Summarize early termination and mileage clauses.
3. Highlight anything unusual or important for the renter.
"""

result = generator(prompt, max_new_tokens=200)

print("\n--- LLM Analysis ---")
print(result[0]['generated_text'])
