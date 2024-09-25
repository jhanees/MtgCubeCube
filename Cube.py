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
from utilFunc import readArchetype, display, displayList, analyseObject, dropLastLetter, rlinput, updateStatus
from Cubing import cubemode, cubing

#initializes the ini File
def initStatus():
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n;;\nCubes:\n;;")
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
        x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
        object,info = analyseObject(x)
        #if found writes into file
        if(object == "card"):
            print("Card name is " + info)
            file.write(info + "\n")
        else:
            print("Error type is " + info)
            #if not found tries again with exact command if ambiguous
            if(info == "ambiguous"):
                x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                object,info = analyseObject(x)
                if(object == "card"):
                    print("Card name is " + info)
                    file.write(info + "\n")
    #closes file and goes back to default mode
    file.close()

def editArchetypeMode(filename):
    if (os.path.exists("archetypes/" + filename) == False):
        print("Filename " + filename + " does not exist")
    else:
        file = open("archetypes/" + filename, "r")
        cardsPlus = file.readlines()
        cards = list(map(dropLastLetter,cardsPlus))
        print("Archetype currently consists of " + str(len(cards)) + " cards.")
        file.close()
        print("Edit options:\n" + 
              "display | displays the archetype\n" + 
              "list | lists the archetype\n" + 
              "remove _cardname_ | removes _cardname from the archetype\n" + 
              "add _cardname_ | adds _cardname_\n" + 
              "replace _cardname1_ _cardname2_ | replaces _cardname1_ with _cardname2_\n" +
              "done | ends edit mode")
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
                x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
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
                        x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
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
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname1, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                    object1,info1 = analyseObject(x)
                    time.sleep(0.1)
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname2, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
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
                x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                object,info = analyseObject(x)
                if(object == "card"):
                    print("Card name is " + info)
                    cards.append(info)
                else:
                    print("Error type is " + info)
                    #if not found tries again with exact command if ambiguous
                    if(info == "ambiguous"):
                        time.sleep(0.1)
                        x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                        object,info = analyseObject(x)
                    if(object == "card"):
                        print("Card name is " + info)
                        cards.append(info)
        file = open("archetypes/" + filename, "w")
        for c in cards:
            file.write(c + "\n")
        file.close()

def editMode(archetypes, cubes):
    #state options in console
    Options = ["Edit Mode Options:", 
               "write _filename_ | puts you into write file mode to create the archetype _filename_",
               "edit _filename_ | reads the archetype _filename_ and gives you options to change it",
               "display _filename_ [size] | displays pictures of all cards in _filename_, downloads pictures from scryfall if needed. [size] puts number of cards displayed to [size] cards at a time",
               "cube _cubename_ | puts you into cubemode",
               "archetypes | lists all archetypes",
               "options | displays this menu",
               "back | goes back to the main menu",
               "quit | ends the programm"]
    for o in Options:
        print(o)
    #listen to commands
    prefill = ""
    quitBool=False
    while(True):
        #reads line with potential prefill from prior commands
        inputString = rlinput("Command: ", prefill)
        print("")
        #checks if command ends the script
        if (inputString.startswith("q") or inputString.startswith("quit")):
            quitBool=True
            break
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("back")):
            quitBool=False
            break
        #boolean variable to check whether command was recognized or if set to false user gets option to edit input
        recognizedCommand = True
        #check for all command options
        if(inputString.startswith("archetypes") or inputString.startswith("a")):
            print(archetypes)
        elif(inputString.startswith("options") or inputString.startswith("o")):
            for o in Options:
                print(o)
        elif(inputString.startswith("cube ") or inputString.startswith("c ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            cubes = cubemode(inputString, archetypes, cubes)
            for o in Options:
                print(o)
        elif(inputString.startswith("display ") or inputString.startswith("dp ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            #find _size_ if used in input
            i = inputString.find(" ")
            numStr = "500"
            num = 1000
            if (i != -1):
                numStr = inputString[(i+1):]
                archetypePrefix = inputString[:i]
            print("Archetype prefix is " + archetypePrefix)
            try:
                num = int(numStr)
            except:
                print("bad input!")
                num = 1000
            f = []
            for archetype in archetypes:
                if(archetype.startswith(archetypePrefix)):
                    f.append(archetype)
            if(f != []):
                print("Archetypes to display are " + str(f))
            else:
                print("No archetype starting with " + archetypePrefix + " found")
                recognizedCommand = False
            for archetype in f:
                display(archetype, num)
        elif(inputString.startswith("s ") or inputString.startswith("search ")):
            i = inputString.find(" ")
            inputString = inputString[(i+1):]
            x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
            object,info = analyseObject(x)
            #if found writes into file
            if(object == "card"):
                print("Card name is " + info)
                result = []
                for a in archetypes:
                    cards = readArchetype(a)
                    for c in cards:
                        if c == info:
                            result.append(a)
                print(result)
            else:
                recognizedCommand = False
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
            editArchetypeMode(filename)
        else:
            recognizedCommand = False
        if(recognizedCommand == False):
            print("Command not recognized")
            prefill = inputString
        else:
            prefill = ""
    updateStatus(archetypes, cubes)
    return quitBool

def mainMenu(archetypes, cubes):
    options = ("Main Menu Options:\n" + 
            "edit | mode for editing the archetype piles and editing cubes\n" + 
            "host draft | start hosting an online draft[not implemented yet]\n" + 
            "join draft | join an online draft[not implemented yet]\n" + 
            "bot draft | start a bot draft\n" +
            "options | displays this menu\n" +
            "quit | ends this programm")
    print(options)
    while(True):
        inputString = input("Command: ")
        if (inputString.startswith("q")):
            break
        #checks for write file mode
        if(inputString.startswith("o") or inputString.startswith("Options")):
            print(options)
        elif(inputString.startswith("e") or inputString.startswith("edit")):
            quitBool = editMode(archetypes, cubes)
            if(quitBool):
                break
            else:
                print(options)
        elif(inputString.startswith("host draft")  or inputString.startswith("hd")):
            #TODO
            time.sleep(0.1)
        elif(inputString.startswith("join draft")  or inputString.startswith("jd")):
            #TODO
            time.sleep(0.1)
        elif(inputString.startswith("bot draft")  or inputString.startswith("bd")):
            while(True):
                name = input("Which cube would you like to draft?\nPress 1 for a list of all available cubes, otherwise enter the name of the Cube\nCommand:")
                if(name == "1"):
                    print(f"Cubes:{str(cubes)}")
                else:
                    if(name in cubes):
                        cubing(name)
                        break
                    else:
                        print("The name of the cube was not recognized. Please try again.")
if __name__ == "__main__":
    #init
    archetypes = []
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("draftlogs"):
        os.makedirs("draftlogs")
    if not os.path.exists("archetypes"):
        os.makedirs("archetypes")
    if not os.path.exists("cubes"):
        os.makedirs("cubes")
    if not os.path.exists("draftdecks"):
        os.makedirs("draftdecks")
    if not os.path.exists("Cube.ini"):
        initStatus()
    else:
        archetypes, cubes = initialize()
    mainMenu(archetypes, cubes)
    updateStatus(archetypes, cubes)