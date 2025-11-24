import json
import random
import tensorflow as tf
from transformers import BertTokenizer, TFBertForQuestionAnswering

class QnADataLoader:
    def __init__(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as json_file:
            self.data = json.load(json_file)

    def get_random_qa_pair(self):
        random_qa_pair = random.choice(self.data['questions'])
        return random_qa_pair['question'], random_qa_pair['answer']

def answer_question(question, context, model_name="bert-large-uncased-whole-word-masking-finetuned-squad"):

    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = TFBertForQuestionAnswering.from_pretrained(model_name)

    inputs = tokenizer(question, context, return_tensors='tf', truncation=True, max_length=512)

    outputs = model(inputs)

    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    answer_start = tf.argmax(answer_start_scores, axis=1).numpy()[0]
    answer_end = (tf.argmax(answer_end_scores, axis=1) + 1).numpy()[0]

    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0].numpy())
    answer = tokens[answer_start:answer_end]
    answer = tokenizer.convert_tokens_to_string(answer)

    return answer

def ask_question_and_get_answer(filepath, question):
    with open(filepath, 'r', encoding='utf-8') as file:
        context = file.read()

    answer = answer_question(question, context)
    return question, context, answer

# question = "What is the rent"
# file_path = "static/pdf/legal.txt"
# question, context, answer = ask_question_and_get_answer(file_path, question)
# print("Question:", question)
# print("Context:", context)
# print("Answer:", answer)
