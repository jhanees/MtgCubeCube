import random 
import requests
import time
import sys
import os.path
from utilFunc import analyseObject, readArchetype, displayList, downloadImage, dropLastLetter, draft

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
    while(packsize <= len(cards)):
        packs.append(getElements(cards,packsize))
    print(f"Created {str(len(packs))} packs of {str(packsize)} cards each from {str(cubesize)} cards in the cube.")
    return packs, cards

def cubing(packs):
    playernumberStr = input("Choose number of players:")
    try:
        playernumber = int(playernumberStr)
        if(playernumber < 2):
            print("Can't draft with fewer than 2 players. Number of players set to 8 by default.")
            playernumber = 8
    except:
        playernumber = 8
        print("Couldn't parse input. Number of players set to 8 by default.")
    #we first implement botdraft
    draftroundnumStr = input("Choose number of draft rounds:")
    try:
        draftroundnum = int(draftroundnumStr)
        if(draftroundnum < 1):
            print("Can't draft fewer than 1 pack. Number of packs set to 3 by default.")
            draftroundnum = 3
    except:
        draftroundnum = 8
        print("Couldn't parse input. Number of packs set to 3 by default.")
    if(draftroundnum * playernumber > len(packs)):
        print("Drafting with " + str(playernumber) + " players for " + str(draftroundnum) + " rounds requires " + str(draftroundnum * playernumber) + " packs but there are only " + str(len(packs)) + " packs.")
        return
    yourname = input("\nChoose a Draftername for yourself:")
    print("Your chosen name is \"" + yourname + "\".")
    players = []
    players.append(("local",yourname,[]))
    i=0
    while(len(players) < playernumber):
        players.append(("bot","Bot N°" + str(i),[]))
        i = i + 1
    draft(packs,players,draftroundnum)

    #print("waiting for players...")
    #listen to join requests and accept players
    
    #
    
def instantiate(archetypesAdded):
    cards = []
    for (a,n) in archetypesAdded:
        archetypeCards = readArchetype(a)
        if(archetypeCards != []):
            if((n >= len(archetypeCards)) or (n == -1)):
                for card in archetypeCards:
                    cards.append(card)
            else:
                addIndices = random.sample(range(0,len(archetypeCards)),n)
                for i in addIndices:
                    cards.append(archetypeCards[i])
        else:
            print("Archetype \"" + a + "\" could not be identified. We will skip it.")
    return cards

def readCube(filename):
    file = open("cubes/" + filename, "r")
    linesSpace = file.readlines()
    if(linesSpace[0] == "lazy Cube\n"):
        cubetype = 1
    else:
        cubetype = 0
    ind = linesSpace.index("Cards:\n")
    cardsSpace = []
    if ind == -1:
        print("Could not initialize Cards")
    else:
        done = False
        while(done == False):
            ind = ind + 1
            if(ind == len(linesSpace)):
                print("failed to resolve cube correctly. Semicolon missing.")
                break
            if(linesSpace[ind].startswith(";")):
                done = True
            else:
                cardsSpace.append(linesSpace[ind])
    cards = list(map(dropLastLetter,cardsSpace))
    try:
        ind = linesSpace.index("Archetypes:\n")
    except:
        print(str(linesSpace))
    archetypesSpace = []
    if ind == -1:
        print("Could not initialize archetypes")
    else:
        done = False
        while(done == False):
            ind = ind + 1
            if(ind == len(linesSpace)):
                print("failed to resolve cube correctly. Semicolon missing.")
                break
            if(linesSpace[ind].startswith(";")):
                done = True
            else:
                archetypesSpace.append(linesSpace[ind])
    archetypes = list(map(dropLastLetter,archetypesSpace))
    archetypesAdded = []
    for a in archetypes:
        ind = a.find(" ")
        if(ind != -1):
            try:
                cardnumber = int(a[(ind+1):])
            except:
                print("bad input!")
                cardnumber = -1
            archetype = a[:ind]
            archetypesAdded.append((archetype, cardnumber))
        else:
            archetypesAdded.append((a, -1))
    if(cubetype == 0):
        print("This Cube consists of " + str(len(cards)) + " cards and " + str(len(archetypes)) + " archetypes are part of this cube.")
    if(cubetype == 1):
        totalcardnumber = 0
        for (a,n) in archetypesAdded:
            if(n != -1):
                totalcardnumber = totalcardnumber + n
            else:
                totalcardnumber = totalcardnumber + len(readArchetype(a))
        print("This is a lazy Cube consisting of " + str(len(archetypesAdded)) + " archetypes which add up to a total of " + str(len(cards) + totalcardnumber) + " yet to be determined cards.")
    return cubetype, cards, archetypesAdded

def writeCube(cubetype, cards, archetypes, filename):
    file = open("cubes/" + filename, "w")
    if cubetype == 0:
        file.write("eager Cube\n")
    if cubetype == 1:
        file.write("lazy Cube\n")
    file.write("Cards:\n")
    for c in cards:
        file.write(c + "\n")
    file.write(";;\n")
    file.write("Archetypes:\n")
    for (a,n) in archetypes:
        if(n != -1):
            file.write(a + " " + str(n) + "\n")
        else:
            file.write(a + "\n")
    file.write(";;")
    file.close()

def cubemode(filename, archetypes, cubes):
    cards = []
    archetypesAdded = []
    cubetype = 0
    if(os.path.exists("cubes/" + filename)):
        cubetype, cards, archetypesAdded = readCube(filename)
    else:
        print("New cube " + filename + " created!")
        a = input("\nWhich Cube type do you want this cube to be? Type 0 for a cube with a specific cardlist and 1 for a Cube which randomly selects cards from specified archetypes every time it is drafted. \nCommand:")
        if(a.startswith("1")):
            cubetype = 1
        elif(a.startswith("0")):
            cubetype = 0
        else:
            print("input could not be parsed. Selcting the first option by default.")
            cubetype = 0
        cubes.append(filename)
    Options = ["Cube " + filename + " options:", 
               "display | displays the cube",
               "list | lists the cube",
               "archetypes | displays list of all archetypes and all archetypes in the cube"
               "addcard _cardname_ | adds _cardname_",
               "addarchetype _archetype_ [_cardnumber_] | adds _cardnumber_ cards from _archetype_ to the cube. _cardnumber_ is all by default."
               "remove _cardname_ | removes _cardname from the cube",
               "replace _cardname1_ _cardname2_ | replaces _cardname1_ with _cardname2_",
               "draft _packsize_ | start drafting with packs of size _packsize_, default is 15.\nends cube mode",
               "options | displays this menu",
               "back | goes back to the main menu",
               "quit | ends the programm"]
    for o in Options:
        print(o)
    while(True):
        inputString = input("Cube " + filename + ": ")
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("back") or inputString.startswith("q ") or inputString.startswith("quit ")):
            break
        if(inputString.startswith("archetypes")):
            print("All archetypes: " + str(archetypes))
            print("Archetypes added so far: " + str(archetypesAdded))
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
        elif(inputString.startswith("addcard ") or inputString.startswith("ac ")):
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
                    x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                    object,info = analyseObject(x)
                if(object == "card"):
                    print("Card name is " + info)
                    cards.append(info)
        elif(inputString.startswith("addarchetype ") or inputString.startswith("aa ")):
            i = inputString.find(" ")
            archetypename = inputString[(i+1):]
            i = archetypename.find(" ")
            cardnumber = 1000
            if(i != -1):
                cardnumberStr = archetypename[(i+1):]
                archetypename = archetypename[:i]
                try:
                    cardnumber = int(cardnumberStr)
                except:
                    print("bad input!")
                    cardnumber = 1000
            if((archetypename,) in archetypesAdded):
                print("archetype is already in the cube. Another copy will be added anyway.")
            archetypeCards = readArchetype(archetypename)
            if(archetypeCards != []):
                if(cardnumber >= len(archetypeCards)):
                    if(cubetype == 0):
                        for card in archetypeCards:
                            cards.append(card)
                    archetypesAdded.append((archetypename,-1))
                    print("Added entire archetype " + archetypename + " with " + str(len(archetypeCards)) + " cards.")
                else:
                    if(cubetype == 0):
                        addIndices = random.sample(range(0,len(archetypeCards)),cardnumber)
                        for i in addIndices:
                            cards.append(archetypeCards[i])
                    archetypesAdded.append((archetypename,cardnumber))
                    print("Added " + str(cardnumber) + " cards from " + archetypename + " to the cube.")
            else:
                print("archetype with name archetype with name" + archetypename + " could not be resolved.")
        elif(inputString.startswith("draft")):
            i = inputString.find(" ")
            #packsize equals number of cards par pack. default 15 card pack
            packsize = 15
            if(i != -1):
                packsizestr = inputString[(i+1):]
                try:
                    packsize = int(packsizestr)
                except Exception:
                    print("packsize could not be resolved.")
                    packsize = 15
            cubeInstance = cards.copy()
            if(cubetype == 1):
                cubeInstance = cubeInstance + instantiate(archetypesAdded)
            print("Test:" + str(len(cubeInstance)) + " " + str(len(cards)))
            packs, rest = createPacks(cubeInstance, packsize)
            cubing(packs)
    writeCube(cubetype, cards, archetypesAdded, filename)
    return cubes

