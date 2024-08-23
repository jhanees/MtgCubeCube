from distutils.log import error
from fileinput import filename
import requests
import time
import sys
import shutil
import os.path
from matplotlib import pyplot
from matplotlib import axes
from matplotlib import image

def parseSeperation(str, sep, num):
    items = [""] * num
    for i in range(num):
        ind = str.find(sep)
        if (i == -1):
            break
        else:
            items[i] = str[:i]
            str = str[:(i+len(sep))]

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

def displayList(names, size=1000):
    pics = []
    for i in range(len(names)):
        tind = names[i].find("//")
        if(tind != -1):
            names[i] = names[i][:(tind-1)]
        if (os.path.exists("images/" + names[i] + ".jpg") == False):
            print(names[i])
            time.sleep(0.1)
            x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + names[i])
            url = findAttribute(x.text,"image_uris", "small")
            print(url)
            x = requests.get(url, stream = True)
            file = open("images/" + names[i] + ".jpg", "wb")
            shutil.copyfileobj(x.raw,file)
            file.close()
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

def display(filename, size = 1000):
    if (os.path.exists("archetypes/" + filename) == False):
        print("Filename does not exist")
    else:
        file = open("archetypes/" + filename, "r")
        names = file.readlines()
        file.close()
        displayList(names, size)

def readArchetype(filename):
    if (os.path.exists("archetypes/" + filename) == False):
        print("Filename does not exist")
        return []
    else:
        file = open("archetypes/" + filename, "r")
        names = file.readlines()
        return names

#initializes the ini File
def initCube():
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n;")
    file.close()

#write archetypes into the ini file    
def updateCube(archetypes):
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n")
    for a in archetypes:
        file.write(a + ",\n")
    file.write(";;")
    file.close()

#get archetypes from the ini file
def readCube():
    archetypes = []
    file = open("Cube.ini", "r")
    text = file.read()
    ind = text.find("Archetypes:\n")
    if ind == -1:
        print("Could not initialize archetypes")
    else:
        ind = ind+12
        x = ""
        while(text[ind] != ";"):
            if(text[ind] == ","):
                archetypes.append(x)
                x = ""
                ind = ind + 2
            x = x + text[ind]
            ind = ind + 1
    print(str(archetypes) + ": archetypes loaded")
    return archetypes

def writemode(filename):
    print("Write file mode options:\nstop | stops write file mode and closes the file\n_cardname_ | searches up _cardname_ on scryfall and writes the english name of the card into _filename_ if sucessful")
    file = open("archetypes/" + filename, "w")
    #write file mode
    while(True):
        inputString = input("Write: ")
        if (inputString == "end" or inputString == "stop" or inputString == "q"):
            break
        #searches for card
        x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + inputString)
        object,info = analyseObject(x)
        #if found writes into file
        if(object == "card"):
            print("Card name is " + info)
            file.write(info + "\n")
        else:
            print("Error type is " + info)
            #if not found tries again with exact command if ambiguous
            if(info == "ambiguous"):
                x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString)
                object,info = analyseObject(x)
                if(object == "card"):
                    print("Card name is " + info)
                    file.write(info + "\n")
    #closes file and goes back to default mode
    file.close()

def editmode(filename):
    if (os.path.exists("archetypes/" + filename) == False):
        print("Filename " + filename + "does not exist")
    else:
        file = open("archetypes/" + filename, "r")
        cards = file.readlines()
        for i in range(len(cards)):
            cards[i] = cards[i][:len(cards[i])-1]
        print("Archetype currently consists of " + str(len(cards)) + " cards.")
        file.close()
        print("Edit options:\ndisplay | displays the archetype\nlist | lists the archetype\nremove _cardname_ | removes _cardname from the archetype\nadd _cardname_ | adds _cardname_\nreplace _cardname1_ _cardname2_ | replaces _cardname1_ with _cardname2_\ndone | ends edit mode")
        while(True):
            inputString = input("Edit: ")
            if (inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") ):
                break
            if(inputString.startswith("display") or inputString.startswith("dp")):
                displayList(cards)
            elif(inputString.startswith("list") or inputString.startswith("l")):
                print(cards)
            elif(inputString.startswith("remove ") or inputString.startswith("rm ")):
                i = inputString.find(" ")
                cardname = inputString[(i+1):]
                #searches for card
                x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname)
                object,info = analyseObject(x)
                #if found writes into file
                if(object == "card"):
                    print("Card name is " + info)
                    try:
                        cards.remove(info)
                    except:
                        print("cardname " + info + " not found and thus could not be removed.")
                else:
                    print("Error type is " + info)
                    #if not found tries again with exact command if ambiguous
                    if(info == "ambiguous"):
                        x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString)
                        object,info = analyseObject(x)
                    if(object == "card"):
                        print("Card name is " + info)
                        try:
                            cards.remove(info)
                        except:
                            print("cardname " + info + " not found and thus could not be removed.")
            elif(inputString.startswith("replace ") or inputString.startswith("rp ")):
                i = inputString.find(" ")
                cardname = inputString[(i+1):]
                i = cardname.find(";")
                if (i == -1):
                    print("replace command requires two values seperated by ;")
                else:
                    cardname2 = cardname[(i+1):]
                    cardname1 = cardname[:i]
                    #searches for card
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname1)
                    object1,info1 = analyseObject(x)
                    time.sleep(0.1)
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname2)
                    object2,info2 = analyseObject(x)                
                    #if found writes into file
                    if(object1 == "card" and object2 == "card"):
                        print(info1 + " will be replaced by " + info2 + ".")
                        try:
                            cards.remove(info1)
                            cards.append(info2)
                        except:
                            print("cardname " + cardname + " not found and thus could not be replaced.")
                    else:
                        if(object1 != "card"):
                            print("Error type for first card is " + info1 + ".")
                        if(object2 != "card"):
                            print("Error type for second card is " + info2 + ".")
            elif(inputString.startswith("add ")):
                i = inputString.find(" ")
                cardname = inputString[(i+1):]
                x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname)
                object,info = analyseObject(x)
                if(object == "card"):
                    print("Card name is " + info)
                    cards.append(info)
                else:
                    print("Error type is " + info)
                    #if not found tries again with exact command if ambiguous
                    if(info == "ambiguous"):
                        x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString)
                        object,info = analyseObject(x)
                    if(object == "card"):
                        print("Card name is " + info)
                    cards.append(info)
    file = open("archetypes/" + filename, "w")
    for c in cards:
        file.write(c + "\n")
    file.close()

if __name__ == "__main__":
    #init
    archetypes = []
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("archetypes"):
        os.makedirs("archetypes")
    if not os.path.exists("Cube.ini"):
        initCube()
    else:
        archetypes = readCube()
                
    #state options in console
    print("Options:\n" + 
          "write _filename_ | puts you into write file mode\n" + 
          "edit _filename_ | reads the archetype _filename_ and gives you options to change it\n" + 
          "display _filename_ _size_ | displays pictures of all cards in _filename_, downloads pictures from scryfall if needed. _size_ is optional if you want to only display _size_ pictures at a time\n" + 
          "stop | ends the script\n" +
          "options | displays this menu")
    #listen to commands
    while(True):
        inputString = input("Command: ")
        if (inputString == "stop"):
            break
        #checks for write file mode
        if(inputString.startswith("archetypes")):
            print(archetypes)
        elif(inputString.startswith("options") or inputString.startswith("Options")):
            print("Options:\n" + 
                    "write _filename_ | puts you into write file mode\n" + 
                    "edit _filename_ | reads the archetype _filename_ and gives you options to change it\n" + 
                    "display _filename_ _size_ | displays pictures of all cards in _filename_, downloads pictures from scryfall if needed. _size_ is optional if you want to only display _size_ pictures at a time\n" + 
                    "stop | ends the script\n" +
                    "options | displays this menu")
        elif(inputString.startswith("display ") or inputString.startswith("dp ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            
            #find displaysize if input
            i = inputString.find(" ")
            numStr = "500"
            num = 1000
            if (i != -1):
                numStr = inputString[(i+1):]
                inputString = inputString[:i]
            print("Filename is " + inputString)
            try:
                num = int(numStr)
            except:
                print("bad input!")
                num = 1000
            display(inputString, num)
        elif(inputString.startswith("s ") or inputString.startswith("search ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + inputString)
            object,info = analyseObject(x)
            #if found writes into file
            if(object == "card"):
                print("Card name is " + info)
                result = []
                for a in archetypes:
                    cards = readArchetype(a)
                    for c in cards:
                        if c.startswith(info):
                            result.append(a)
                print(result)
        elif(inputString.startswith("write ")  or inputString.startswith("w ")):
            i = inputString.find(" ")
            filename = inputString[(i+1):]
            print("Filename is " + filename)
            writemode(filename)
        elif(inputString.startswith("edit ")  or inputString.startswith("e ")):
            i = inputString.find(" ")
            filename = inputString[(i+1):]
            print("Filename is " + filename)
            editmode(filename)
    updateCube(archetypes)
        
        
        

    

    
