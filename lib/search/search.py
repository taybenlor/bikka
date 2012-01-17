import math
from pg8000 import DBAPI as sqlite3
import os.path
import pickle

from stem import *
from inverse_index import *

DATABASE_LOC = "database.sqlitedb"

ARGUMENT = 'posts'
COMMENT = 'comments'

MAX_SNIPPET_LENGTH = 150
MAX_SURROUNDING_LENGTH = 2
ELLIPSES = '... '

class SearchResult(object):
    """
    Represents a single result in a site search.
    """

    def __init__(self, title, snippet, _id, _type):
        """
        Creates a new SearchResult with a given document title, snippet, database id and type.
        """
        self._title = title
        self._snippet = snippet
        self._id = _id
        if _type not in [ARGUMENT, COMMENT]:
            raise ValueError('Not a valid value for SearchResult type')
        self._type = _type

    def title(self):
        """
        Returns the result's title.
        """
        return self._title

    def snippet(self):
        """
        Returns the result's snippet.
        """
        return self._snippet

    def id(self):
        """
        Returns the result's id in the database.
        """
        return self._id

    def type(self):
        """
        Returns the result's type, corresponding to its table in the database. Can be either ARGUMENT or COMMENT.
        """
        return self._type

    def __repr__(self):
        t = str(self._title)
        sn = str(self._snippet)

        return t + "\n" + ('=' * len(t)) + '\n' + sn + '\n'

def search(query_string):
    """
    performs a search based on the query_string provided.
    tokenisation and stemming is done within the function.
    """
    # tokenise the query string
    tokens = tokenise_string(query_string)

    # get documents index
    documents = query_inverse_index(tokens, inverse_index())
    documents_count = inverse_index_count()

    # rank these documents
    ranked = rank(tokens, documents, documents_count)

    # for each of these documents, get the post title, snippet text and post ID
    results = []
    for doc_id, doc_type in ranked:
        # TODO: get shit from the database
        #post_identifier = 0
        post_title, post_snippet = extract_snippets(documents, doc_id, doc_type)

        result = SearchResult(post_title, post_snippet, doc_id, doc_type)
        results.append(result)

    # return list of results
    return results

def dummy_search():
   """
   A dummy search to test with.
   """
   results = []
   results.append(SearchResult('Is banana bread a cake?', '...banana bread is...', 0, ARGUMENT))
   results.append(SearchResult('Are tabs better than spaces?', '...but tabs are...', 1, ARGUMENT))
   results.append(SearchResult('Of course vim is superior!', "...I need a text editor, not an OS...", 0, COMMENT))
   results.append(SearchResult("Backpacks are carried, it's obvious!", "...you're all wrong...", 1, COMMENT))
   return results

def get_documents():
    """
    stub for getting documents from the index
    """
    return {
            #(0, ARGUMENT): [(0,3), (1,1)],
            #(1, ARGUMENT): [(1,1)]
            (0, ARGUMENT): [(1,1), (0,3), (2,6)],
            (1, ARGUMENT): [(2,1), (0,3)],
            (2, ARGUMENT): [(1,1), (2,4)],
            (3, ARGUMENT): []
    }



NOT_RANKED = -1
def score(query, document, documents, documents_count):
    """
    query - list of stemmed words
    document - data from the index
    """
    #print "docs"
    #print documents
    #print "enddocs"
    # to calculate the score: TF(term, document) * IDF(term, documents)
    # do this for each term in the query
    total_tf_idf = 0
    term_id = 0

    #print document
    document_id, document_type = document.keys()[0]
    if len(document.values()[0]) == 0:
        return NOT_RANKED
    terms_id_query, terms_pos_document = zip(*document.values()[0])

    for term in query:
        # calculate the tf
        tf = terms_id_query.count(term_id)

        # calculate the idf
        term_doc_count = 0
        for doc in documents.values():
            if len(filter(lambda t: t[0]==term_id, doc)) > 0:
                term_doc_count += 1
        #for doc in documents.values():
        #    term_ids = zip(*doc)
        #    if term_id in term_ids:
        #    	term_doc_count += 1

        if term_doc_count > 0:
            idf = math.log(float(documents_count) / float(term_doc_count))
        else:
            continue

        # calculate the tf-idf
        tf_idf = float(tf) * idf

        # add it to the total
        total_tf_idf += tf_idf

        term_id += 1

    return total_tf_idf

def rank(query, documents, documents_count):
    """
    query - the list of keywords in your search (tokenise and stem first!)
    documents - the dictionary of documents
    """
    ranked = []
    for document, contents in documents.items():
        doc_score = score(query, {document: contents}, documents, documents_count)
        if doc_score != NOT_RANKED:
            ranked.append((doc_score, document))
    print ranked
    return [doc[1] for doc in sorted(ranked, key=lambda x: x[0], reverse=True)]

def extract_snippets(index_data, loc_id, loc_type):
    """
    given index_data, returns a tuple of (title, snippets) that correspond
    to the input data
    """

    conn = sqlite3.connect(DATABASE_LOC)
    cur = conn.cursor()

    #get posts and comments from database
    #print loc_type, loc_id

    #query_string = "SELECT title, description FROM %s WHERE id = ?" % str(loc_type)
    if loc_type == ARGUMENT:
    	query_string = "SELECT title, description FROM posts WHERE id = ?"
        cur.execute(query_string, (str(loc_id),))
    else:
    	query_string = "SELECT description FROM comments WHERE id = ?"
    	cur.execute(query_string, (str(loc_id),))

    results = cur.fetchall()

#    print "OMNOMNOM"
#    print results
#    print index_data

    # TODO: should it be comment's title or post's title
    if len(results) > 0:
        #title, text = results[0]

        # link title
        if loc_type == ARGUMENT:
        	title = '<a href="/argument/%d">%s</a>' % (loc_id, results[0][0])
        	text = results[0][1]
        else:
        	cur.execute("SELECT post_id FROM comments WHERE id=?", (str(loc_id),))
        	post_id = int(cur.fetchone()[0])

        	cur.execute("SELECT title FROM posts WHERE id=?", (str(post_id),))
        	title = cur.fetchall()[0][0]
        	title = '<a href="/argument/%d">%s</a>' % (post_id, title)
        	text = results[0][0]

        snippets = []
        total_length = 0

        text = text.split()
#       print text

        cur_pos = 0
        matches = index_data[(loc_id, loc_type)]
  #      print "DRINKING IT IS LIKE DRIVING A FAST CAR"
 #       print matches
        while cur_pos < len(matches) and total_length < MAX_SNIPPET_LENGTH:
            cur_snippet = ''
            temp, actual = matches[cur_pos]
#            print actual
            for i in xrange(actual - MAX_SURROUNDING_LENGTH, actual + MAX_SURROUNDING_LENGTH):
                if i < 0 or i >= len(text):
                    continue
                elif i == actual:
                    cur_snippet += "<em>" + text[i] + "</em> "
                else:
                    cur_snippet += text[i] + " "

            snippets += cur_snippet + ELLIPSES
            total_length += len(cur_snippet) + len(ELLIPSES)
            cur_pos += 1

    conn.close()

    snippets = ''.join(snippets)
    return title, snippets

def run_all_the_tests():
    search_string = 'COMIC SANS'
    inv = pickle.load(open('inverse_index.txt','r'))
#    print inv

    q = query_inverse_index(tokenise_string(search_string), inv)
#    print q
    snips = list(extract_snippets(q, 1, ARGUMENT))
    snips[1] = ''.join(snips[1])
    snips = tuple(snips)
#    print snips

# these are crappy test functions
if __name__ == '__main__':
    search_string = 'COMIC SANS'
    for res in search(search_string):
        print res
