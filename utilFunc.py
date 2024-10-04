import os.path
import requests
import time
import shutil
import platform
if(platform.system() != "Windows"):
    import readline
import random
from matplotlib import pyplot
from matplotlib import axes
from matplotlib import image

#input method which displays prompt + prefill and prefill can be edited on the command line, not compatible with windows
def rlinput(prompt, prefill=''):
   if(platform.system() == "Windows"):
       x = input(prompt)
       print("")
       return x
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
       x = input(prompt)
       print("")
       return x  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()

#finds x and y values such that x*y >= total and x/y ~ xaxis/yaxis
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

#returns the index of matchstring in matchlist. if matchString not in matchList tries to match it with an element. In case of an ultimate fail returns -1
def getIndexFuzzy(matchString, matchList):
    if(matchString in matchList):
        return matchList.index(matchString)
    else:
        for ind in range(0,len(matchList)):
            if(matchList[ind].startswith(matchString)):
                return ind
        for ind in range(0,len(matchList)):
            if(matchList[ind].lower().startswith(matchString.lower())):
                return ind
    return -1

#write archetypes into the ini file[deprecated]
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

#converts a list to a string and includes the index of every element
def listToString(list):
    listString = "["
    for ind in range(0,len(list)):
        listString = listString + str(ind) + ":'" + str(list[ind]) + "', "
    if(listString.endswith(", ")):
        listString = listString[:len(listString)-2]
    listString = listString + "]"
    return listString

#separates the string into a list of strings separated by each instance of separator
def chopItUp(string,separator):
    chopped = []
    ind = string.find(separator)
    while(ind != -1):
        cut = string[:ind]
        chopped.append(cut)
        string = string[ind+len(separator):]
        ind = string.find(separator)
    chopped.append(string)
    return chopped
#sort archetypes current order:artifacts,monocolor,ally,enemy,shards,wedges,rest
def sortArchetypes(archetypesUnsorted):
    archetypes = []
    for a in ["Artifacts", "White", "Blue", "Black", "Red", "Green"]:
        if(a in archetypesUnsorted):
            archetypesUnsorted.remove(a)
            archetypes.append(a)
    colorcombos = {}
    for w in [0,1]:
        for u in [0,1]:
            for b in [0,1]:
                for r in [0,1]:
                    for g in [0,1]:
                        colorcombos[(w,u,b,r,g)] = []
    for a in archetypesUnsorted:
        w,u,b,r,g = 0,0,0,0,0
        i = 0
        while(True):
            if(len(a) <= i):
                break
            elif a[i] == "W":
                w = 1
            elif a[i] == "U":
                u = 1
            elif a[i] == "B":
                b = 1
            elif a[i] == "R":
                r = 1
            elif a[i] == "G":
                g = 1
            else:
                break
            i = i+1
        colorcombos[(w,u,b,r,g)].append(a)
    for singleColor in [(1,0,0,0,0),(0,1,0,0,0),(0,0,1,0,0),(0,0,0,1,0),(0,0,0,0,1)]:
        for a in colorcombos[singleColor]:
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    for allyColor in [(1,1,0,0,0),(0,1,1,0,0),(0,0,1,1,0),(0,0,0,1,1),(1,0,0,0,1)]:
        for a in colorcombos[allyColor]:
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    for enemyColor in [(1,0,1,0,0),(0,1,0,1,0),(0,0,1,0,1),(1,0,0,1,0),(0,1,0,0,1)]:
        for a in colorcombos[enemyColor]:
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    for shard in [(1,1,1,0,0),(0,1,1,1,0),(0,0,1,1,1),(1,0,0,1,1),(1,1,0,0,1)]:
        for a in colorcombos[shard]:
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    for wedge in [(1,0,1,1,0),(0,1,0,1,1),(1,0,1,0,1),(1,1,0,1,0),(0,1,1,0,1)]:
        for a in colorcombos[wedge]:
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    for a in archetypesUnsorted:
        if(a.find("lands") != -1):
            archetypes.append(a)
            archetypesUnsorted.remove(a)
    archetypesUnsorted.sort()
    for a in archetypesUnsorted:
        archetypes.append(a)
    return archetypes

#make the bot AI pick a card from the pack
def Botpick(pack, cardsDrafted):
    return pack.pop(random.randrange(0,len(pack)))

def savedraftedcards(playername, cardsDrafted):
    if(not os.path.exists(f"draftdecks/{playername}")):
        file = open(f"draftdecks/{playername}", "w")
    else:
        i = 1
        while i > 0:
            if(not os.path.exists(f"draftdecks/{playername}" + str(i))):
                file = open(f"draftdecks/{playername}" + str(i), "w")
                i = -2
            i = i+1
    file.write("Cards Drafted:")
    for card in cardsDrafted:
        file.write(card + "\n")
    file.write(";;")
    file.close()

def saveLog(draftLog, players):
    logname = input("Choose name for the draft Log file:")
    if(not os.path.exists(f"draftlogs/{logname}")):
        file = open(f"draftlogs/{logname}", "w")
    else:
        i = 1
        while i > 0:
            if(not os.path.exists(f"draftlogs/{logname}" + str(i))):
                file = open(f"draftlogs/{logname}" + str(i), "w")
                i = -2
            i = i+1
    file.write("Draft Log Version 3:\n")
    file.write("Players:\n")
    for (playertype,playername,cardsDrafted) in players:
        file.write(playername + ": " + playertype + "\n")
    file.write(";\nDraft Picks:\n")
    for roundnumber in range(0,len(draftLog)):
        file.write(f"Round {roundnumber}:\n")
        for packnumber in range(0,len(draftLog[roundnumber])):
            file.write(f"Pack {packnumber}:\n")
            for card,playername in draftLog[roundnumber][packnumber]:
                file.write(card + "; " + playername + "\n")
            file.write(";\n")
        file.write(";;\n")
    file.write(";;;")
    file.close()

def saveDeck(playername,deck,sideboard):
    if(not os.path.exists(f"draftdecks/{playername}.dec")):
        file = open(f"draftdecks/{playername}.dec", "w")
    else:
        i = 1
        while i > 0:
            if(not os.path.exists(f"draftdecks/{playername}" + str(i) + ".dec")):
                file = open(f"draftdecks/{playername}" + str(i) + ".dec", "w")
                i = -2
            i = i+1
    file.write(f"//{playername}\n")
    for card in set(deck):
        count = deck.count(card)
        file.write(f"{count} {card}\n")
    for card in set(sideboard):
        count = sideboard.count(card)
        file.write(f"SB: {count} {card}\n")
    file.close()

def buildDeck(playername, sideboard):
    deck = []
    print(f"\nYou are now in deck building mode {playername}.")
    print(f"You have drafted the following cards: {listToString(sideboard)}\nThey all start in the sideboard.")
    options = ("Options:\n" +
          "display1 | displays the deck and sideboard\n" + 
          "display2 | displays the deck\n" + 
          "display3 | displays your sideboard\n" +
          "list1 | lists the deck and sideboard\n" +
          "list2 | lists your deck\n" +
          "list3 | lists your sideboard\n" +
          "add _cardID_ | adds card _cardID_ to your deck from your sideboard\n" +
          "remove _cardID_ | moves card _cardID_ from your deck to your sideboard\n" +
          "addBasics _basicID_ _number_ | adds _number_ copies of the basic land _basicID_ to your deck\n" +
          "options | displays this menu\n" +
          "discard deck | ands deck building move WITHOUT saving the deck\n" +
          "done | ends deck building mode")
    print(options)
    prefill = ""
    while(True):
        inputString = rlinput("Command:", prefill)
        commands = chopItUp(inputString," ")
        prefill=""
        if(inputString.startswith("display1") or inputString.startswith("d1")):
            if(len(commands) > 1):
                numStr = commands[1]
                try:
                    num = int(numStr)
                except:
                    print("bad input!")
                    num = 1000
            else:
                num = 1000
            num = 1000
            displayList(deck + ["decksideboarddivider"] + sideboard,num)
        elif(inputString.startswith("list1") or inputString.startswith("l1")):
            print("Deck:" + listToString(deck))
            print("Sideboard:" + listToString(sideboard))
        elif(inputString.startswith("display2") or inputString.startswith("d2")):
            if(len(commands) > 1):
                numStr = commands[1]
                try:
                    num = int(numStr)
                except:
                    print("bad input!")
                    num = 1000
            else:
                num = 1000
            num = 1000
            displayList(deck,num)
        elif(inputString.startswith("list2") or inputString.startswith("l2")):
            print(listToString(deck))
        elif(inputString.startswith("display3") or inputString.startswith("d3")):
            if(len(commands) > 1):
                numStr = commands[1]
                try:
                    num = int(numStr)
                except:
                    print("bad input!")
                    num = 1000
            else:
                num = 1000
            num = 1000
            displayList(sideboard,num)
        elif(inputString.startswith("list3") or inputString.startswith("l3")):
            print(listToString(sideboard))
        elif(inputString.startswith("add ") or inputString.startswith("a ")):
            cardname = inputString[(inputString.find(" ")+1):]
            try:
                ind = int(cardname)
                if(ind < len(sideboard)):
                    info = sideboard[ind]
                    print("The chosen card is " + info +".")
                    deck.append(info)
                    sideboard.remove(info)
            except:
                ind = getIndexFuzzy(cardname,sideboard)
                if(ind != -1):
                    info = sideboard[ind]
                    print(info +" added to the deck.")
                    deck.append(info)
                    sideboard.remove(info)
                else:
                    print("No card starting with \"" + cardname + "\" is in the sideboard")
                    prefill = inputString
        elif(inputString.startswith("remove ") or inputString.startswith("rm ")):
            cardname = inputString[(inputString.find(" ")+1):]
            try:
                ind = int(cardname)
                if(ind < len(deck)):
                    info = deck[ind]
                    print(info +" moved to the sideboard.")
                    sideboard.append(info)
                    deck.remove(info)
            except:
                ind = getIndexFuzzy(cardname,deck)
                if(ind != -1):
                    info = deck[ind]
                    print(info +" moved to the sideboard.")
                    sideboard.append(info)
                    deck.remove(info)
                else:
                    print("No card starting with \"" + cardname + "\" is in the deck")
                    prefill = inputString
        elif(inputString.startswith("done") or inputString.startswith("q")):
            saveDeck(playername,deck,sideboard)
            break
        elif(inputString.startswith("discard deck")):
            break
        elif(inputString.startswith("o") or inputString.startswith("O")):
            print(options)
        elif(inputString.lower().startswith("addbasics ") or inputString.lower().startswith("ab ")):
            type = commands[1]
            if(len(commands) > 2):
                try:
                    number = int(commands[2])
                except ValueError:
                    print("bad input!")
                    number = 1
            else:
                number = 1
            Basics = ["Plains","Island","Swamp","Mountain","Forest"]
            ind = getIndexFuzzy(type, Basics)
            if(ind != -1):
                for i in range(number):
                    deck.append(Basics[ind])
            else:
                print(f"Basic land {commands[1]} was not recognized.")
        else:
            print("Command was not recognized")
            prefill=inputString

def makePick(player, pack):
    (playertype, playername, cardsDrafted) = player
    if(playertype == "bot"):
        pick = Botpick(pack,cardsDrafted)
        cardsDrafted.append(pick)
        return pick
    elif(playertype == "local"): 
        print(f"\nIt is now your turn to pick {playername}.")
        print("The pack consists of the following cards: " + listToString(pack))
        print("Options:\n" +
              "display1 | displays the pack\n" + 
              "display2 | displays your drafted cards\n" +
              "list1 | lists the pack\n" +
              "list2 | lists your drafted cards\n" +
              "pick _cardID_ | adds _cardID_ to your drafted cards and passes the pack. _cardID_ can be name or index.")
        prefill = ""
        while(True):
            inputString = rlinput("Command: ", prefill)
            commands = chopItUp(inputString," ")
            prefill=""
            status=0
            if(inputString.startswith("display1") or inputString.startswith("d1")):
                if(len(commands) > 1):
                    numStr = commands[1]
                    try:
                        num = int(numStr)
                    except:
                        print("bad input!")
                        num = 1000
                else:
                    num = 1000
                num = 1000
                displayList(pack,num)
            elif(inputString.startswith("list1") or inputString.startswith("l1")):
                print(listToString(pack))
            elif(inputString.startswith("display2") or inputString.startswith("d2")):
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
                displayList(cardsDrafted,num)
            elif(inputString.startswith("list2") or inputString.startswith("l2")):
                print(str(cardsDrafted))
            elif(inputString.startswith("pick ") or inputString.startswith("p ")):
                cardname = inputString[(inputString.find(" ")+1):]
                try:
                    ind = int(cardname)
                    if(ind < len(pack)):
                        info = pack[ind]
                        print("The chosen card is " + info +".")
                        cardsDrafted.append(info)
                        pack.remove(info)
                        return info
                except:
                    ind = getIndexFuzzy(cardname,pack)
                    if(ind != -1):
                        info = pack[ind]
                        print("You picked " + info +".")
                        cardsDrafted.append(info)
                        pack.remove(info)
                        return info
                    else:
                        print("No card starting with \"" + cardname + "\" is in this pack")
                        prefill = inputString
            else:
                print("Command was not recognized")
                prefill=inputString

def draft(packs,players,draftroundnum):
    if(draftroundnum * len(players) > len(packs)):
        print("Drafting with " + str(len(players)) + " players for " + str(draftroundnum) + " rounds requires " + str(draftroundnum * len(players)) + " packs but there are only " + str(len(packs)) + " packs.")
        return
    draftlog = []
    for roundcount in range(0,draftroundnum):
        roundparity = roundcount % 2
        #saves the number of cards drafted for each player
        playernextpack = []
        roundpacks = []
        packnextplayer = []
        draftorderbypack = []
        for i in range(len(players)):
            draftorderbypack.append([])
            playernextpack.append(i)
            packnextplayer.append(i)
            roundpacks.append(packs.pop(random.randrange(0,len(packs))))
        packsDone = 0
        while(packsDone < len(roundpacks)):
            for playerind in range(len(players)):
                if(packnextplayer[playernextpack[playerind]] == playerind):
                    playertype, playername, cardsDrafted = players[playerind]
                    draftorderbypack[playernextpack[playerind]].append((makePick(players[playerind],roundpacks[playernextpack[playerind]]),playername))
                    if(len(roundpacks[playernextpack[playerind]]) == 0):
                        packnextplayer[playernextpack[playerind]] = -1
                        packsDone = packsDone + 1
                    else:
                        packnextplayer[playernextpack[playerind]] = (packnextplayer[playernextpack[playerind]] - 1 + 2 * roundparity) % len(players)
                    playernextpack[playerind] = (playernextpack[playerind] +1- 2 * roundparity) % len(roundpacks)
            time.sleep(0.1)
        draftlog.append(draftorderbypack)
    saveLog(draftlog, players)
    for (playertype2,playername2,cardsDrafted2) in players:
        if(playertype2 == "local"):
            buildDeck(playername2, cardsDrafted2)
        
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
    
def readAttributes():
    cardAttributes = {}
    file = open("cardAttributes.txt","r")
    lines = file.readlines()
    for line in lines:
        ind = line.find("*")
        if(ind == -1):
            continue
        cardname = line[:ind]
        cardAttributes[cardname]= {}
        while(True):
            skind = line.find("'", ind) +1
            if(skind == 0):
                break
            ekind = line.find("'", skind)
            if(ekind == -1):
                break
            key = line[skind:ekind]
            svind = line.find("'", ekind +1) +1
            if(svind == 0):
                break
            evind = line.find("'", svind)
            if(evind == -1):
                break
            value = line[svind:evind]
            if(key == "cmc"):
                try: 
                    cardAttributes[cardname][key] = int(value)
                except ValueError:
                    print(f"could not convert {value} to int")
            elif(key in ["colors", "color_identity", "produced_mana"]):
                cardAttributes[cardname][key] = []
                for color in ["W","U","B","R","G","C"]:
                    if value.find(color) != -1:
                        cardAttributes[cardname][key].append(color)
            elif(key in ["type_line"]):
                cardAttributes[cardname][key] = []
                for cardtype in ["Creature","Sorcery","Instant","Land","Artifact","Enchantment","Planeswalker"]:
                    if value.find(cardtype) != -1:
                        cardAttributes[cardname][key].append(cardtype)
            elif(key in ["mana_cost"]):
                cardAttributes[cardname][key] = {"W": 0 ,"U": 0 ,"B": 0 ,"R": 0 ,"G": 0 ,"C": 0}
                for color in ["W","U","B","R","G","C"]:
                    cardAttributes[cardname][key][color] = .5 * value.count('{' + color) + .5 * value.count(color + '}')
            ind = evind + 1
    print(cardAttributes)
    return cardAttributes



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

#checks whether x is card or error and searches up card attributes, then returns them in a dict
def deeplyAnalyseObject(x):
    object = findAttribute(x.text,'object')
    if(object == "error"):
        type = findAttribute(x.text,'type')
        print(x.text)
        return object,type
    if(object == "card"):
        attributes = {}
        value = findAttribute(x.text,"colors",None,'[',']')
        if(value != "error"):
            attributes["colors"] = value
        value = findAttribute(x.text,"color_identity",None,'[',']')
        if(value != "error"):
            attributes["color_identity"] = value
        value = findAttribute(x.text,"produced_mana",None,'[',']')
        if(value != "error"):
            attributes["produced_mana"] = value
        value = findAttribute(x.text,"mana_cost")
        if(value != "error"):
            attributes["mana_cost"] = value
        value = findAttribute(x.text,"type_line")
        if(value != "error"):
            attributes["type_line"] = value
        value = findAttribute(x.text,"cmc",None,':',',')
        if(value != "error"):
            attributes["cmc"] = value
        return object,attributes


#checks for value of att within str, searches for subatt after att if subatt is given
def findAttribute(str, att, subatt=None, frontsymbol = '"', backsymbol = '"'):
    tind = str.find(att)
    if(tind == -1):
        return "error"
    tind = str.find(frontsymbol,tind+1+len(att))
    if(tind == -1):
        return "error"
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
        while(str[i] != backsymbol):
            content += str[i]
            i = i+1
        return content

#searches up the card 'name' on scryfall and, if found, saves the image to images/'name'.jpg
def downloadImage(name):
    time.sleep(0.1)
    try:
        x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + name, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
    except:
        print(f"Threw error while connecting to scryfall. The picture for \"{name}\" could not be downloaded.")
        return -1
    url = findAttribute(x.text,"image_uris", "small")
    print(url)
    try:
        x = requests.get(url, stream = True, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
    except:
        print(f"Could not connect to scryfall. The picture for \"{name}\" could not be downloaded.")
        return -1
    file = open("images/" + name + ".jpg", "wb")
    shutil.copyfileobj(x.raw,file)
    file.close()
    return 0


def displayList(namestodisplay, size=30):
    pics = []
    toDisplay = namestodisplay.copy()
    for i in range(len(toDisplay)):
        tind = toDisplay[i].find("//")
        if(tind != -1):
            if (os.path.exists("images/" + toDisplay[i][:(tind-1)] + ".jpg") == False):
                print(toDisplay[i])
                error = downloadImage(toDisplay[i][:(tind-1)])
                if (error == -1):
                    toDisplay[i] = "offline"
        else:
            if (os.path.exists("images/" + toDisplay[i] + ".jpg") == False):
                print(toDisplay[i])
                error = downloadImage(toDisplay[i])
                if (error == -1):
                    toDisplay[i] = "offline"
    for j in range(((len(toDisplay)-1)//size)+1):
        size1 = min(size,len(toDisplay)-j*size)
        myImage = [None] * size1
        #determine size
        x,y = fragmentFormat(5,2,size1)
        if(x*y < size1):
            print("massive error!")
        fig, axs = pyplot.subplots(((size1-1)//x + 1),x)
        fig.tight_layout(pad=0)
        for i in range(size1):
            tind = toDisplay[i+j*size1].find("//")
            if(tind != -1):
                myImage[i] = image.imread("images/" + toDisplay[i+j*size1][:(tind-1)] + ".jpg")
            else:
                myImage[i] = image.imread("images/" + toDisplay[i+j*size1] + ".jpg")
            if(y == 1):
                if(x == 1):
                    axs.set_axis_off()
                    axs.get_xaxis().set_visible(False)
                    axs.get_yaxis().set_visible(False)
                    axs.imshow(myImage[i])
                else:
                    axs[i].set_axis_off()
                    axs[i].get_xaxis().set_visible(False)
                    axs[i].get_yaxis().set_visible(False)
                    axs[i].imshow(myImage[i])
            else:
                axs[i//x][i % x].set_axis_off()
                axs[i//x][i % x].get_xaxis().set_visible(False)
                axs[i//x][i % x].get_yaxis().set_visible(False)
                axs[i//x][i % x].imshow(myImage[i])
        for i in range(size1,x*y):
            if(y == 1):
                axs[i].set_axis_off()
                axs[i].get_xaxis().set_visible(False)
                axs[i].get_yaxis().set_visible(False)
            else:
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
