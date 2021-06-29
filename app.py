﻿import os

from scrapy.selector import Selector

# os.chdir('/home/dina/PycharmProjects/blast_search')
import subprocess

from flask import Flask, render_template, redirect, session, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

import subprocess

import xml.etree.ElementTree as ET
from forms import SearchForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
Bootstrap(app)


# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'txt', 'fa', 'fasta'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        # input_bytes = form.data['sequence'].decode('utf8')
        if form.data['query_from'] and form.data['query_to']:
            lb = int(form.data['query_from']) - 1
            rb = int(form.data['query_to']) - 1
            seq = form.data['sequence'][lb:rb]
        else:
            seq = form.data['sequence']
        cmd = ['blastn', '-db', 'db/' + form.data['search_db'], '-outfmt', '5',
               '-max_target_seqs', str(form.data['max_target_sequences'])
               ]
        sp_run = subprocess.run(cmd,
                                input=seq,
                                capture_output=True,
                                encoding='utf-8')
        result = Selector(
            text=sp_run.stdout,
            type='xml')
        dict = {c.root.tag: c.xpath('./text()').get().strip() for c in result.xpath('//*')}
        # s = {(k, v) for (k, v) in dict.items() if v}
        a = "".join(dict['Hsp_midline'])
        data = {'query': form.data['sequence'], 'result': dict, 'db': form.data['search_db'],
                'program': dict['BlastOutput_program'], 'query_id': dict['BlastOutput_query-ID'],
                'results': [{'name': dict['Hit_def'], 'def': dict['Hit_def'], 'evalue': dict['Hsp_evalue'],
                             'query_cover': str(round((len(a.replace(' ','')) / len(a)) * 100)) + '%'}],
                'alignment': [{'Hsp_qseq': dict['Hsp_qseq'], 'Hsp_hseq': dict['Hsp_hseq'], 'Hsp_midline': a}],
                'job_title': form.data['job_title'],
                'query_from': form.data['query_from'],
                'query_to': form.data['query_to'],
                }
        return render_template('result.html', data=data)
    return render_template('index.html', form=form)


# [{'name': i, 'def': i, 'id': } for i in dict['Hit_def']]
# [{'a': 1, 'b': 2, 'id':'aasdasd'}, {'a':3, 'b':4, 'id':'sdfsdf'}]
# }

# Hit_def - описание
# Hsp_qseq - последовательность которую ищем
# Hsp_hseq - то что нашлось
# Hsp_midline - разделитель

# def allowed_file(filename):
#     return '.' in filename and
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# @app.route('/login', methods=["GET", "POST"])
# def login():
#     form = MyForm()
#     if form.validate_on_submit():
#       pass
#     return return
#     # def upload_file():
#     #     if request.method == 'POST':
#     #         # check if the post request has the file part
#     #         if 'file' not in request.files:
#     #             flash('No file part')
#     #             return redirect(request.url)
#     #         file = request.files['file']
#     #         # if user does not select file, browser also submit an empty part without filename
#     #         if file.filename == '':
#     #             flash('No selected file')
#     #             return redirect(request.url)
#     #         if file and allowed_file(file.filename):
#     #             filename = secure_filename(file.filename)
#     #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     #             return redirect(url_for('uploaded_file',
#     #                                     filename=filename))
#     #     return

#     if form.validate_on_submit():
#         session['sequence'] = form.sequence.data
#         if not session['sequence']:
#             session['sequence'] = form.file.data
#         session['job_title'] = form.job_title.data
#         session['query_from'] = form.query_from.data
#         session['query_to'] = form.query_to.data
#         session['search_db'] = form.search_db.data
#         session['max_target_sequences'] = form.max_target_sequences.data
#         session['short_query'] = form.short_query.data
#         return redirect(url_for('success'))
#     return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run()


# blastn -db /path/to/blastdb -reward 1 -penalty -5 -gapopen 3 -gapextend 3 -dust yes -soft_masking true -evalue 700 -searchsp 1750000000000 -query file.fa -outfmt 6 -out file.format6.out
