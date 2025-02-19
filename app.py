from flask import Flask, request, render_template, make_response
import re
import pdfkit
import os

app = Flask(__name__)
organized_data = []
column_names = []

# Definir o caminho do executável wkhtmltopdf
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organize', methods=['POST'])
def organize():
    global organized_data
    global column_names
    
    data_input = request.form['dataInput']
    separator_input = request.form['separatorInput']
    fields_input = int(request.form['fieldsInput'])
    add_ranking = 'addRankingColumn' in request.form
    
    column_names = [request.form[f'columnName{i}'] or f'Campo {i}' for i in range(1, fields_input + 1)]
    
    if add_ranking:
        column_names.insert(0, 'Classificação')

    candidates = data_input.split('/')
    
    organized_data = []
    for candidate in candidates:
        regex = re.compile(f'{separator_input}(?=\\s|$)')
        data_array = regex.split(candidate)
        
        if len(data_array) != fields_input:
            return f"Erro: Número de campos em sequência incorreto para o candidato: {candidate}"
        
        organized_data.append(data_array)
    
    if add_ranking:
        organized_data = sorted(organized_data, key=lambda x: float(x[2].replace(',', '.')), reverse=True)
        for rank, row in enumerate(organized_data, start=1):
            row.insert(0, rank)
    
    return render_template('result.html', column_names=column_names, organized_data=organized_data)

@app.route('/generate_pdf')
def generate_pdf():
    global organized_data
    global column_names
    
    html = render_template('pdf_template.html', column_names=column_names, organized_data=organized_data)
    options = {
        'enable-local-file-access': None
    }
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=resultados.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
