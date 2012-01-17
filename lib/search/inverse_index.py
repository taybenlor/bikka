from stem import *


import re
import string
import pickle
from pg8000 import DBAPI as sqlite3

FILENAME = 'lib/search/inverse_index.txt'
DATABASE = 'database.sqlitedb'

word_delimeter = re.compile('[,.!?\s+]')

def index_text(loc_id, text, location_type):
    words = tokenise_string(text, False)
#    print words

    word_indices = {}

    for i in xrange(len(words)):
        word = stem(words[i])
        if word != '':
            next_tuple = (loc_id, i, location_type)
            if word in word_indices:
                word_indices[word].append(next_tuple)
            else:
                word_indices[word] = [next_tuple]

#    print word_indices
    return word_indices

def add_text(loc_id, text, location_type):
    inverse_index = pickle.load(open(FILENAME,'r'))
#    print inverse_index
    additional_index = index_text(loc_id, text, location_type)

    for word in additional_index:
        if word in inverse_index:
        	inverse_index[word] += additional_index[word]
        else:
        	inverse_index[word] = list(additional_index[word])

    pickle.dump(inverse_index, open(FILENAME,'w'))

def empty_index():
    pickle.dump({}, open(FILENAME, 'w'))

def create_index():
    """ re-create the index from scratch """
    empty_index()
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('select id, description from posts')
    for _id, desc in cur.fetchall():
        #print _id, desc
        add_text(_id, desc, 'posts')

    cur.execute('select id, description from comments')
    for _id, desc in cur.fetchall():
        #print _id, desc
        add_text(_id, desc, 'comments')

    cur.close()
    conn.close()


def query_inverse_index(query, inverse_index):
    """
    returns a dict of (loc_id, location_type): [(query_token_index, text_position)]
    given a spilt stemmed query
    """

#    print query

    index_query_result = {}

    for i in xrange(len(query)):
    	word = query[i]
#    	print word,
        if word in inverse_index:
            for loc_id, pos, loc_type in inverse_index[word]:
                next_tuple = (i, pos)
                if (loc_id, loc_type) in index_query_result:
                    index_query_result[(loc_id, loc_type)].append(next_tuple)
                else:
                    index_query_result[(loc_id, loc_type)] = [next_tuple]

#    print index_query_result
    return index_query_result

def inverse_index_count():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('select count(*) from posts')

    posts_count = int(cur.fetchone()[0])

    cur.execute('select count(*) from comments')

    comments_count = int(cur.fetchone()[0])

    cur.close()
    conn.close()

    return posts_count + comments_count

#empty_index()
#add_text('0','this is a mat this is a math cat hat laughing cat laugh cat the cat laughed','argument')
#add_text('1','cat dog computer free_time mat the cat rat set birthmark','comment')

#inv = pickle.load(open(FILENAME, 'r'))

#print query_inverse_index(tokenise_string('the cat mat'), inv)
#print query_inverse_index(tokenise_string('zoolander'), inv)
#print inv

def inverse_index():
    inv = pickle.load(open(FILENAME, 'r'))
    return inv
