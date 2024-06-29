from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_name = "google/flan-t5-base"
tokenizer = None
model = None

def init_model():
    global tokenizer, model
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        raise

def generate_answer(question, context):
    if not tokenizer or not model:
        raise ValueError("Model not initialized. Call init_model() first.")

    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=100)
        
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return answer
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        raise