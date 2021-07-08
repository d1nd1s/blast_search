import os
from tempfile import NamedTemporaryFile


from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from forms import BlastnForm, BlastpForm
import blast

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
Bootstrap(app)


@app.route('/', methods=["GET", "POST"])
def index():
    form_n = BlastnForm()
    form_p = BlastpForm()

    if request.method == 'GET':
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p)

    if request.form['which-form'] == 'blastn':
        program = 'blastn'
        form = form_n
        db_path = 'db/'
    else:
        program = 'blastp'
        form = form_p
        db_path = 'dbp/'

    if not form.validate_on_submit():
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p)

    if form.query_from.data and form.query_to.data:
        qry_fr = int(form.query_from.data) - 1
        qry_to = int(form.query_to.data) - 1
        seq = str(form.sequence.data)[qry_fr:qry_to]
    else:
        seq = form.sequence.data

    query_file = NamedTemporaryFile(mode="w+", delete=False)
    query_file.write(seq)
    query_file.close()

    db_file = db_path + form.search_db.data

    runner = blast.BlastRunner(program, db_file)
    result = runner.run(query_file)

    os.remove(query_file.name)

    if result is None:
        return render_template('except.html')

    if not result.hits:
        return render_template('nothing_found.html')

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run()
