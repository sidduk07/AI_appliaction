from transformers import pipeline
import torch

# Initialize the model (do this once, outside of the function)
device = 0 if torch.cuda.is_available() else -1
question_generator = pipeline('text-generation', model='gpt2', device=device)

def generate_questions(text, num_questions=5, max_length=100):
    questions = []
    try:
        # Split text into chunks if it's too long
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        for chunk in chunks:
            prompt = f"Generate a question based on this text: {chunk}\nQuestion:"
            generated_text = question_generator(prompt, max_length=50, num_return_sequences=num_questions, temperature=0.7)
            
            for item in generated_text:
                question = item['generated_text'].split("Question:")[-1].strip()
                if question.endswith("?"):
                    questions.append(question)
                
            if len(questions) >= num_questions:
                break
        
        return questions[:num_questions]
    except Exception as e:
        print(f"An error occurred while generating questions: {str(e)}")
        return []

# Example usage
text = "Your long text here..."
generated_questions = generate_questions(text)
for q in generated_questions:
    print(q)