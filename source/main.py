#!/usr/bin/env python3
"""nlp_dependency_parser:
Create dependency parser diagram and display over http
    Requirements:
        Using spacy, displayc and nltk
    Design/Implementation:
"""
__author__ = "Ramprasad Polana"
__email__ = "rpolana@yahoo.com"
__license__ = "Unlicense: See the accompanying LICENCE file for details"
__copyright__ = "Anti-Copyright Waiver: The author of this work hereby waives all claim of copyright (economic and moral) in this work and immediately places it in the public domain; it may be used, distorted or destroyed in any manner whatsoever without further attribution or notice to the creator."
__date__ = "Jan 2022"
__version__ = "1.0"
__status__ = "Development"

import logging
import os
import pprint
import sys
import argparse
logger = logging.getLogger(__file__)
logger.setLevel('DEBUG')  # ('INFO')
logger.addHandler(logging.StreamHandler())


from flask import Flask, request, render_template
# from flask_ngrok import run_with_ngrok
from flask_wtf import FlaskForm
# from wtformsparsleyjs import StringField, TextAreaField
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
# from wtforms.widgets import TextArea
from wtforms.validators import ValidationError, DataRequired, Length
import secrets
import dependency_parser

STATIC_URL = r'static'
STATIC_FOLDER = r'../static'  # the static content to be kept outside the source code
IMAGES_DIR = r'images'  # this is the subdirectory under STATIC_FOLDER where images are stored
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 100
MIN_TEXT_LENGTH = 3
MAX_TEXT_LENGTH = 5000

app = Flask(__name__, static_url_path=r'/' + STATIC_URL, static_folder=STATIC_FOLDER)  #  + STATIC_URL_PREFIX)
# wtf_csrf_secret_key = secrets.token_hex(16)
wtf_csrf_secret_key = secrets.token_urlsafe(16)
# dynamic key on every startup (login sessions across startups will not work)
app.config['SECRET_KEY'] = wtf_csrf_secret_key
# run_with_ngrok(app)


@app.route('/check')
def check():
    print(request.headers)
    print(request.data)
    print(request.args)
    print(request.form)
    print(request.endpoint)
    print(request.method)
    print(request.remote_addr)
    pprint.pformat(request.__dict__, depth=5)
    return 'nlp_dependency_parser is working..'


@app.route('/greet', methods=('GET', 'POST'))
def greet():
    class GreetUserForm(FlaskForm):
        username = StringField(label='Please enter your name:', validators=[DataRequired(),
                                                                            Length(min=MIN_NAME_LENGTH, max=MAX_NAME_LENGTH, message='Name length must be between %(min)d and %(max)d characters')])
        submit = SubmitField(label='Submit')

    def validate_text(self, text):
        excluded_chars = r"*^+=}{#~|"
        for char in text.data:
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
        svg_filename = dependency_parser.parse(text, os.path.join(STATIC_FOLDER, IMAGES_DIR))
        svg_filename = IMAGES_DIR + r'/' + os.path.basename(svg_filename)
        # svg_filename = os.path.basename(svg_filename)
        logging.getLogger(f'nlp_dependency_parser: displaying dependency tree in file <{svg_filename}>')
        print(f'nlp_dependency_parser: displaying dependency tree in file <{svg_filename}>')
        return render_template("main_page.html", parse_form=parse_form, static_url=STATIC_URL, svg_filename=svg_filename)
    else:
        return render_template("main_page.html", parse_form=parse_form)


if __name__ == '__main__':
    logger.info(f'***Running {sys.argv[0]} with arguments: {sys.argv[1:]}')
    logger.debug(f'**Current working directory: {os.getcwd()}')
    logger.debug(f'**Path for loading python modules: {sys.path}')

    app.debug = True  # turn on in production
    app.run()
