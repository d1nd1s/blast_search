import os
import subprocess

from scrapy.selector import Selector

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from forms import SearchForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
Bootstrap(app)


@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    if form.query_from.data and form.query_to.data:
        qry_fr = int(form.query_from.data) - 1
        qry_to = int(form.query_to.data) - 1
        seq = str(form.sequence.data)[qry_fr:qry_to]
    else:
        seq = form.sequence.data
    cmd = ['blastn', '-db', 'db/' + form.search_db.data, '-outfmt', '5',
           '-max_target_seqs', str(form.max_target_sequences.data)]
    try:
        sp_run = subprocess.run(cmd,
                                input=seq,
                                capture_output=True,
                                encoding='utf-8',
                                check=True)
    except subprocess.CalledProcessError:
        return render_template('except.html')

    result = Selector(
        text=sp_run.stdout,
        type='xml')
    blast_dict = {c.root.tag: c.xpath('./text()').get().strip() for c in result.xpath('//*')}

    if 'Hsp_midline' not in blast_dict:
        return render_template('nothing_found.html')
    midln = "".join(blast_dict.get('Hsp_midline'))
    data = {
        'query': form.sequence.data,
        'result': blast_dict,
        'db': form.search_db.data,
        'program': blast_dict.get('BlastOutput_program'),
        'query_id': blast_dict.get('BlastOutput_query-ID'),
        'results': [{'name': blast_dict.get('Hit_def'),
                     'def': blast_dict.get('Hit_def'),
                     'evalue': blast_dict.get('Hsp_evalue'),
                     'query_cover': str(round((len(midln.replace(' ', ''))
                                               / len(midln)) * 100)) + '%'}],
        'alignment': [{'Hsp_qseq': blast_dict.get('Hsp_qseq'),
                       'Hsp_hseq': blast_dict.get('Hsp_hseq'),
                       'Hsp_midline': midln}],
        'job_title': form.job_title.data,
        'query_from': form.query_from.data,
        'query_to': form.query_to.data}
    return render_template('result.html', data=data)


if __name__ == '__main__':
    app.run()
