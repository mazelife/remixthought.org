import random
import re

from nltk.corpus import words, gutenberg

from django.db import IntegrityError, transaction
from django.template.defaultfilters import slugify

from statements import extract
from statements.color import ColorPicker
from statements.models import Statement, Tag

"""
Some helper functions for creating test data sets.
"""

_linebreak = re.compile('[\n\r]+')

def clear_tags():
    for tag in Tag.objects.all():
        tag.delete()

def clear_statements():
    for statement in Statement.objects.all():
        statement.delete()


def create_random_tags(count=100):
    """
    This function uses the corpora available in ``nltk`` to create a randomized 
    set of tags.
    """
    all_words = words.words('en')
    selected_words = []
    picker = ColorPicker(reset=True)
    colors = picker._get_colors()
    while count > 0:
        word = random.choice(all_words)
        selected_words.insert(0, word)
        all_words.remove(word)
        count += -1
    del all_words
    for word in selected_words:
        color = colors.next()
        tag = Tag(slug=slugify(word), tag=word, color=color)
        tag.save()

@transaction.commit_manually
def create_random_statements(count=50):
    """
    This function scans the ``nltk`` Project Gutenberg dataset, extracts random
    sentences containing some form of "it is" and tags them with a random tag.
    NB: This thing can take a while.
    """
    created_count = 0
    tags = Tag.objects.order_by("?")
    gutenberg_files = gutenberg.fileids()
    random.shuffle(gutenberg_files)
    for file_name in gutenberg_files:
        exists, not_exists = extract.from_text(gutenberg.raw(file_name))
        for sentence in [_linebreak.sub(' ', s) for s in exists]:
            if created_count == count:
                break
            statement = Statement(text = sentence, tag = random.choice(tags))
            try:
                statement.save()
                created_count += 1
                transaction.commit()
            except IntegrityError:
                transaction.rollback()

def reset_data(tag_count=100, statement_count=100):
    """
    Erase everything and recreate some randomized data.
    NB: This thing can take a long while.
    """
    clear_tags()
    clear_statements()
    create_random_tags(count=tag_count)
    create_random_statements(count=statement_count)
