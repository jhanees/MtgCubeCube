import os.path
import requests
import time
import shutil
import readline
from matplotlib import pyplot
from matplotlib import axes
from matplotlib import image

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()

def fragmentFormat(xaxis, yaxis, total):
    if(xaxis < 1):
        print("incorrect x input!")
    if(yaxis < 1):
        print("incorrect y input!")
    s = total
    x = 0
    y = 0
    i = 1
    while(x*y < total):
        if i % yaxis == 0:
            x = x+1
        if i % xaxis == 0:
            y = y+1
        i = i+1
    if((y-1)*x >= total):
        return x,y-1
    if(y*(x-2) >= total):
        return x-2,y
    if(y*(x-1) >= total):
        return x-1,y
    return x,y

def dropLastLetter(word):
    return word[:len(word)-1]

def readArchetype(filename):
    if (os.path.exists("archetypes/" + filename) == False):
        print("Filename " + filename + "does not exist")
        return []
    else:
        file = open("archetypes/" + filename, "r")
        namesSpace = file.readlines()
        names = list(map(dropLastLetter,namesSpace))
        return names

#checks whether x is card or error and searches for additional info
def analyseObject(x):
    object = findAttribute(x.text,'object')
    if(object == "error"):
        type = findAttribute(x.text,'type')
        print(x.text)
        return object,type
    if(object == "card"):
        name = findAttribute(x.text,'name')
        return object,name

#checks for value of att within str, searches for subatt after att if subatt is given
def findAttribute(str, att, subatt=None):
    tind = str.find(att)
    tind = str.find('"',tind+1+len(att))
    i = tind + 1
    content = ""
    if(subatt != None):
        tind = str.find(subatt, i)
        tind = str.find('"',tind+1+len(subatt))
        i = tind + 1
        while(str[i] != '"'):
            content += str[i]
            i = i+1
        return content
    else:
        while(str[i] != '"'):
            content += str[i]
            i = i+1
        return content

def downloadImage(name):
    time.sleep(0.1)
    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + name, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
    url = findAttribute(x.text,"image_uris", "small")
    print(url)
    x = requests.get(url, stream = True, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
    file = open("images/" + name + ".jpg", "wb")
    shutil.copyfileobj(x.raw,file)
    file.close()

def displayList(names, size=30):
    pics = []
    for i in range(len(names)):
        tind = names[i].find("//")
        if(tind != -1):
            if (os.path.exists("images/" + names[i][:(tind-1)] + ".jpg") == False):
                print(names[i])
                downloadImage(names[i][:(tind-1)])
        else:
            if (os.path.exists("images/" + names[i] + ".jpg") == False):
                print(names[i])
                downloadImage(names[i])
    for j in range(((len(names)-1)//size)+1):
        size1 = min(size,len(names)-j*size)
        myImage = [None] * size1
        #determine size
        x,y = fragmentFormat(5,2,size1)
        if(x*y < size1):
            print("massive error!")
        fig, axs = pyplot.subplots(((size1-1)//x + 1),x)
        fig.tight_layout(pad=0)
        for i in range(size1):
            tind = names[i].find("//")
            if(tind != -1):
                myImage[i] = image.imread("images/" + names[i+j*size1][:(tind-1)] + ".jpg")
            else:
                myImage[i] = image.imread("images/" + names[i+j*size1] + ".jpg")
            axs[i//x][i % x].set_axis_off()
            axs[i//x][i % x].get_xaxis().set_visible(False)
            axs[i//x][i % x].get_yaxis().set_visible(False)
            axs[i//x][i % x].imshow(myImage[i])
        for i in range(size1,x*y):
            axs[i//x][i % x].set_axis_off()
            axs[i//x][i % x].get_xaxis().set_visible(False)
            axs[i//x][i % x].get_yaxis().set_visible(False)
        fig.tight_layout(pad=0)
        pyplot.show()

def display(filename, size = 30):
    if (os.path.exists("archetypes/" + filename) == False):
        print("$archetypes/" + filename + "$")
        print("Filename does not exist")
    else:
        file = open("archetypes/" + filename, "r")
        namesSpace = file.readlines()
        names = list(map(dropLastLetter,namesSpace))
        file.close()
        displayList(names, size)
