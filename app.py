import os
import logging
from tempfile import NamedTemporaryFile

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from forms import SearchForm
import blast
import config

app = Flask(__name__)
app.config.from_object('config.Config')
Bootstrap(app)

data_config = config.get_data_config(app.config['DATA_CONFIG'])
logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
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

    if request.form['which-form'] == 'blastn':
        program = 'blastn'
        form = form_n
        db_path = data_config.db_blast_n[form_n.search_db.data]
    else:
        program = 'blastp'
        form = form_p
        db_path = data_config.db_blast_p[form_p.search_db.data]

    if not form.validate_on_submit():
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p)

    if form.query_from.data and form.query_to.data:
        qry_fr = int(form.query_from.data) - 1
        qry_to = int(form.query_to.data) - 1
        seq = str(form.sequence.data)[qry_fr:qry_to]
    else:
        seq = form.sequence.data

    with NamedTemporaryFile(mode="w+", delete=False) as query_file:
        query_file.write(seq)

    runner = blast.BlastRunner(program, db_path)
    result = runner.run(query_file)

    os.remove(query_file.name)

    if result is None:
        return render_template('except.html')

    if not result.hits:
        return render_template('nothing_found.html')

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run()
