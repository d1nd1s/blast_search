import os
import logging
from tempfile import NamedTemporaryFile

from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap

from forms import SearchForm
from models import db, Request
import blast
import config

app = Flask(__name__)
app.config.from_object('config.Config')
Bootstrap(app)
db.init_app(app)

data_config = config.get_data_config(app.config['DATA_CONFIG'])
logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(app.config['LOG_FILE']),
                        logging.StreamHandler()
                    ])


@app.route('/', methods=["GET", "POST"])
def index():
    form_n = SearchForm()
    form_n.search_db.choices = list(data_config.db_blast_n.keys())

    form_p = SearchForm()
    form_p.search_db.choices = list(data_config.db_blast_p.keys())

    if request.method == 'GET':
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p)

    if request.form['which-form'] == 'blastn' and form_n.validate_on_submit():
        return process_blastn(form_n)
    elif request.form['which-form'] == 'blastp' and form_p.validate_on_submit():
        return process_blastp(form_p)

    return render_template('index.html', form_blastn=form_n, form_blastp=form_p)


def process_blastn(form):
    program = 'blastn'
    db_path = data_config.db_blast_n[form.search_db.data]
    return process_blast(form, program, db_path)


def process_blastp(form):
    program = 'blastp'
    db_path = data_config.db_blast_p[form.search_db.data]
    return process_blast(form, program, db_path)


def process_blast(form, program, db_path):
    if form.query_from.data and form.query_to.data:
        qry_fr = int(form.query_from.data) - 1
        qry_to = int(form.query_to.data) - 1
        seq = str(form.sequence.data)[qry_fr:qry_to]
    else:
        seq = form.sequence.data

    with NamedTemporaryFile(mode="w+", delete=False) as query_file:
        query_file.write(seq)

    params = blast.FormParameters(
        max_target_sequences=form.max_target_sequences.data,
        program_selection=form.program_selection.data,
        tax_id=form.tax_id.data,
        tax_id_neg=form.tax_id_neg.data,
        short_query=form.short_query.data,
        e_value=form.e_value.data,
        word_size=form.word_size.data,
        gapopen=form.gapopen.data,
        gapextend=form.gapextend.data
    )

    runner = blast.BlastRunner(program, db_path)
    result = runner.run(query_file, params)

    search_req = Request(data=result.to_json())
    db.session.add(search_req)
    db.session.commit()

    os.remove(query_file.name)

    if result is None:
        return render_template('except.html')

    return redirect(url_for('search', req_id=search_req.id))


@app.route('/search/<int:req_id>')
def search(req_id):
    search_req = Request.query.get(req_id)
    if search_req is None:
        return render_template('search_id_error.html')

    result = blast.BlastResult.from_json(search_req.data)
    if not result.hits:
        return render_template('nothing_found.html')

    return render_template('result.html', result=result, max_len=60)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run()
