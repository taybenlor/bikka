def bold(line):
    answer = []
    for word in line.split():
        if word[0] == word[-1] == '*':
            answer.append('<strong>'+word[1:-1]+'</strong>')
        else:
            answer.append(word)
    return ' '.join(answer)

def underline(line):
    answer = []
    for word in line.split():    
        if word[0] == word[-1] == '_':
            answer.append('<ins>'+word[1:-1]+'</ins>')
        else:
            answer.append(word)
    return ' '.join(answer)

def link(line):
    answer = []
    for word in line.split(): 
        if word.startswith('http://'):
            answer.append('<a href="' + word + '">'+word+'</a>')
        else:
            answer.append(word)
    return ' '.join(answer)
        
def picture(line):
    answer = []
    for word in line.split():
        if word.startswith('!'):
            answer.append('<img scr="'+word+'">')
        else:
            answer.append(word)
    return ' '.join(answer)

def markdown(line):
    line = bold(line)
    line = underline(line)
    line = link(line)
    line = picture(line)
    return line
