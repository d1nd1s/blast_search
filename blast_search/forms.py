from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField,\
    TextField, validators, TextAreaField, SelectField
from wtforms.validators import InputRequired, NumberRange


class SearchForm(FlaskForm):
    sequence = TextAreaField(
        'Последовательность для поиска',
        [validators.length(min=10, message='Минимальная длина строки для поиска: 10 нуклеотидов')],
        render_kw={"rows": 7, "cols": 11})
    query_from = IntegerField('От', validators=[NumberRange(min=0)])
    query_to = IntegerField('Дo', validators=[NumberRange(min=0)])
    job_title = TextField('Название запроса')
    max_target_sequences = IntegerField(
        'Максимальное число выдаваемых последовательностей',
        default=10, validators=[NumberRange(
            0, 100, message='Введите число в диапазоне от 0 до 100')])
    short_query = BooleanField('Короткий запрос (запрос длиной до 30)')
    search_db = SelectField('База данных, в которой будет производиться поиск',
                            validators=[InputRequired()])
