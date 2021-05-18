from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, BooleanField, SubmitField, TextField, FileField, validators, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField
from wtforms.widgets import TextArea

DB_CHOICES = ["Не выбрано", "Nucleotide", "WGS", "Reference Genome"]
MAX_TAR_SEQ = ["Не выбрано", 10, 50, 100, 250, 500, 1000, 5000]


class MyForm(FlaskForm):
    sequence = TextAreaField('Введите последовательность', render_kw={"rows": 7, "cols": 11})
    file = FileField('Или выберите файл', [validators.optional()])
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
    max_target_sequences = SelectField('Максимальное число выдаваемых последовательностей',
                                       [validators.optional()], choices=MAX_TAR_SEQ)
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')
    e_value = StringField('')
    # special_check = BooleanField('special')
    submit = SubmitField('Submit')