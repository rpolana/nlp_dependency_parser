import logging
import os.path

# from IPython.display import display, Image
from pathlib import Path
# import asyncio
# import threading
import logging

# spaCy Code Initialization:
import spacy
import spacy.cli
from spacy import displacy
import benepar
# from benepar.spacy_plugin import BeneparComponent
# from benepar import BeneparComponent, NonConstituentException
import nltk
from nltk import Tree
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import *

IMAGES_DIR = r'static\images'


def exception_retry(e_type, f, on_exception_f, max_retries=1, logger=None):
    import time
    for i in range(max_retries + 1):
        try:
            time.sleep(0.3)
            f()
        except e_type as exc:
            if logger is not None:
                logger.warn(f'exception_retry: Exception {exc}')
            on_exception_f()
        else:
            break
    else:
        if logger is not None:
            logger.error(f'exception_retry: all {max_retries} retries failed with exceptions!!')
        raise()

# exception_retry(OSError,
#                 lambda: nlp = spacy.load('en_core_web_sm'); True,
#                 lambda: spacy.cli.download('en_core_web_sm'), max_retries = 1, logging.getLogger())


def setup_spacy():
    global nlp
    # spacy initialization
    try:
        nlp = spacy.load('en_core_web_sm')
        add_pipe_benepar(nlp)
    except OSError as e:
        # download('en')
        spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
        add_pipe_benepar(nlp)
    return nlp


def setup():
    # NLTK Code Initialization:
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')
    try:
        nltk.data.find('wordnet')
    except LookupError:
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    # initialize benepar
    try:
        add_pipe_benepar(nlp)
    except Exception as e:
        benepar.download('benepar_en3')
        add_pipe_benepar(nlp)

    return setup_spacy()

def add_pipe_benepar(nlp):
    if spacy.__version__.startswith('2'):
        nlp.add_pipe(benepar.BeneparComponent("benepar_en3"))
        logging.getLogger().info(f'benepar_en3 component added to spacy {spacy.__version__} pipeline')
    else:
        nlp.add_pipe("benepar", config={"model": "benepar_en3"})
        logging.getLogger().info(f'benepar_en3 model added to spacy {spacy.__version__} pipeline')


nlp = None
spacy_doc = None
spacy_sentences = None



p_stemmer = PorterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()


def tokenization(input_text, tool='spacy'):
    global spacy_doc, nlp
    if tool == 'spacy':
        # spaCy
        if spacy_doc is None:
            spacy_doc = nlp(input_text)
        spacy_tokens = [token.text for token in spacy_doc]
        return spacy_tokens
    elif tool == 'nltk':
        # nltk
        nltk_tokens = word_tokenize(input_text)
        return nltk_tokens
    else:
        print('tokenization(): ERROR: unsupported tool specified: ', tool)
        return []


def lemmatization(input_text, tool='spacy', spacy_doc=None, nltk_tokens=None):
    global p_stemmer, wordnet_lemmatizer
    global spacy_doc, nlp
    if tool == 'spacy':
        # spaCy
        if spacy_doc is None:
            spacy_doc = nlp(input_text)
        spacy_lemmas = [token.lemma_ for token in spacy_doc]
        return spacy_lemmas
    elif tool == 'nltk':
        # NLTK
        if nltk_tokens is None:
            nltk_tokens = tokenization(input_text, tool)
        # nltk_stems = [p_stemmer.stem(word) for word in nltk_tokens]
        nltk_lemmas = [wordnet_lemmatizer.lemmatize(word) for word in nltk_tokens]
        return nltk_lemmas
    else:
        print('lemmatization(): ERROR: unsupported tool specified: ', tool)
        return []


def remove_stopwords(input_text, tool = 'spacy', spacy_lemmas=None, nltk_lemmas=None):
    global spacy_doc, nlp
    if tool == 'spacy':
        def spacy_lexeme(word):
            lexeme = nlp.vocab[word]
            return lexeme.is_stop == False
        spacy_filtered = [word for word in spacy_lemmas if spacy_lexeme(word)]
        return spacy_filtered
    elif tool == 'nltk':
        nltk_stop_words = set(stopwords.words("english"))
        nltk_filtered = [word for word in nltk_lemmas if word not in nltk_stop_words]
        return nltk_filtered
    else:
        print('remove_stopwords(): ERROR: unsupported tool specified: ', tool)
        return []


def remove_punctuation(input_text, tool = 'spacy', spacy_filtered=None, nltk_filtered=None):
    punctuations = "?:!.,;"
    if tool == 'spacy':
        result = [word for word in spacy_filtered if not word in punctuations]
        return result
    elif tool == 'nltk':
        result = [word for word in nltk_filtered if not word in punctuations]
        return result
    else:
        print('remove_punctuation(): ERROR: unsupported tool specified: ', tool)
        return []

def get_POS(input_text, tool='spacy', spacy_doc=None, nltk_tokens=None):
    global spacy_doc, nlp
    if tool == 'spacy':
        # spaCy
        if spacy_doc is None:
            spacy_doc = nlp(input_text)
        spacy_pos = [(token, token.pos_, token.tag_, '=>',token.dep_,'=>',token.head.text)  for token in spacy_doc]
        return spacy_pos
    elif tool == 'nltk':
        if nltk_tokens is None:
            nltk_tokens = tokenization(input_text, tool)
        nltk_pos = pos_tag(nltk_tokens)
        return nltk_pos
    else:
        print('get_POS(): ERROR: unsupported tool specified: ', tool)
        return []


# Note: doesn't work for the last sentence in a document.
# The bug will be fixed in a new release of benepar, shortly
def sentences_to_dict(span, idx=0):
    if len(span) == 1:
        res = str(span)
    else:
        res = {}
        for i, child_span in enumerate(span._.children):
            res.update(sentences_to_dict(child_span, i))

    labels = list(span._.labels)
    if len(span) == 1:
        labels.append(span[0].tag_)

    for label in reversed(labels[1:]):
        res = {"0/" + label: res}

    res = {str(idx) + "/" + labels[0]: res}
    return res


def spacy_tok_format(tok):
    return "_".join([tok.orth_, tok.tag_])


def spacy_doc_to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(spacy_tok_format(node), [spacy_doc_to_nltk_tree(child) for child in node.children])
    else:
        return spacy_tok_format(node)


# async def displayc_serve(spacy_doc):
def displayc_serve(spacy_doc):
    import socketserver
    free_port = 0
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
        try:
            displacy.serve(spacy_doc, style='dep', host="localhost", port=free_port)
        except:
            with socketserver.TCPServer(("localhost", 0), None) as s2:
                free_port = s2.server_address[1]
            displacy.serve(spacy_doc, style='dep', host="localhost", port=free_port)


def process_text(input_text, input_number, unique_file_suffix):
    print(f'***Input text {input_number}: ')
    print(input_text)
    global nlp, spacy_sentences
    if nlp is None:
        nlp = setup_spacy()
    spacy_doc = nlp(input_text)
    spacy_tokens = tokenization(input_text, 'spacy')
    print('Spacy Tokens:')
    print(spacy_tokens)
    nltk_tokens = tokenization(input_text, 'nltk')
    print('NLTK Tokens:')
    print(nltk_tokens)

    spacy_pos = get_POS(input_text, tool='spacy', spacy_doc=spacy_doc)
    print('Spacy POS:')
    print(spacy_pos)
    # displacy_thread = threading.Thread(target=displayc_serve, args=[spacy_doc])
    # displacy_thread.start()
    svg = displacy.render(spacy_doc, style='dep', jupyter=False, options={'distance': 80})  # , style="dep")
    svg_filename = os.path.join(IMAGES_DIR, f'displayc_{input_number}_{unique_file_suffix}.svg')
    with Path(svg_filename).open("w", encoding="utf-8") as fh:
        print(f'Saving svg file of displacy render into {svg_filename}')
        fh.write(svg)
    [(spacy_doc_to_nltk_tree(sent.root) if isinstance(spacy_doc_to_nltk_tree(sent.root), str) else spacy_doc_to_nltk_tree(sent.root).pretty_print()) for sent in spacy_doc.sents]
    spacy_sentences = list(spacy_doc.sents)
    print('Spacy sentences:')
    for s in spacy_sentences:
        print(s._.parse_string)
        print(s._.labels)
        if len(list(s._.children)) > 0:
            print(list(s._.children)[0])
    if len(list(spacy_doc.sents)) > 0:
        print(sentences_to_dict(list(spacy_doc.sents)[0]))

    nltk_pos = get_POS(input_text, tool='nltk', nltk_tokens=nltk_tokens)
    print('NLTK POS:')
    print(nltk_pos)

    spacy_lemmas = lemmatization(input_text, 'spacy', spacy_doc=spacy_doc)
    print('Spacy Lemmas:')
    print(spacy_lemmas)
    nltk_lemmas = lemmatization(input_text, 'nltk', nltk_tokens=nltk_tokens)
    print('NLTK Lemmas:')
    print(nltk_lemmas)

    spacy_filtered = remove_stopwords(input_text, tool = 'spacy', spacy_lemmas=spacy_lemmas)
    print('Spacy Stop-words Removed:')
    print(spacy_filtered)
    nltk_filtered = remove_stopwords(input_text, tool = 'nltk', nltk_lemmas=nltk_lemmas)
    print('NLTK Stop-words Removed:')
    print(nltk_filtered)

    spacy_filtered = remove_punctuation(input_text, tool = 'spacy', spacy_filtered=spacy_filtered)
    print('Spacy Stop-words and Punctuations Removed:')
    print(spacy_filtered)
    nltk_filtered = remove_punctuation(input_text, tool = 'nltk', nltk_filtered=nltk_filtered)
    print('NLTK Stop-words and Punctuations Removed:')
    print(nltk_filtered)
    return svg_filename


def parse(input_text):
    input_number = 1
    # import tempfile
    # unique_file_suffix = next(tempfile._get_candidate_names()) # required to ensure output files created run to run will not conflict
    import uuid
    unique_file_suffix = uuid.uuid4().hex # required to ensure output files created run to run will not conflict
    return process_text(input_text, input_number, unique_file_suffix)
