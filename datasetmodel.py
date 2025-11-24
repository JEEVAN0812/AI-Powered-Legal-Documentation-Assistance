import json
import torch
from datasets import Dataset
from transformers import BertForQuestionAnswering, BertTokenizer, Trainer, TrainingArguments

# Load dataset from qna.json
with open('qna.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Extract questions and corresponding answers
questions = [qna['question'] for qna in dataset['questions']]
answers = [qna['answer'] for qna in dataset['questions']]

# Create a training dataset
train_dataset = Dataset.from_dict({"question": questions, "context": answers, "id": range(len(questions))})

# Initialize BERT model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForQuestionAnswering.from_pretrained(model_name)

# Tokenize the training data
def prepare_train_features(examples):
    # If 'context' is a list of strings, join them into a single string
    if isinstance(examples["context"], list):
        context = " ".join(examples["context"])
    else:
        context = examples["context"]

    tokenized_examples = tokenizer(
        text=examples["question"],
        text_pair=context,  # Use 'context' as text_pair
        truncation="only_second",  # Truncate the context if needed
        padding="max_length",
        max_length=512,
        return_token_type_ids=True,
    )
    
    # Find start and end token positions of the answer within the tokenized context
    answer_tokens = tokenizer.tokenize(examples["context"])  # Use 'context' for answer_tokens
    answer_start_idx = -1
    answer_end_idx = -1
    
    for i in range(len(tokenized_examples["input_ids"])):
        if tokenized_examples["input_ids"][i:i+len(answer_tokens)] == tokenizer.convert_tokens_to_ids(answer_tokens):
            answer_start_idx = i
            answer_end_idx = i + len(answer_tokens) - 1
            break

    tokenized_examples["start_positions"] = answer_start_idx
    tokenized_examples["end_positions"] = answer_end_idx
    
    return tokenized_examples

# Process the dataset with the tokenization function
train_dataset = train_dataset.map(
    prepare_train_features,
    batched=True,
    remove_columns=["question", "context"]
)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./bert_qa",
    overwrite_output_dir=True,
    num_train_epochs=2,
    per_device_train_batch_size=8,
    save_steps=500,
    save_total_limit=2,
    prediction_loss_only=True,
)

# Instantiate Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
)

# Fine-tune BERT for question answering
trainer.train()

# Save the fine-tuned model
model_path = './fine_tuned_bert_qa'
model.save_pretrained(model_path)

# Example of using the fine-tuned model for question answering
def answer_question(question, context):
    inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    # Perform inference
    with torch.no_grad():
        start_scores, end_scores = model(**inputs)

    # Find the tokens with the highest start and end scores
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores) + 1  # Get the last token

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

# Example usage of the fine-tuned model
context = "A rental agreement is a legal contract between a landlord and a tenant, outlining the terms and conditions of renting a property."
question = "What is a rental agreement?"
print(answer_question(question, context))
