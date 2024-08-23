from distutils.log import error
from fileinput import filename
import requests
import time
import sys
import shutil
import os.path
import random 
from matplotlib import pyplot
from matplotlib import axes
from matplotlib import image
from utilFunc import readArchetype, display, displayList, analyseObject
from Cubing import cubemode

#initializes the ini File
def initStatus():
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n;;\nCubes:\n;;")
    file.close()

#write archetypes into the ini file    
def updateStatus(archetypes, cubes):
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n")
    for a in archetypes:
        file.write(a + ",\n")
    file.write(";;\n")
    file.write("Cubes:\n")
    for c in cubes:
        file.write(c + ",\n")
    file.write(";;")
    file.close()

#get archetypes from the ini file
def initialize():
    archetypes = []
    cubes = []
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
    print(str(len(archetypes)) + " archetypes loaded")
    ind = text.find("Cubes:\n")
    if ind == -1:
        print("Could not initialize Cubes")
    else:
        ind = ind+7
        x = ""
        while(text[ind] != ";"):
            if(text[ind] == ","):
                cubes.append(x)
                x = ""
                ind = ind + 2
            x = x + text[ind]
            ind = ind + 1
    print(str(len(cubes)) + " cubes loaded")
    return archetypes, cubes

def writemode(filename):
    print("Write file mode options:\nstop | stops write file mode and closes the file\n_cardname_ | searches up _cardname_ on scryfall and writes the english name of the card into _filename_ if sucessful")
    file = open("archetypes/" + filename, "w")
    #write file mode
    while(True):
        inputString = input("Write " + filename + ": ")
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
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
        print("Filename " + filename + " does not exist")
    else:
        file = open("archetypes/" + filename, "r")
        cards = file.readlines()
        for i in range(len(cards)):
            cards[i] = cards[i][:len(cards[i])-1]
        print("Archetype currently consists of " + str(len(cards)) + " cards.")
        file.close()
        print("Edit options:\ndisplay | displays the archetype\nlist | lists the archetype\nremove _cardname_ | removes _cardname from the archetype\nadd _cardname_ | adds _cardname_\nreplace _cardname1_ _cardname2_ | replaces _cardname1_ with _cardname2_\ndone | ends edit mode")
        while(True):
            inputString = input("Edit " + filename + ": ")
            if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
                break
            if(inputString.startswith("display") or inputString.startswith("dp")):
                i = inputString.find(" ")
                numStr = "500"
                num = 1000
                if (i != -1):
                    numStr = inputString[(i+1):]
                    inputString = inputString[:i]
                    try:
                        num = int(numStr)
                    except:
                        print("bad input!")
                        num = 1000
                displayList(cards,num)
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
    if not os.path.exists("cubes"):
        os.makedirs("cubes")
    if not os.path.exists("Cube.ini"):
        initStatus()
    else:
        archetypes, cubes = initialize()
                
    #state options in console
    print("Options:\nwrite _filename_ | puts you into write file mode to create the archetype _filename_\nedit _filename_ | reads the archetype _filename_ and gives you options to change it\ndisplay _filename_ _size_ | displays pictures of all cards in _filename_, downloads pictures from scryfall if needed. _size_ is optional if you want to only display _size_ pictures at a time\ncube _cubename_ | puts you into cubemode\nstop | ends the script\n")
    #listen to commands
    while(True):
        inputString = input("Command: ")
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
            break
        #checks for write file mode
        if(inputString.startswith("archetypes")):
            print(archetypes)
        elif(inputString.startswith("cube ") or inputString.startswith("c ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            cubemode(inputString, archetypes)
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
        elif(inputString.startswith("s+ ") or inputString.startswith("search+ ")):
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
            archetypes.add(filename)
        elif(inputString.startswith("edit ")  or inputString.startswith("e ")):
            i = inputString.find(" ")
            filename = inputString[(i+1):]
            print("Filename is " + filename)
            editmode(filename)
    updateStatus(archetypes, cubes)