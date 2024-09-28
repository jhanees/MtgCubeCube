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

def rlinput(prompt, prefill=''):
   if(platform.system() == "Windows"):
       return input(prompt)
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

def saveLog(draftLog):
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
    file.write("Draft Log:\n")
    for roundnumber in range(0,len(draftLog)):
        file.write(f"Round {roundnumber}:\n")
        for packnumber in range(0,len(draftLog[roundnumber])):
            file.write(f"Pack {packnumber}:\n")
            for card in draftLog[roundnumber][packnumber]:
                file.write(card + "\n")
            file.write(";\n")
        file.write(";;\n")
    file.write(";;;")
    file.close()

def makePick(player, pack):
    (playertype, playername, cardsDrafted) = player
    if(playertype == "bot"):
        pick = Botpick(pack,cardsDrafted)
        cardsDrafted.append(pick)
        return pick
    elif(playertype == "local"): 
        print("\nIt is now your turn to pick.")
        print("The pack consists of the following cards: " + str(pack))
        print("Options:\n" +
              "display1 | displays the pack\n" + 
              "display2 | displays your drafted cards\n" +
              "list1 | lists the pack\n" +
              "list2 | lists your drafted cards\n" +
              "pick _cardname_ | adds _cardname to your drafted cards and passes the pack.")
        prefill = ""
        while(True):
            inputString = rlinput("Command: ", prefill)
            prefill=""
            status=0
            if(inputString.startswith("display1") or inputString.startswith("d1")):
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
                displayList(pack,num)
            elif(inputString.startswith("list1") or inputString.startswith("l1")):
                print(str(pack))
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
                i = inputString.find(" ")
                cardname = inputString[(i+1):]
                try:
                    x = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + cardname, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                except:
                    print("Could not connect to Scryfall. Maybe check your internet connection.")
                    status = -1
                if(status != -1):
                    object,info = analyseObject(x)
                    if(object == "card"):
                        print("Card name is " + info)
                        if(info in pack):
                            cardsDrafted.append(info)
                            pack.remove(info)
                            return info
                        else:
                            print("The card \"" + info + "\" is not in this pack")
                            prefill = inputString
                    else:
                        print("Error type is " + info)
                        #if not found tries again with exact command if ambiguous
                        if(info == "ambiguous"):
                            time.sleep(0.1)
                            try: 
                                x = requests.get('https://api.scryfall.com/cards/named?exact=' + inputString, headers = {"User-Agent" : "MtgCubeCube", "Accept" : "*/*"})
                                object,info = analyseObject(x)
                            except:
                                print("Could not connect to Scryfall. Maybe check your internet connection.")
                                status = -1
                        if(object == "card"):
                            print("Card name is " + info)
                            if(info in pack):
                                cardsDrafted.append(info)
                                pack.remove(info)
                                return info
                            else:
                                print("The card \"" + info + "\" is not in this pack")
                                prefill = inputString
                        else:
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
                    draftorderbypack[playernextpack[playerind]].append(makePick(players[playerind],roundpacks[playernextpack[playerind]]))
                    if(len(roundpacks[playernextpack[playerind]]) == 0):
                        packnextplayer[playernextpack[playerind]] = -1
                        packsDone = packsDone + 1
                    else:
                        packnextplayer[playernextpack[playerind]] = (packnextplayer[playernextpack[playerind]] - 1 + 2 * roundparity) % len(players)
                    playernextpack[playerind] = (playernextpack[playerind] +1- 2 * roundparity) % len(roundpacks)
            time.sleep(0.1)
        draftlog.append(draftorderbypack)
    for (playertype,a,cardsDrafted) in players:
        if(playertype == "local"):
            savedraftedcards(a,cardsDrafted)
    saveLog(draftlog)

        
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
