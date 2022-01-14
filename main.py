import logging
import os.path


from flask import Flask, request, render_template
# from flask_ngrok import run_with_ngrok
from flask_wtf import FlaskForm
from wtformsparsleyjs import StringField, TextAreaField
from wtforms import SubmitField
# from wtforms.widgets import TextArea
from wtforms.validators import ValidationError, DataRequired, Length
import secrets
import dependency_parser

IMAGES_DIR = r'images'
STATIC_URL_PREFIX = r'static'
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 100
MIN_TEXT_LENGTH = 3
MAX_TEXT_LENGTH = 5000

app = Flask(__name__, static_url_path=r'/' + STATIC_URL_PREFIX)
# wtf_csrf_secret_key = secrets.token_hex(16)
wtf_csrf_secret_key = secrets.token_urlsafe(16)
# dynamic key on every startup (login sessions across startups will not work)
app.config['SECRET_KEY'] = wtf_csrf_secret_key
# run_with_ngrok(app)


@app.route('/check')
def check():
    return 'nlp_dependency_parser is working..'


@app.route('/greet', methods=('GET', 'POST'))
def greet():
    class GreetUserForm(FlaskForm):
        username = StringField(label='Please enter your name:', validators=[DataRequired(),
                                                                            Length(min=MIN_NAME_LENGTH, max=MAX_NAME_LENGTH, message='Name length must be between %(min)d and %(max)d characters')])
        submit = SubmitField(label='Submit')

    def validate_text(self, text):
        excluded_chars = r"*^+=}{#~|"
        for char in self.text.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} is not allowed in input text.")
    form = GreetUserForm()
    if form.validate_on_submit():
        return f'''<h1> Welcome {form.username.data} </h1>'''
    return render_template('greet.html', form=form)


# @app.route('/', methods=['GET'])
# @app.route('/parse', methods=['GET'])
# def parse_empty():
#     return render_template("main_page.html")


@app.route('/', methods=('GET', 'POST'))
@app.route('/parse', methods=('GET', 'POST'))
def parse():
    class ParseForm(FlaskForm):
        # text = StringField(label='Please enter input text to parse:', widget=TextArea(),
        #                    validators=[DataRequired(), Length(min=MIN_TEXT_LENGTH, max=MAX_TEXT_LENGTH)])
        text = TextAreaField(label='Please enter input text to parse:', validators=[DataRequired(),
                                                                            Length(min=MIN_TEXT_LENGTH, max=MAX_TEXT_LENGTH, message='Text length must be between %(min)d and %(max)d characters')])
        submit = SubmitField(label='Parse')
    parse_form = ParseForm()
    if parse_form.validate_on_submit():
        text = parse_form.text.data
        logging.getLogger(f'nlp_dependency_parser: calling parse with input <{text}>')
        svg_filename = dependency_parser.parse(text)
        svg_filename = IMAGES_DIR + r'/' + os.path.basename(svg_filename)
        logging.getLogger(f'nlp_dependency_parser: displaying dependency tree in file <{svg_filename}>')
        print(f'nlp_dependency_parser: displaying dependency tree in file <{svg_filename}>')
        return render_template("main_page.html", parse_form=parse_form, static_dir=STATIC_URL_PREFIX, svg_filename=svg_filename)
    else:
        return render_template("main_page.html", parse_form=parse_form)


if __name__ == '__main__':
    app.debug = True # TODO: turn off in production
    app.run()
