from transformers import BertTokenizer, BertForQuestionAnswering
import torch
import json

# Load your data from the JSON file
with open('qna.json', 'r') as file:
    data = json.load(file)

# Prepare the training data
train_data = []
for qa_pair in data['questions']:
    question = qa_pair['question']
    answer = qa_pair['answer']
    train_data.append({'question': question, 'context': answer})

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

inputs = tokenizer([example['question'] for example in train_data], [example['context'] for example in train_data], padding=True, truncation=True, return_tensors='pt')

optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
model.train()
for epoch in range(3): 
    optimizer.zero_grad()
    outputs = model(**inputs)
    print("Outputs:", outputs)  # Debugging
    if outputs is None:
        raise ValueError("Model outputs are None.")
    loss = outputs.loss
    print("Loss:", loss)  # Debugging
    if loss is None:
        raise ValueError("Loss is None.")
    loss.backward()
    optimizer.step()
    print(f'Epoch {epoch+1}, Loss: {loss.item()}')

model.save_pretrained('fine_tuned_bert')

def answer_question(question, context):
    inputs = tokenizer.encode_plus(question, context, return_tensors='pt')
    start_scores, end_scores = model(**inputs)
    start_index = torch.argmax(start_scores)
    end_index = torch.argmax(end_scores)
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][start_index:end_index+1]))
    return answer

question = "What is a rental agreement?"
context = "A rental agreement is a legal contract between a landlord and a tenant, outlining the terms and conditions of renting a property."
answer = answer_question(question, context)
print("Answer:", answer)
