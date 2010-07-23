import csv
import re
from urllib import urlopen

from django.utils.encoding import force_unicode, DjangoUnicodeDecodeError

import nltk

#---------------------------------------------------------
#       Extract statemnts from a CSV file
#---------------------------------------------------------

def _normlize_file(file_obj):
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
    
def from_csv(file_obj, is_excel=False):
    file_obj = _normlize_file(file_obj)
    kwargs = is_excel and {'dialect': 'excel'} or {}
    reader = csv.reader(file_obj, **kwargs)
    results = []
    for line in reader:
        statement, tag = line[0:2]
        if len(line) >= 2:
            (statement, tag,), problems = _fix_encoding(statement, tag)
            if not statement == '' and not tag == '':
                results.append((statement, tag, problems))
    return results

#---------------------------------------------------------
#       Extract "It Is" statemnts from a body of text.
#---------------------------------------------------------


sentence_detector = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

AFFIRMATIVES = (
    re.compile("it is(?!n't)(?! not)[ ]+"), 
    re.compile("it's (?!not)"),
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
    >>> matcher(AFFIRMATIVES, "It isolates things.")
    False
    >>> matcher(NEGATIVES, "It's not bad.")
    True
    >>> matcher(NEGATIVES, "It isn't fair.")
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