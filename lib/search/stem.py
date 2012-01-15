import re

STOP_WORDS = [word.strip() for word in open('lib/search/stopwords.txt','rU').readlines()]
RULES = [tuple(rule.split()) for rule in r"""
([ml])ice           \1ouse
dice                die
(.{3}.*)ing         \1
(.*([bdgnt]))\2ed   \1
(.{3}.*)ied         \1
(.{3}.*)ies         \1y
(.{3}.*)e[sd]       \1
(.{2}.*?[^s])s      \1
(.{3}.*)ly          \1
(.([bdgnt]))\2er    \1
(.{3}.*)er          \1
(.{2}.*)able        \1
(.{3}.*)ability     \1
(.{3}.*)ation        \1
(.{3}.*)ment        \1
(.{3}.*)i[sz]e      \1
(.{3}.*)iful        \1
(.{3}.*)is[tm]      \1
(.{3}.*)[eiy]       \1
""".strip().split('\n')]

# please note: the stemming rules are horrible
# in order to ensure that the stems of computing, computed and compute are all equal,
# they all resolve to comput
# in the same way: liking, liked and like all resolve to lik
# :(

def tokenise_string(s, stop=True):
    """
    given a string s, converts to lowercase, tokenises and removes stopwords
    """

    filter_function = lambda x: x not in STOP_WORDS
    if stop == False:
        filter_function = lambda x: True

    return map(stem, filter(filter_function, [re.sub(r'[^a-z ]', '', word) for word in s.lower().strip().split()])) # uhuhuh!

def stem(word):
    for pattern, sub in RULES:
        base = re.sub('^' + pattern + '$', sub, word)
        if word != base:
            return stem(base)
    return base

