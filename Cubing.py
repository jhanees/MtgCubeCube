import random 
import requests
import time
import sys
import os.path
from utilFunc import analyseObject, readArchetype, displayList, downloadImage

#get _number_ elements from list
def getElements(list, number):
    elements = []
    if number > len(list):
        print(f"List does not contain enough elements. {str(len(list))} < {str(number)}")
        return []
    for i in range(number):
        ind = random.randrange(0, len(list))
        elements.append(list[ind])
        list.remove(list[ind])
    return elements

def createPacks(cards, packsize=15):
    i = 0
    packs = []
    cubesize = len(cards)
    while(packsize >= len(cards)):
        packs.append(getElements(cards,packsize))
    print(f"Created {str(len(packs))} packs of {str(packsize)} cards each from {str(cubesize)} cards in the cube.")
    return packs, cards

def cubing(packs):
    for p in packs:
        for c in p:
            if(os.path.exists("images/" + c + ".jpg") == False):
                downloadImage(c)
    #print("waiting for players...")
    #listen to join requests and accept players
    
    #
    
    

def readCube(filename):
    file = open("cubes/" + filename, "r")
    text = file.read()
    file.close()
    archetypes = []
    cards = []
    ind = text.find("Cards:\n")
    if ind == -1:
        print("Could not initialize Cubes")
    else:
        ind = ind+7
        x = ""
        while(text[ind] != ";"):
            if(text[ind] == ","):
                cards.append(x)
                x = ""
                ind = ind + 2
            x = x + text[ind]
            ind = ind + 1
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
    print("Cube consists of " + str(len(cards)) + " cards." + str(len(archetypes)) + " archetypes are part of this cube.")
    return cards, archetypes

def writeCube(cards, archetypes, filename):
    file = open("cubes/" + filename, "w")
    file.write("Cards:\n")
    for c in cards:
        file.write(c + "\n")
    file.write(";;")
    file.write("Archetypes:\n")
    for a in archetypes:
        file.write(a + "\n")
    file.write(";;")
    file.close()

def cubemode(filename, archetypes):
    cards = []
    archetypesAdded = []
    if(os.path.exists("cubes/" + filename)):
        cards, archetypesAdded = readCube(filename)
        for i in range(len(cards)):
            cards[i] = cards[i][:len(cards[i])-1]
        print("Cube currently consists of " + str(len(cards)) + " cards.")
    else:
        print("New cube " + filename + " created!")
    print("Cube options:\ndisplay | displays the cube\nlist | lists the cube\nremove _cardname_ | removes _cardname from the cube\nadd _cardname_ | adds _cardname_\nreplace _cardname1_ _cardname2_ | replaces _cardname1_ with _cardname2_\ndone |draft _packsize_ | start drafting with packs of size _packsize_, default is 15.\nends cube mode")
    while(True):
        inputString = input("Cube " + filename + ": ")
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("stop") or inputString.startswith("q ") or inputString.startswith("quit ")):
            break
        if(inputString.startswith("archetypes")):
            print("All archetypes: " + archetypes)
            print("Archetypes added so far: " + archetypesAdded)
        elif(inputString.startswith("display") or inputString.startswith("dp")):
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
            object = ""
            info = ""
            try:
                x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString)
                object,info = analyseObject(x)
            except:
                print("Error occured while contacting scryfall.")
            #if found writes into file
            if(object == "card"):
                print("Card name is " + info)
                try:
                    cards.remove(info)
                except:
                    print("cardname " + info + " not found and thus could not be removed.")
            elif(object == "error"):
                print("Error type is " + info)
                #if not found tries again with exact command if ambiguous
                if(info == "ambiguous"):
                    object = ""
                    info = ""
                    try:
                        x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString)
                        object,info = analyseObject(x)
                    except:
                        print("Error occured while contacting scryfall.")
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
                try:
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname1)
                    object1,info1 = analyseObject(x)
                    time.sleep(0.1)
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname2)
                    object2,info2 = analyseObject(x)
                except:
                    print("Contacting scryfall failed.")
                    object1 = ""
                    object2 = ""
                #if found writes into file
                if(object1 == "card" and object2 == "card"):
                    print(info1 + " will be replaced by " + info2 + ".")
                    try:
                        cards.remove(info1)
                        cards.append(info2)
                    except:
                        print("cardname " + cardname + " not found and thus could not be replaced.")
                else:
                    if(object1 != "card" and object1 != ""):
                        print("Error type for first card is " + info1 + ".")
                    if(object2 != "card" and object2 != ""):
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
        elif(inputString.startswith("include ") or inputString.startswith("i ")):
            i = inputString.find(" ")
            archetype = inputString[(i+1):]
            #find seperator between archetype and size
            i = inputString.find(" ")
            #size equals number of cards to be added. default 10000 equals all
            size = 10000
            if(i != -1):
                sizestr = archetype[(i+1):]
                archetype = archetype[:i]
                try:
                    size = int(sizestr)
                except:
                    print("size could not be resolved.")
                    size = 10000
            if(not archetypes.contains(archetype)):
                print("archetype " + archetype + " could not be found")
            else:
                list = readArchetype(archetype)
                if(len(list) <= size):
                    for e in list:
                        cards.append(e)
                    print("Added " + len(list) + " cards to the cube.")
                else:
                    add = []
                    k = 0
                    for i in range(size):
                        if(random.random() < (size-len(add))/(len(list)-k)):
                            print("Yes " + str((size-len(add))/(len(list)-k)))
                            add.append(i)
                        else:
                            print("No " + str((size-len(add))/(len(list)-k)))
                        k = k+1
                    if(size != len(add)):
                        print("error. " + size + " does not equal " + len(add))
                    for e in add:
                        cards.append(e)
        elif(inputString.startswith("draft")):
            i = inputString.find(" ")
            #packsize equals number of cards par pack. default 15 card pack
            packsize = 15
            if(i != -1):
                packsizestr = archetype[(i+1):]
                try:
                    packsize = int(packsizestr)
                except Exception:
                    print("packsize could not be resolved.")
                    packsize = 15
            packs, rest = createPacks(cards, packsize)
            cubing(packs, rest)
    writeCube(cards, archetypes, filename)    

