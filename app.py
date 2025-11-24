import pathlib
import time
from flask import Flask, render_template, request, jsonify,redirect, url_for,send_file
import os
import requests
import PyPDF2
from transformers import pipeline
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
import PyPDF2
from flask import Flask, render_template, request, send_file
import re
from generate_doc import generate_rental_agreement
import tempfile
from translate import extract_text_from_pdf,translate_text,save_text_as_pdf
from nlp import generate_response
from qna import get_answer
import json
from correct_sentense import correct_text_with_languagetool
from app3 import  parse_rental_agreement,save_as_json
import json 
from summerize_text import generate_summary
passage=''

app = Flask(__name__)

qa_pipeline = pipeline("question-answering")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def extract_owner_details(passage):
    owner_start = passage.find("Owner:")
    owner_end = passage.find("Tenant:")
    owner_details = passage[owner_start:owner_end].strip()
    return owner_details

def extract_tenant_details(passage):
    tenant_start = passage.find("Tenant:")
    tenant_end = passage.find("Property Details:")
    tenant_details = passage[tenant_start:tenant_end].strip()
    return tenant_details

def extract_terms_conditions(passage):
    terms_start = passage.find("Terms and Conditions:")
    terms_end  = passage.find("[Signature of Owner]")
    terms_conditions = passage[terms_start:terms_end].strip()
    return terms_conditions

@app.route('/')
def index():
    return render_template('index.html')

candidate_questions = [
    "When was this rental agreement executed?",
    "Who is the owner?",
    "What is the permanent address of the owner?",
    "Who is the tenant?",
    "What is the rent?",
    "What is the complete permanent address of the tenant?",
    "Where is the property located?",
    "What are the terms and conditions for renting the property?",
    "When does the rent commence?",
    "What is the monthly rent amount?",
    "What does the rent exclude?",
    "How should the rent be paid?",
    "What is the monthly maintenance charge for?",
    "What are the Tenant's responsibilities regarding elevator and generator costs?",
    "What bills are the Tenant responsible for during the rental period?",
    "What is the amount of the security deposit?",
    "When should the security deposit be paid?",
    "Under what conditions will the security deposit be refunded?",
    "What repairs are the Tenant responsible for?",
    "Who is responsible for major repairs?",
    "Can the Tenant make structural alterations without permission?",
    "What rights does the Owner have regarding inspection of the premises?",
    "What rules and regulations must the Tenant comply with?",
    "Who is responsible for paying taxes and other fees related to the property?",
    "What obligation does the Owner have regarding claims against the Tenant?",
    "How can the Rent Agreement be terminated before the expiry of the tenancy period?",
    "What condition must the Tenant maintain the premises in?",
    "What happens if the Tenant fails to vacate the premises?",
    "What is the process for settling disputes?",
    "What is the requirement regarding registration of the Rent Agreement?",
    "What fittings and fixtures are included in the property?"
]
candidate_questions_embeddings = model.encode(candidate_questions, convert_to_tensor=True)
def answer_question2(question):
    question_embedding = model.encode(question, convert_to_tensor=True)
    
    if len(candidate_questions_embeddings.shape) == 1:
        similarity_scores = util.pytorch_cos_sim(question_embedding.unsqueeze(0), candidate_questions_embeddings.unsqueeze(0))
    else:
        similarity_scores = util.pytorch_cos_sim(question_embedding.unsqueeze(0), candidate_questions_embeddings)
    
    closest_index = similarity_scores.argmax()
    closest_question = candidate_questions[closest_index]
    print(closest_question)
    
    answer = qa_pipeline(question=closest_question, context=passage)
    generated_response = generate_response(closest_question, answer['answer'])
    
    return generated_response if generated_response is not None else answer['answer'],answer['score']



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
    with open('qna.json', 'r') as file:
        legal_data = json.load(file)
    answer = get_answer(message, legal_data)
    
    if answer:
        return answer
    else:
        text, score = answer_question2(message)
        if score > 0.01:
            return text,score
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
            existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'legal.pdf')
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'legal.pdf'))
            return redirect(url_for('chat')) 
    return render_template('upload.html')


@app.route("/api/message", methods=["POST"])
def api_message():
    with open('qna.json', 'r') as file:
        legal_data = json.load(file)
    score = 100
    with open("static/pdf/legal.txt", "r", encoding="utf-8") as file:
        global passage
        passage = file.read()
    message = request.json["message"]
    print("Received message: ", message)
    if "joke" in message.lower():
        r = tell_joke()
        print(r)
        response = jsonify({"message": r})
        response.status_code = 200
        return response
    elif "summerize" in message.lower():
        summary = generate_summary()
        response = jsonify({"message": summary})
        response.status_code = 200
        return response
    elif get_answer(message, legal_data):
        response_message = get_answer(message, legal_data)
        response = jsonify({"message": response_message})
        response.status_code = 200
        return response
    elif "owner details" in message.lower() or "who is the owner" in message.lower() :    
        owner_details = extract_owner_details(passage)
        response = jsonify({"message": owner_details,"score":score})
        response.status_code = 200
        return response
    elif "tenant details" in message.lower() or "who is the tenant" in message.lower() :
        tenant_details = extract_tenant_details(passage)
        response = jsonify({"message": tenant_details,"score":score})
        response.status_code = 200
        return response
    elif "terms and conditions" in message.lower() :
        terms_conditions = extract_terms_conditions(passage)
        response = jsonify({"message": terms_conditions,"score":score})
        response.status_code = 200
        return response
    else:
        response_message,score = getresponse(message)
        response = jsonify({"message": response_message,"score":score})
        response.status_code = 200
        return correct_text_with_languagetool(response)





@app.route('/view')
def rental_agreement():
    file_path = "static/pdf/legal.txt"
    output_file_path = "rental_agreement.json"
    rental_agreement_data = parse_rental_agreement(file_path)
    save_as_json(rental_agreement_data, output_file_path)
    with open('rental_agreement.json', 'r') as file:
        data = json.load(file)
    return render_template('view_info.html', rental_agreement=data)




@app.route("/chat")
def chat():     
    parser = PDFParser()
    txt_filepath = parser("static/pdf/legal.pdf")
    print(f"Extracted text saved to: {txt_filepath}")


    return render_template("chat1.html")




UPLOAD_TRANSLATE = 'static/uploads'
app.config['UPLOAD_TRANSLATE'] = UPLOAD_TRANSLATE

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



UPLOAD_TRANSLATE = 'static/uploads'
app.config['UPLOAD_TRANSLATE'] = UPLOAD_TRANSLATE
@app.route('/translate_upload', methods=['GET', 'POST'])
def translate_upload():
    if request.method == 'POST':
        folder = app.config['UPLOAD_TRANSLATE']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        if 'file' not in request.files:
            return render_template('upload2.html', message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload2.html', message='No selected file')
        if file:
            file.save(os.path.join(app.config['UPLOAD_TRANSLATE'], file.filename))
            filename = file.filename.split('.')[0]
            print(filename)
            return redirect('/translate/'+filename)
    return render_template('upload2.html')


@app.route('/translate/<lang>', methods=['GET'])
def translate_file(lang):
    input_path = os.path.join(app.config['UPLOAD_TRANSLATE'], f'{lang}.pdf')
    output_path = os.path.join(app.config['UPLOAD_TRANSLATE'], f'{lang}_translated.pdf')
    
    text = extract_text_from_pdf(input_path)
    translated_text = translate_text(text, lang, 'en')
    save_text_as_pdf(translated_text, output_path)
    
    return send_file(output_path, as_attachment=True)



@app.route('/get_rent_info')
def get_rent_info():
    return render_template('get_rent_info.html')

@app.route('/generate_document', methods=['POST'])
def generate_document():
    owner_name = request.form['owner_name']
    owner_father_name = request.form['owner_father_name']
    owner_address = request.form['owner_address']
    tenant_name = request.form['tenant_name']
    tenant_father_name = request.form['tenant_father_name']
    location = request.form['location']
    tenant_address = request.form['tenant_address']
    property_address = request.form['property_address']
    rental_period_start = request.form['rental_period_start']
    rental_period_end = request.form['rental_period_end']
    rent_amount = request.form['rent_amount']
    maintenance_charge = request.form['maintenance_charge']
    security_deposit = request.form['security_deposit']
    print("Owner Name:", owner_name)
    print("Owner's Father Name:", owner_father_name)
    print("Owner's Address:", owner_address)
    print("Tenant Name:", tenant_name)
    print("Tenant's Father Name:", tenant_father_name)
    print("Tenant Status:", location)
    print("Tenant's Address:", tenant_address)
    print("Property Address:", property_address)
    print("Rental Period Start:", rental_period_start)
    print("Rental Period End:", rental_period_end)
    print("Rent Amount:", rent_amount)
    print("Maintenance Charge:", maintenance_charge)
    print("Security Deposit:", security_deposit)
    owner_info = {
        "name": owner_name,
        "father_name": owner_father_name,
        "address": owner_address
    }

    tenant_info = {
        "name": tenant_name,
        "father_name": tenant_father_name,
        "work_address": "",  # You need to fill this with appropriate form field data
        "permanent_address": tenant_address
    }

    property_info = {
        "address": property_address
    }
    rental_agreement_doc = generate_rental_agreement(owner_info, tenant_info, property_info,location,rent_amount)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    rental_agreement_doc.save(temp_file.name)

    # Return the file as an attachment for download
    return send_file(temp_file.name, as_attachment=True, download_name='rental_agreement.docx')










@app.route("/chat2")
def chat2():     
    return render_template("chat2.html")

@app.route("/api2/message", methods=["POST"])
def api_message2():
    from llama_ask import query

    message = request.json["message"]
    print("Received message: ", message)
    response = query(message)
    response = jsonify({"message": response})
    response.status_code = 200
    return response



if __name__ == '__main__':
    app.run(port=8080,debug=True)