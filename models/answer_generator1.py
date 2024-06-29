from transformers import pipeline

qa_pipeline = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

def generate_answer(question, context):
    result = qa_pipeline(question=question, context=context)
    return result['answer']