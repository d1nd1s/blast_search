import os

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField,\
    TextField, validators, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

MAX_TAR_SEQ = ["Не выбрано", 10, 50, 100, 250, 500, 1000, 5000]
DB_CHOICES = [s.name[:-4] for s in os.scandir('db2') if s.name[-3:] == 'nin']
DB_CHOICES_PROT = [s.name[:-4] for s in os.scandir('dbp') if s.name[-3:] == 'pin']


class SearchForm(FlaskForm):
    sequence = TextAreaField(
        'Последовательность для поиска',
        [validators.length(min=10, message='Минимальная длина строки для поиска: 10 нуклеотидов')],
        render_kw={"rows": 7, "cols": 11})
    query_from = StringField('От', [validators.optional(), validators.length(max=20)])
    query_to = StringField('Дo', [validators.optional(), validators.length(max=20)])
    job_title = TextField('Название запроса')
    max_target_sequences = IntegerField(
        'Максимальное число выдаваемых последовательностей',
        default=10, validators=[NumberRange(
            0, 100, message='Введите число в диапазоне от 0 до 100')])
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')


class BlastnForm(SearchForm):
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            choices=DB_CHOICES, validators=[DataRequired()])


class BlastpForm(SearchForm):
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            choices=DB_CHOICES_PROT, validators=[DataRequired()])
