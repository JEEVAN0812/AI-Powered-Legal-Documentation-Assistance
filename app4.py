from app3 import  parse_rental_agreement,save_as_json
import json 
from flask import Flask, render_template

file_path = "static/pdf/legal.txt"
output_file_path = "rental_agreement.json"
rental_agreement_data = parse_rental_agreement(file_path)
save_as_json(rental_agreement_data, output_file_path)


app = Flask(__name__)

@app.route('/view')
def rental_agreement():
    with open('rental_agreement.json', 'r') as file:
        data = json.load(file)
    return render_template('view_info.html', rental_agreement=data)

if __name__ == '__main__':
    app.run(debug=True)