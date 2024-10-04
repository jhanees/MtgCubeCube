import random 
import requests
import time
import sys
import os.path
from utilFunc import analyseObject, readArchetype, displayList, dropLastLetter, draft, listToString, getIndexFuzzy, rlinput, chopItUp

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

def cubing(filename):
    if(not os.path.exists("cubes/" + filename)):
        print("Error!")
    else:
        cubetype, cards, archetypesAdded = readCube(filename)
        packsizeStr = input("Choose packsize:")
        try:
            packsize = int(packsizeStr)
            if(packsize < 1):
                print("Packsize has to be at least 1. Packsize set to 15 by default.")
                packsize = 15
        except:
            packsize = 15
            print("Couldn't parse input. Packsize set to 15 by default.")
        cubeInstance = cards.copy()
        if(cubetype == 1):
            cubeInstance = cubeInstance + instantiate(archetypesAdded)
        packs, rest = createPacks(cubeInstance, packsize)
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
    try:
        ind = int(filename)
    except:
        ind = getIndexFuzzy(filename, cubes)
    if(ind != -1 and os.path.exists("cubes/" + cubes[ind])):
        filename = cubes[ind]
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
               "addarchetype _archetypeID_ [_cardnumber_] | adds _cardnumber_ cards from archetype _archetypeID_ to the cube. _cardnumber_ is all by default. _archetypeID_ can be name or index."
               "removecard _cardID_ | removes the card _cardID_ from the cube. Can refer to the card by index or name.",
               "removearchetype _archetypeID_ | removes archetype _archetypeID_ from the cube. _archetypeID_ can be name or index.",
               "draft | start drafting this cube.\n",
               "options | displays this menu",
               "back | goes back to the main menu"]
    for o in Options:
        print(o)
    prefill = ""
    while(True):
        inputString = rlinput("Cube " + filename + ": ", prefill)
        prefill = ""
        commands = chopItUp(inputString, " ")
        if (inputString.startswith("end") or inputString.startswith("done") or inputString.startswith("back") or inputString.startswith("q") or inputString.startswith("quit")):
            break
        if(inputString.startswith("archetypes")):
            print("All archetypes: " + listToString(archetypes))
            print("Archetypes added so far: " + listToString(archetypesAdded))
        elif(inputString.lower().startswith("o")):
            for o in Options:
                print(o)
        elif(inputString.startswith("display") or inputString.startswith("dp")):
            if(len(commands) > 1):
                numStr = commands[1]
                try:
                    num = int(numStr)
                except:
                    print("bad input!")
                    num = 1000
            else:
                num = 1000
            if(cubetype == 0):
                displayList(cards,num)
            if(cubetype == 1):
                displaycards= cards + instantiate(archetypesAdded)  
                displayList(displaycards,num)
        elif(inputString.startswith("list") or inputString.startswith("l")):
            print(cards)
        elif(inputString.startswith("removecard ") or inputString.startswith("rc ")):
            cardname = inputString[(inputString.find(" ")+1):]
            #searches for card
            object = ""
            info = ""
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
                    print("No card starting with " + cardname + " was found in this cube and thus no card was removed.")
        elif(inputString.startswith("removearchetype ") or inputString.startswith("ra ")):
            archetypename = commands[1]
            #searches for card
            object = ""
            info = ""
            try:
                ind = int(archetypename)
                if(ind < len(archetypesAdded)):
                    name, number = archetypesAdded[ind]
                    if number == -1:
                        print("Deleted entire archetype " + name + " from the cube.")
                    else:
                        print("Deleted " + str(number) + " cards from archetype " + name + " from the cube.")
                    archetypesAdded.pop(ind)
            except ValueError:
                archetypesAddedNames = []
                for i in range(0, len(archetypesAdded)):
                    (archetypename2,a) = archetypesAdded[i]
                    archetypesAddedNames.append(archetypename2)
                ind = getIndexFuzzy(archetypename,archetypesAddedNames)
                if(ind != -1):
                    (name,number) = archetypesAdded[ind]
                    if number == -1:
                        print("Deleted entire archetype " + name + " from the cube.")
                    else:
                        print("Deleted " + str(number) + " cards from archetype " + name + " from the cube.")
                    archetypesAdded.remove((name,number))
                else:
                    print("Archetype starting with " + archetypename + " not found and thus could not be removed.")
        elif(inputString.startswith("addcard ") or inputString.startswith("ac ")):
            cardname = inputString[(inputString.find(" ")+1):]
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
        elif(inputString.startswith("addarchetype ") or inputString.startswith("aa ")):
            archetypename = commands[1]
            if(len(commands) > 2):
                cardnumberStr = commands[2]
                try:
                    cardnumber = int(cardnumberStr)
                except:
                    print("bad input!")
                    cardnumber = 1000
            else:
                cardnumber = 1000
            try:
                ind = int(archetypename)
                if(ind < len(archetypes)):
                    name = archetypes[ind]
                    if((name,) in archetypesAdded):
                        print("archetype is already in the cube. Another copy will be added anyway.")
                    archetypeCards = readArchetype(name)
                    if(archetypeCards != []):
                        if(cardnumber >= len(archetypeCards)):
                            if(cubetype == 0):
                                for card in archetypeCards:
                                    cards.append(card)
                            archetypesAdded.append((name,-1))
                            print("Added entire archetype " + name + " with " + str(len(archetypeCards)) + " cards.")
                        else:
                            if(cubetype == 0):
                                addIndices = random.sample(range(0,len(archetypeCards)),cardnumber)
                                for i in addIndices:
                                    cards.append(archetypeCards[i])
                            archetypesAdded.append((name,cardnumber))
                            print("Added " + str(cardnumber) + " cards from " + name + " to the cube.")
                    else:
                        print("archetype with name " + archetypename + " could not be resolved.")
            except ValueError:
                ind = getIndexFuzzy(archetypename,archetypes)
                if(ind != -1):
                    name = archetypes[ind]
                    if((name,) in archetypesAdded):
                        print("archetype is already in the cube. Another copy will be added anyway.")
                    archetypeCards = readArchetype(name)
                    if(archetypeCards != []):
                        if(cardnumber >= len(archetypeCards)):
                            if(cubetype == 0):
                                for card in archetypeCards:
                                    cards.append(card)
                            archetypesAdded.append((name,-1))
                            print("Added entire archetype " + name + " with " + str(len(archetypeCards)) + " cards.")
                        else:
                            if(cubetype == 0):
                                addIndices = random.sample(range(0,len(archetypeCards)),cardnumber)
                                for i in addIndices:
                                    cards.append(archetypeCards[i])
                            archetypesAdded.append((name,cardnumber))
                            print("Added " + str(cardnumber) + " cards from " + name + " to the cube.")
                    else:
                        print("archetype with name " + name + " could not be resolved.")
        elif(inputString.startswith("draft")):
            writeCube(cubetype, cards, archetypesAdded, filename)
            cubing(filename)
        else:
            prefill = inputString
            print("Command not recognized")
    writeCube(cubetype, cards, archetypesAdded, filename)
    return cubes

