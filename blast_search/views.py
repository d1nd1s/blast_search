"Blast search views"

import os
from tempfile import NamedTemporaryFile

from flask import Blueprint, current_app, render_template, redirect, request, url_for

from .forms import BlastNForm, BlastPForm, BlastXForm, TBlastNForm, TBlastXForm
from .models import db, Request
from . import blast


search_bp = Blueprint('search', __name__, url_prefix='/')


@search_bp.route('/', methods=["GET", "POST"])
def index():
    form_n = BlastNForm()
    form_n.search_db.choices = list(current_app.config['BLAST_DB'].blastn.keys())

    form_p = BlastPForm()
    form_p.search_db.choices = list(current_app.config['BLAST_DB'].blastp.keys())

    form_x = BlastXForm()
    form_x.search_db.choices = list(current_app.config['BLAST_DB'].blastx.keys())

    form_tn = TBlastNForm()
    form_tn.search_db.choices = list(current_app.config['BLAST_DB'].tblastn.keys())

    form_tx = TBlastXForm()
    form_tx.search_db.choices = list(current_app.config['BLAST_DB'].tblastx.keys())

    if request.method == 'GET':
        return render_template('index.html', form_blastn=form_n, form_blastp=form_p, form_blastx=form_x,
                               form_tblastn=form_tn, form_tblastx=form_tx)

    if request.form['which-form'] == 'blastn' and form_n.validate_on_submit():
        return process_blastn(form_n)
    elif request.form['which-form'] == 'blastp' and form_p.validate_on_submit():
        return process_blastp(form_p)
    elif request.form['which-form'] == 'blastx' and form_x.validate_on_submit():
        return process_blastp(form_x)
    elif request.form['which-form'] == 'tblastn' and form_tn.validate_on_submit():
        return process_blastp(form_tn)
    elif request.form['which-form'] == 'tblastx' and form_tx.validate_on_submit():
        return process_blastp(form_tx)

    return render_template('index.html', form_blastn=form_n, form_blastp=form_p, form_blastx=form_x,
                           form_tblastn=form_tn, form_tblastx=form_tx)


def process_blastn(form):
    program = 'blastn'
    db_path = current_app.config['BLAST_DB'].blastn[form.search_db.data]
    return process_blast(form, program, db_path)


def process_blastp(form):
    program = 'blastp'
    db_path = current_app.config['BLAST_DB'].blastp[form.search_db.data]
    return process_blast(form, program, db_path)


def process_blastx(form):
    program = 'blastx'
    db_path = current_app.config['BLAST_DB'].blastx[form.search_db.data]
    return process_blast(form, program, db_path)


def process_tblastn(form):
    program = 'tblastn'
    db_path = current_app.config['BLAST_DB'].tblast,[form.search_db.data]
    return process_blast(form, program, db_path)


def process_tblastx(form):
    program = 'tblastx'
    db_path = current_app.config['BLAST_DB'].tblastx[form.search_db.data]
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

    if program == 'blastn':
        params = blast.BlastnParameters(
            max_target_sequences=form.max_target_sequences.data,
            program_selection=form.program_selection.data,
            tax_id=form.tax_id.data,
            tax_id_neg=form.tax_id_neg.data,
            short_query=form.short_query.data,
            e_value=form.e_value.data,
            word_size=form.word_size.data,
            gapopen=form.gapopen.data,
            gapextend=form.gapextend.data,
        )
    elif program == 'blastp':
        params = blast.BlastpParameters(
            max_target_sequences=form.max_target_sequences.data,
            program_selection=form.program_selection.data,
            tax_id=form.tax_id.data,
            tax_id_neg=form.tax_id_neg.data,
            short_query=form.short_query.data,
            e_value=form.e_value.data,
            word_size=form.word_size.data,
            gapopen=form.gapopen.data,
            gapextend=form.gapextend.data,
            matrix=form.matrix.data
        )
    elif program == 'blastx':
        params = blast.BlastxParameters(
            max_target_sequences=form.max_target_sequences.data,
            tax_id=form.tax_id.data,
            tax_id_neg=form.tax_id_neg.data,
            short_query=form.short_query.data,
            e_value=form.e_value.data,
            word_size=form.word_size.data,
            gapopen=form.gapopen.data,
            gapextend=form.gapextend.data,
            matrix=form.matrix.data,
            query_gencode=form.query_gencode.data
        )
    elif program == 'tblastn':
        params = blast.TblastNParameters(
            max_target_sequences=form.max_target_sequences.data,
            tax_id=form.tax_id.data,
            tax_id_neg=form.tax_id_neg.data,
            short_query=form.short_query.data,
            e_value=form.e_value.data,
            word_size=form.word_size.data,
            gapopen=form.gapopen.data,
            gapextend=form.gapextend.data,
            matrix=form.matrix.data
        )
    elif program == 'tblastx':
        params = blast.TblastXParameters(
            max_target_sequences=form.max_target_sequences.data,
            tax_id=form.tax_id.data,
            tax_id_neg=form.tax_id_neg.data,
            short_query=form.short_query.data,
            e_value=form.e_value.data,
            word_size=form.word_size.data,
            matrix=form.matrix.data
        )

    runner = blast.BlastRunner(program, db_path)
    result = runner.run(query_file, params)

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
