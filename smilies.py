def smilies(string):
    faces={":)":"/static/imgs/happy.png",":(":"/static/imgs/sad.png",":D":"/static/imgs/super_happy.png"}
    for emoticon, image in faces.items():
        string=string.replace(emoticon, '<img src="%s" alt="%s">' % (image, image))
    return string
