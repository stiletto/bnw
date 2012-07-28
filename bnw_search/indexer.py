import re
import datetime
import xapian


class Indexer(object):
    """Create search index for passed message and
    comment objects.
    """

    def __init__(self, dbpath, language):
        self.db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)
        self.stemmer = xapian.Stem(language)

    def make_stem_term(self, text):
        term = text.lower()
        term_e = term.encode('utf-8')
        # Max term length is 245 bytes.
        if len(term_e) > 245:
            term = term_e[:245].decode('utf-8', 'ignore')
        return self.stemmer(term)

    WORD_REC = re.compile(r'\w+', re.UNICODE)
    ID = 0
    USER = 1
    DATE = 2
    TYPE = 3
    TAGS_INFO = 4
    DATE_ORIG = 5
    def create_document(self, obj):
        """Get an message or comment object and
        return a tuple of unique term and Xapian
        document representing it.
        """
        doc = xapian.Document()
        text = obj['text']
        doc.set_data(text)
        # Go word by word, stem it and add to the document.
        for index, match in enumerate(self.WORD_REC.finditer(text)):
            doc.add_posting(self.make_stem_term(match.group()), index)
        id_term = 'Q'+obj['id']
        doc.add_term(id_term)
        doc.add_term('A'+obj['user'])
        tags_info = []
        if 'replycount' in obj:
            # Message object.
            doc.add_term('XTYPEm')
            doc.add_value(self.TYPE, 'message')
            for tag in obj['tags']:
                doc.add_term('XTAGS'+self.make_stem_term(tag))
                tags_info.append('*'+tag)
            for club in obj['clubs']:
                doc.add_term('XCLUBS'+self.make_stem_term(club))
                tags_info.append('!'+club)
        else:
            # Comment object.
            doc.add_term('XTYPEc')
            doc.add_value(self.TYPE, 'comment')
        doc.add_value(self.ID, obj['id'])
        doc.add_value(self.USER, obj['user'])
        doc.add_value(self.TAGS_INFO, ' '.join(tags_info))
        date = datetime.datetime.utcfromtimestamp(obj['date'])
        date = date.strftime('%Y%m%d')
        doc.add_value(self.DATE, date)
        doc.add_value(self.DATE_ORIG, str(obj['date']))
        return id_term, doc

    def create_index(self, objs):
        for obj in objs:
            self.db.replace_document(*self.create_document(obj))
        self.db.commit()
