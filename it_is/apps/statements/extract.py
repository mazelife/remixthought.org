import nltk
import re
from urllib import urlopen

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