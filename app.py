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
    if form.validate_on_submit():
        if form.data['query_from'] and form.data['query_to']:
            qry_fr = int(form.data['query_from']) - 1
            qry_to = int(form.data['query_to']) - 1
            seq = str(form.data['sequence'])[qry_fr:qry_to]
        else:
            seq = form.data['sequence']
        cmd = ['blastn', '-db', 'db/' + form.data['search_db'], '-outfmt', '5',
               '-max_target_seqs', str(form.data['max_target_sequences'])
               ]
        sp_run = subprocess.run(cmd,
                                input=seq,
                                capture_output=True,
                                encoding='utf-8',
                                check=True)
        result = Selector(
            text=sp_run.stdout,
            type='xml')
        blast_dict = {c.root.tag: c.xpath('./text()').get().strip() for c in result.xpath('//*')}
        if 'Hsp_midline' not in blast_dict:
            return 'Результаты выравнивания не найдены'
        midln = "".join(blast_dict['Hsp_midline'])
        data = {
                'query': form.data['sequence'],
                'result': blast_dict,
                'db': form.data['search_db'],
                'program': blast_dict['BlastOutput_program'],
                'query_id': blast_dict['BlastOutput_query-ID'],
                'results': [{'name': blast_dict['Hit_def'],
                             'def': blast_dict['Hit_def'],
                             'evalue': blast_dict['Hsp_evalue'],
                             'query_cover': str(round((len(midln.replace(' ', ''))
                                                       / len(midln)) * 100)) + '%'}],
                'alignment': [{'Hsp_qseq': blast_dict['Hsp_qseq'],
                               'Hsp_hseq': blast_dict['Hsp_hseq'],
                               'Hsp_midline': midln}],
                'job_title': form.data['job_title'],
                'query_from': form.data['query_from'],
                'query_to': form.data['query_to']}
        return render_template('result.html', data=data)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
