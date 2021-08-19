from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, \
    TextField, validators, TextAreaField, SelectField, StringField
from wtforms.validators import InputRequired, NumberRange, Optional


class SearchForm(FlaskForm):
    sequence = TextAreaField(
        'Последовательность для поиска',
        [validators.length(min=10, message='Минимальная длина строки для поиска: 10 нуклеотидов')],
        render_kw={"rows": 7, "cols": 11})
    query_from = IntegerField('От', validators=[Optional(), NumberRange(min=0)])
    query_to = IntegerField('Дo', validators=[Optional(), NumberRange(min=0)])
    job_title = TextField('Название запроса')
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            validators=[InputRequired()])
    max_target_sequences = IntegerField(
        'Максимальное число выдаваемых HSP',
        default=10, validators=[NumberRange(
            0, 100, message='Введите число в диапазоне от 0 до 100')])
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')
    e_value = IntegerField(
        'Expect Threshold',
        default=10.0, validators=[NumberRange(
            0, 100, message='Введите число в диапазоне от 0 до 100')])
    word_size = SelectField('Word Size', default=11, choices=[16, 20, 24, 28, 32, 48, 64, 128, 256])
    # HSP_range_max = IntegerField('HSP max range',
    #                              validators=[Optional(), NumberRange(min=0)])
    tax_id = StringField('Tax ID', validators=[Optional(), NumberRange(min=0)])
    tax_id_neg = StringField('Tax ID Negative', validators=[Optional(), NumberRange(min=0)])


class BlastNForm(SearchForm):
    program_selection = SelectField('Программа', default='megablast', choices=['megablast', 'blastn', 'dc-megablast'])
    gapopen = IntegerField('Gap Open', default=5)
    gapextend = IntegerField('Gap Extend', default=2)


class BlastPForm(SearchForm):
    program_selection = SelectField('Программа', default='blastp', choices=['blastp', 'blastp-fast', 'blastp-short'])
    matrix = SelectField('Matrix', default='BLOSUM62', choices=['PAM30', 'PAM70', 'PAM250', 'BLOSUM62', 'BLOSUM45',
                                                                'BLOSUM50', 'BLOSUM90'])
    gapopen = IntegerField('Gap Open', default=5)
    gapextend = IntegerField('Gap Extend', default=2)


class BlastXForm(SearchForm):
    query_gencode = IntegerField('Генетический код', default=1)
    matrix = SelectField('Matrix', default='BLOSUM62', choices=['PAM30', 'PAM70', 'PAM250', 'BLOSUM62', 'BLOSUM45',
                                                                'BLOSUM50', 'BLOSUM90'])
    gapopen = IntegerField('Gap Open', default=5)
    gapextend = IntegerField('Gap Extend', default=2)


class TBlastNForm(SearchForm):
    matrix = SelectField('Matrix', default='BLOSUM62', choices=['PAM30', 'PAM70', 'PAM250', 'BLOSUM62', 'BLOSUM45',
                                                                'BLOSUM50', 'BLOSUM90'])
    gapopen = IntegerField('Gap Open', default=5)
    gapextend = IntegerField('Gap Extend', default=2)


class TBlastXForm(SearchForm):
    matrix = SelectField('Matrix', default='BLOSUM62', choices=['PAM30', 'PAM70', 'PAM250', 'BLOSUM62', 'BLOSUM45',
                                                                'BLOSUM50', 'BLOSUM90'])
