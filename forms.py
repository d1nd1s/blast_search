from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, BooleanField, IntegerField, SubmitField, TextField, FileField, validators, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange
from wtforms.fields.html5 import EmailField
from wtforms.widgets import TextArea

import os

# DB_CHOICES = ["Не выбрано", "Nucleotide", "WGS", "Reference Genome"]
DB_CHOICES = [l.name[:-4] for l in os.scandir('db2') if l.name[-3:]=='nin']
MAX_TAR_SEQ = ["Не выбрано", 10, 50, 100, 250, 500, 1000, 5000]
DB_CHOICES_PROT = [l.name[:-4] for l in os.scandir('dbp') if l.name[-3:]=='pin']

class SearchForm(FlaskForm):
    sequence = TextAreaField('Последовательность для поиска', [validators.length(min=10, message='Минимальная длина строки для поиска: 10 нуклеотидов')], render_kw={"rows": 7, "cols": 11})
    # file = FileField('Или выберите файл', [validators.optional()])
    # query subrange (a, b)
    query_from = StringField('От', [validators.length(max=20)])
    query_to = StringField('Дo', [validators.optional(), validators.length(max=20)])
    # job title
    job_title = TextField('Название запроса')
    # choose database
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            choices=DB_CHOICES, validators=[DataRequired()])
    # organism (optional)
    # exclude (optional)
    # limit to
    # choose a blast algorithm
    # algorithm parameters (выпадающий список)
    # max_target_sequences = SelectField('Максимальное число выдаваемых последовательностей',
                                       # [validators.optional()], choices=MAX_TAR_SEQ)
    max_target_sequences = IntegerField('Максимальное число выдаваемых последовательностей', default=10, validators=[NumberRange(0, 100, message='Введите число в диапазоне от 0 до 100')])
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')
    # e_value = StringField('')
    # submit = SubmitField('Submit')


class BlastPSearch(FlaskForm):
    sequence = TextAreaField('Последовательность для поиска', [validators.length(min=10, message='Минимальная длина строки для поиска: 10 нуклеотидов')], render_kw={"rows": 7, "cols": 11})
    query_from = StringField('От', [validators.length(max=20)])
    query_to = StringField('Дo', [validators.optional(), validators.length(max=20)])
    job_title = TextField('Название запроса')
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            choices=DB_CHOICES_PROT, validators=[DataRequired()])
    max_target_sequences = IntegerField('Максимальное число выдаваемых последовательностей', default=10, validators=[NumberRange(0, 100, message='Введите число в диапазоне от 0 до 100')])
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')