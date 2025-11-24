import os
import requests
import PyPDF2
from flask import Flask, render_template, request, jsonify, redirect, url_for
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer
from language_tool_python import LanguageTool
import spacy
import json
from difflib import SequenceMatcher

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')


# Load the JSON file containing questions and answers
with open('qna.json', 'r') as file:
    legal_data = json.load(file)

qa_pipeline = pipeline("question-answering")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

with open("static/pdf/legal.txt", "r", encoding="utf-8") as file:
    passage = file.read()

language_tool = LanguageTool('en-US')
nlp = spacy.load("en_core_web_sm")


def find_most_similar(question, legal_data):
    max_similarity = 0
    most_similar_question = ""
    for item in legal_data['questions']:
        similarity = SequenceMatcher(None, question.lower(), item['question'].lower()).ratio()
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_question = item['question']
    return most_similar_question, max_similarity


def get_answer(question, legal_data):
    most_similar_question, similarity = find_most_similar(question, legal_data)
    if similarity > 0.95:
        for item in legal_data['questions']:
            if item['question'] == most_similar_question:
                return item['answer']
    else:
        return None


def generate_response(question, answer):
    question_doc = nlp(question)
    key_nouns = [token.text for token in question_doc if token.pos_ == "NOUN"]
    key_verbs = [token.text for token in question_doc if token.pos_ == "VERB"]
    response = f"The {' '.join(key_nouns)} {' '.join(key_verbs)} {answer}"
    return response


def correct_questions(questions):
    corrected_questions = []
    for question in questions:
        corrected_question = language_tool.correct(question)
        corrected_questions.append(corrected_question)
    return corrected_questions


def answer_question2(questions):
    corrected_candidate_questions = correct_questions(questions)
    for idx, corrected_question in enumerate(corrected_candidate_questions):
        if corrected_question.lower() in questions[idx].lower():
            answer = qa_pipeline(question=questions[idx], context=passage)
            generated_response = generate_response(questions[idx], answer['answer'])
            return generated_response if generated_response is not None else answer['answer'], answer['score']
    return None, None


class PDFParser:
    def __init__(self):
        pass

    def __call__(self, filepath: str) -> str:
        with open(filepath, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                text += page_text
        txt_filepath = f"{filepath[:-4]}.txt"
        with open(txt_filepath, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

        return txt_filepath


def getresponse(message):
    answer = get_answer(message, legal_data)
    if answer:
        return answer
    else:
        text, score = answer_question2(message)
        if score is not None and score > 0.01:
            return text
        else:
            return "Sorry, I couldn't fetch the data"


def tell_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        setup = data["setup"]
        punchline = data["punchline"]
        joke = f"{setup} {punchline}"
        return joke
    else:
        return "Sorry, I couldn't fetch a joke at the moment."


UPLOAD_FOLDER = 'static/pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message='No selected file')
        if file:
            try:
                existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'legal.pdf')
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'legal.pdf'))
                return redirect(url_for('chat'))
            except Exception as e:
                return render_template('upload.html', message='Error occurred while uploading file.')
    return render_template('upload.html')


@app.route("/api/message", methods=["POST"])
def api_message():
    message = request.json["message"]
    print("Received message: ", message)

    if "joke" in message.lower():
        r = tell_joke()
        print(r)
        response = jsonify({"message": r})
        response.status_code = 200
        return response

    corrected_message = language_tool.correct(message)
    print("Corrected message: ", corrected_message)

    response_message = getresponse(corrected_message)
    if response_message is None:
        return jsonify({"message": "Sorry, I couldn't fetch the data"})
    else:
        response = jsonify({"message": response_message})
        response.status_code = 200
        return response


@app.route("/chat")
def chat():
    parser = PDFParser()
    txt_filepath = parser("static/pdf/legal.pdf")
    print(f"Extracted text saved to: {txt_filepath}")
    return render_template("chat.html")


UPLOAD_TRANSLATE = 'static/uploads'
app.config['UPLOAD_TRANSLATE'] = UPLOAD_TRANSLATE

if __name__ == '__main__':
    app.run(port=8080, debug=True)
