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
from utilFunc import readArchetype, display, displayList, analyseObject, dropLastLetter, rlinput, listToString, getIndexFuzzy, chopItUp, sortArchetypes
from Cubing import cubemode, cubing

#initializes the ini File[deprecated]
def initStatus():
    file = open("Cube.ini", "w")
    file.write("Archetypes:\n;;\nCubes:\n;;")
    file.close()


#get archetypes from the ini file
def initialize():
    archetypesUnsorted = [f for f in os.listdir("archetypes/") if os.path.isfile(os.path.join("archetypes/", f))]
    cubes = [f for f in os.listdir("cubes/") if os.path.isfile(os.path.join("cubes/", f))]
    print(str(len(archetypesUnsorted)) + " archetypes loaded")
    print(str(len(cubes)) + " cubes loaded")
    archetypes = sortArchetypes(archetypesUnsorted)
    return archetypes, cubes

def writearchetypemode(filename):
    print("Write file mode options:\n" +
          "stop | stops write file mode and closes the file\n" + 
          "_cardname_ | searches up _cardname_ on scryfall and writes the english name of the card into _filename_ if sucessful")
    file = open("archetypes/" + filename, "w")
    #write file mode
    while(True):
        inputString = input("Write " + filename + ": ")
        commands = chopItUp(inputString," ")
        command = commands[0]
        if (command == "end" or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
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
              "done | ends edit mode")
        while(True):
            status = 0
            inputString = rlinput("Edit " + filename + ": ")
            commands = chopItUp(inputString," ")
            if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
                break
            if(inputString.startswith("display") or inputString.startswith("dp")):
                if(len(commands) > 1):
                    numStr = commands[1]
                    try:
                        num = int(numStr)
                    except:
                        print("bad input!")
                        num = 1000
                else:
                    num = 1000
                displayList(cards,num)
            elif(inputString.startswith("list") or inputString.startswith("l")):
                print(listToString(cards))
            elif(inputString.startswith("remove ") or inputString.startswith("rm ")):
                cardname = inputString[(inputString.find(" ")+1):]
                #searches for card
                try:
                    ind = int(cardname)
                    if(ind < len(cards)):
                        info = cards[ind]
                        print("Card name is " + info)
                        cards.pop(ind)
                except:
                    ind = getIndexFuzzy(cardname,cards)
                    if(ind != -1):
                        info = cards[ind]
                        print("Card name is " + info)
                        cards.remove(info)
                    else:
                        print("cardname " + cardname + " not found and thus could not be removed.")
            elif(inputString.startswith("add ")):
                cardname = commands[1]
                try:
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                except:
                    print("Contacting scryfall failed.")
                    status = -1
                if(status != -1):
                    object,info = analyseObject(x)
                    if(object == "card"):
                        print("Card name is " + info)
                        cards.append(info)
                    else:
                        print("Error type is " + info)
                        #if not found tries again with exact command if ambiguous
                        if(info == "ambiguous"):
                            try: 
                                x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                                object,info = analyseObject(x)
                            except:
                                print("Contacting scryfall failed.")
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
               "write _filename_ | puts you into write file mode to create the archetype _filename_.",
               "edit _archetypeID_ | reads the archetype _archetypeID_ and gives you options to change it.",
               "display _fileID_ [size] | displays pictures of all cards in _fileID_, downloads pictures from scryfall if needed. [size] puts number of cards displayed to [size] cards at a time",
               "cube _cubeID_ | puts you into cubemode editing _cubeID_. _cubeID_ can be the name or the index in cubelist.",
               "archetypes | lists all archetypes",
               "cubes | lists all cubes",
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
        commands = chopItUp(inputString, " ")
        command = commands[0]
        status = 0
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
            print(listToString(archetypes))
        elif(inputString.startswith("cubes") or inputString.startswith("cs ")):
            print(listToString(cubes))
        elif(inputString.startswith("options") or inputString.startswith("o")):
            for o in Options:
                print(o)
        elif(inputString.startswith("cube ") or inputString.startswith("c ")):
            if(len(commands) > 1):
                cubes = cubemode(commands[1], archetypes, cubes)
                for o in Options:
                    print(o)
            else:
                print("Failed to specify a cubename or index.")
        elif(inputString.startswith("display ") or inputString.startswith("dp ")):
            if(len(commands) > 1):
                archetypePrefix = commands[1]
                #find _size_ if used in input
                if(len(commands) > 2):
                    numStr = commands[2]
                    try:
                        num = int(numStr)
                    except:
                        print("bad input!")
                        num = 1000
                else:
                    num = 1000
                try:
                    ind = int(archetypePrefix)
                except ValueError:
                    ind = getIndexFuzzy(archetypePrefix,archetypes)
                if(ind != -1):
                    archetype = archetypes[ind]
                    print("Archetype to display is " + archetype + ".")
                    display(archetype, num)
                else:
                    print("No archetype starting with " + archetypePrefix + " found")
                    recognizedCommand = False
            else:
                print("Failed to specify an archetype identifier for the archetype to display.")
        elif(inputString.startswith("s ") or inputString.startswith("search ")):
            cardnameprefix = inputString[(inputString.find(" ")+1):]
            try:
                x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardnameprefix, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                object,info = analyseObject(x)
            except:
                print("Contacting scryfall failed.")
                status = -1
            if(status != -1):
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
            filename = commands[1]
            try:
                int(filename)
                print("For compatibility issues numbers are not allowed as archetype names")
            except ValueError:
                print("Filename is " + filename)
                writearchetypemode(filename)
                archetypes.add(filename)
        elif(inputString.startswith("edit ")  or inputString.startswith("e ")):
            nameprefixorindex = commands[1]
            try:
                ind = int(nameprefixorindex)
                if(ind < len(archetypes)):
                    filename = archetypes[ind]
                    print("Filename is " + filename)
                    editArchetypeMode(filename)
                else:
                    print(f"There are only {len(archetypes)} archetypes. Index {ind} out of bounds.")
                    prefill=inputString
            except ValueError:    
                ind = getIndexFuzzy(nameprefixorindex, archetypes)
                if(ind != -1):
                    filename = archetypes[ind]
                    print("Filename is " + filename)
                    editArchetypeMode(filename)
                else:
                    print(f"No archetype starting with {nameprefixorindex} found.")
                    prefill=inputString
        else:
            recognizedCommand = False
        if(recognizedCommand == False):
            print("Command not recognized")
            prefill = inputString
        else:
            prefill = ""
    return quitBool

def mainMenu(archetypes, cubes):
    options = ("Main Menu Options:\n" + 
            "edit | mode for editing the archetype piles and editing cubes\n" + 
            "host draft | start hosting an online draft[not implemented yet]\n" + 
            "join draft | join an online draft[not implemented yet]\n" + 
            "bot draft | start a bot draft\n" +
            "options | displays this menu\n" +
            "quit | ends this programm")
    while(True):
        print(options)
        inputString = input("Command: ")
        if (inputString.startswith("q")):
            break
        #checks for write file mode
        if(inputString.startswith("o") or inputString.startswith("O")):
            print(options)
        elif(inputString.startswith("e") or inputString.startswith("E")):
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
        elif(inputString.startswith("debug")  or inputString.startswith("db")):
            for a in archetypes:
                if (os.path.exists("archetypes/" + a) == False):
                    print("Filename " + a + " does not exist")
                else:
                    file = open("archetypes/" + a, "r")
                    cardsPlus = file.readlines()
                    cards = list(map(dropLastLetter,cardsPlus))
                    file.close()
                    for card in cards:
                        status = 0
                        time.sleep(0.1)
                        try:
                            x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + card, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                        except:
                            print("Contacting scryfall failed.")
                            status = -1
                        if(status != -1):
                            object,info = analyseObject(x)
                            if(object == "card"):
                                if(info != card):
                                    print("Card name is " + info + " and not " + card + " in archetype " + a + ".")
                        else:
                            print("Cardname " + card + " not found.")
        elif(inputString.startswith("bot draft")  or inputString.startswith("bd")):
            done = False
            while(not done):
                name = input("Which cube would you like to draft?\nPress l for a list of all available cubes, otherwise enter the name or index of the Cube\nCommand:")
                if(name == "l"):
                    print(f"Cubes:{listToString(cubes)}")
                else:
                    ind = getIndexFuzzy(name,cubes)
                    if(ind != -1):
                        print("You chose to draft cube " + cubes[ind] + ".")
                        cubing(cubes[ind])
                        done = True
                    else:
                        try:
                            ind = int(name)
                            if(ind < len(cubes)):
                                print("Chosen cube is " + cubes[ind] + ".")
                                cubing(cubes[ind])
                                done = True
                        except:
                            print("The name of the cube was not recognized. Please try again.")
if __name__ == "__main__":
    #init
    archetypes = []
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("draftlogs"):
        os.makedirs("draftlogs")
    if not os.path.exists("draftdecks"):
        os.makedirs("draftdecks")
    if not os.path.exists("archetypes"):
        os.makedirs("archetypes")
    if not os.path.exists("cubes"):
        os.makedirs("cubes")
    archetypes, cubes = initialize()
    mainMenu(archetypes, cubes)