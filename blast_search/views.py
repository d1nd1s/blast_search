"Blast search views"

import os
from tempfile import NamedTemporaryFile

from flask import Blueprint, current_app, render_template, redirect, request, url_for

from .forms import SearchForm
from .models import db, Request
from . import blast


search_bp = Blueprint('search', __name__, url_prefix='/')


@search_bp.route('/', methods=["GET", "POST"])
def index():
    form_n = SearchForm()
    form_n.search_db.choices = list(current_app.config['BLAST_DB'].blastn.keys())

    form_p = SearchForm()
    form_p.search_db.choices = list(current_app.config['BLAST_DB'].blastp.keys())

    if request.method == 'GET':
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p)

    if request.form['which-form'] == 'blastn' and form_n.validate_on_submit():
        return process_blastn(form_n)
    elif request.form['which-form'] == 'blastp' and form_p.validate_on_submit():
        return process_blastp(form_p)

    return render_template('index.html', form_blastn=form_n, form_blastp=form_p)


def process_blastn(form):
    program = 'blastn'
    db_path = current_app.config['BLAST_DB'].blastn[form.search_db.data]
    return process_blast(form, program, db_path)


def process_blastp(form):
    program = 'blastp'
    db_path = current_app.config['BLAST_DB'].blastp[form.search_db.data]
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

    runner = blast.BlastRunner(program, db_path)
    result = runner.run(query_file)

    search_req = Request(data=result.to_json())
    db.session.add(search_req)
    db.session.commit()

    os.remove(query_file.name)

    if result is None:
        return render_template('except.html')

    return redirect(url_for('search.search', req_id=search_req.id))


@search_bp.route('/search/<int:req_id>')
def search(req_id):
    search_req = Request.query.get(req_id)
    if search_req is None:
        return render_template('search_id_error.html')

    result = blast.BlastResult.from_json(search_req.data)
    if not result.hits:
        return render_template('nothing_found.html')

    return render_template('result.html', result=result, max_len=60)
