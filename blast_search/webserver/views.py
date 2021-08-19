"Blast search views"

import requests

from flask import Blueprint, current_app, render_template, redirect, request, url_for

from blast_search.blast import blast
from blast_search.models import BlastType, Status
from blast_search import request_data
from .forms import SearchForm


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
    blast_type = BlastType.BLASTN
    return process_blast(form, blast_type)


def process_blastp(form):
    blast_type = BlastType.BLASTP
    return process_blast(form, blast_type)


def process_blast(form, blast_type):
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

    req = request_data.BlastSearchRequest(blast_query=form.sequence.data,
                                          blast_type=blast_type,
                                          db_name=form.search_db.data,
                                          params=params)

    url = current_app.config['BLAST_CONTROLLER_URL'] + request_data.BLAST_SEARCH_URL
    resp = requests.post(url, json=req.to_json())

    if not resp.ok:
        return render_template('except.html')

    search_id = resp.json()["search_id"]

    return redirect(url_for('search.search', req_id=search_id))


@search_bp.route('/search/<int:req_id>')
def search(req_id):
    url = current_app.config['BLAST_CONTROLLER_URL'] + request_data.BLAST_SEARCH_URL + f'/{req_id}'
    
    try:
        resp = requests.get(url)

        if not resp.ok:
            return render_template('search_id_error.html')
    except:
        return render_template('internal_error.html')

    search_req = resp.json()
    search_req['status'] = Status(search_req['status'])

    if search_req['status'] == Status.SUCCESS:
        blast_result = search_req.result

        if not blast_result.hits:
            return render_template('nothing_found.html')

        return render_template('result.html', result=blast_result, max_len=60)
    
    return render_template('pending_search.html', request=search_req)
