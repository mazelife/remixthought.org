import csv
from os import rename

from app_settings import CSV_DATA_FILE_PATH
from models import Statement

def export_csv():
    """
    Export a CSV file of all statements to the static directory.
    """
    statements = ((s.text, s.tag.tag) for s in \
        Statement.objects.all().only('text', 'tag'))
    fh = open(CSV_DATA_FILE_PATH + ".tmp", 'w')
    csv_writer = csv.writer(fh)
    for statement, tag in statements:
        # CVS doesn't grok unicode, so we convert entities and encode as UTF-8,
        # which it can handle. 
        statement = unescape(statement).encode('utf-8')
        tag = unescape(tag).encode('utf-8')
        csv_writer.writerow((statement, tag))
    fh.close()
    rename(CSV_DATA_FILE_PATH + ".tmp", CSV_DATA_FILE_PATH)
        

def unescape(text):
    """
    Convert HTML entities to unicode equivalents.
    By Frederick Lundh: effbot.org/zone/re-sub.html#unescape-html
    """
    import re, htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character ref
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1],1))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            #named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)