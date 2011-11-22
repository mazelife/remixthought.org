import csv
from os import path
import re
from urllib import urlopen

from django.utils.encoding import force_unicode, DjangoUnicodeDecodeError

import nltk

#---------------------------------------------------------
#       Extract statemnts from a CSV file
#---------------------------------------------------------

_double_line_breaks = re.compile("\n{2,}")
_duble_spaces = re.compile("[ ]{2,}")

def _normalize_file(file_obj):
    """
    Not surprisingly, this is necessary mostly for Excel-produced CSV 
    files. It tries to normalize Win and Mac line endings to UNIX-style
    and replace invalid characters with their HTML entity equivalents.
    """
    from StringIO import StringIO
    contents = file_obj.read()
    contents = contents.replace("\r\n", "\n").replace("\r", "\n")
    fixes = [
        ('\xe2\x80\x99', '&#8217;'), # aposrophe
        ('\xe2\x80\x9c', '&#8220;'), # smart quotes
        ('\xe2\x80\x9d', '&#8221;'),
        ('\xe2\x80\x94', '&mdash;'),
        ('\xd1', '&mdash;')
    ]
    for char, entity in fixes:
        contents = contents.replace(char, entity)    
    return StringIO(contents)

def _fix_encoding(*args):
    problems_encountered = False
    strings = []
    for arg in args:
        try: 
            arg = force_unicode(arg)
        except:
            strings.append(arg.decode("utf8", "ignore"))
            problems_encountered = True
        else:
            strings.append(arg)
    return (strings, problems_encountered,)
    
def from_url(url, default_tag):
    """
    Extract "It is..." sentences from a URL. Returns a list of tuples of the
    form:
        
        (sentence, tag, encoding problems)
        
    ...where ``encoding problems`` is a boolean indicating that there were 
    characters that could not be decoded as UTF-8.
    """
    page_contents =  _normalize_file(urlopen(url)).read()
    page_contents = page_contents
    exists, not_exists = from_text(page_contents)
    records = []
    for sentence in exists:
        statement, problems = _fix_encoding(sentence)
        statement = statement[0]
        # remove linebreaks, double spaces:
        statement  = _double_line_breaks.sub("", statement)
        statement = _duble_spaces.sub(" ", statement)
        records.append((statement, default_tag, problems))
    return records
    
def from_csv(file_obj, is_excel=False):
    """
    Extract "It is..." sentences from a CSV. Returns a list of tuples of the
    form:
        
        (sentence, tag, encoding problems)
        
    ...where ``encoding problems`` is a boolean indicating that there were 
    characters that could not be decoded as UTF-8.
    """    
    file_obj = _normalize_file(file_obj)
    kwargs = is_excel and {'dialect': 'excel'} or {}
    reader = csv.reader(file_obj, **kwargs)
    records = []
    for line in reader:
        statement, tag = line[0:2]
        if len(line) >= 2:
            (statement, tag,), problems = _fix_encoding(statement, tag)
            if not statement == '' and not tag == '':
                records.append((statement, tag, problems))
    return records

#---------------------------------------------------------
#       Extract "It Is" statemnts from a body of text.
#---------------------------------------------------------


def get_sentence_detector():
    # FIXME: This is fucking dumb. There has to be a better way.
    from apps import statements
    pth = path.join(
        path.dirname(statements.__file__), 'english.pickle'
    )
    return nltk.data.load("file:/" + pth)

sentence_detector = get_sentence_detector()

AFFIRMATIVES = (
    re.compile(".*it is(?!n't)(?! not)[ ]+"), 
    re.compile(".*it's (?!not)"),
)
NEGATIVES = ("it is not", "it isn't", "it's not")

def from_text(raw_text):
    """
    >>> raw_test = "It is good. It isn't bad. It's fine. It is not all there."
    >>> from_text(raw_test)
    (['It is good.', "It's fine."], ["It isn't bad.", 'It is not all there.'])
    """
    exists = []
    not_exists = []
    sentences = sentence_detector.tokenize(raw_text.strip())
    for sentence in sentences:
        if matcher(AFFIRMATIVES, sentence):
            exists.append(sentence)
        if matcher(NEGATIVES, sentence):
            not_exists.append(sentence)
    return (exists, not_exists)

def matcher(phrases, sentence):
    """
    >>> matcher(AFFIRMATIVES, "It is good.")
    True
    >>> matcher(AFFIRMATIVES, "It's a goal!")
    True
    >>> matcher(AFFIRMATIVES, "It's not time.")
    False
    >>> matcher(AFFIRMATIVES, "It is not time.")
    False
    >>> matcher(AFFIRMATIVES, "It isn't time.")
    False
    >>> matcher(AFFIRMATIVES, "Everyone agrees that it is a loop.")
    True
    >>> matcher(AFFIRMATIVES, "It isolates things.")
    False
    >>> matcher(NEGATIVES, "It's not bad.")
    True
    >>> matcher(NEGATIVES, "It isn't fair.")
    True
    >>> matcher(NEGATIVES, "Everyone agrees that it isn't a loop.")
    True
    >>> matcher(NEGATIVES, "It is not what you know.")
    True
    >>> matcher(NEGATIVES, "It is good.")
    False
    """
    sentence = sentence.lower()
    for phrase in phrases:
        if hasattr(phrase, 'match'):
            if phrase.match(sentence):
                return True
        else:
            if phrase in sentence:
                return True 
    return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()