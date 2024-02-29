from botConfig import confidenceLevel
from difflib import SequenceMatcher
import urllib.parse
import csv
import random
import spacy

# TODO where should i even put this code
print("Loading dataset...")
with open('data/chatbot.csv') as g:
    lines = list(csv.reader(g))
    lineCount = 0
    for i in reversed(range(len(lines))):
        if not (lines[i][0] and lines[i][1]):
            print(f"WARNING: {lines[i]} skipped due to missing data")
            del lines[i]
    data = lines[2:] # list slicing to filter out headings

# if you don't have it, install spacy and run `python -m spacy download en_core_web_md`
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_md")

print("Loading dataset into spaCy...")
data_humansays_only = [line[0] for line in data]
data_doc = list(nlp.pipe(data_humansays_only))

def getResponse(sendMsg: str) -> tuple[str, int|None]:
    #return "You said: " + sendMsg
    sendMsg = urllib.parse.unquote(sendMsg)

    if sendMsg.isdigit():
        movie_id = int(sendMsg)
        return "MOVIEmenu", movie_id

    # TODO check for any direct commands
    # TODO keywords

    successCount = 0
    exactCount = 0
    comeBacks = []
    exactReply = []
    exactMatch = .9
    sendMsg_doc = nlp(sendMsg)

    print("Checking for matches...")
    for i, line_doc in enumerate(data_doc):
        userText = data[i][0]
        botReply = data[i][1]
        checkMatch = sendMsg_doc.similarity(line_doc)
        print(f"Match for {userText}: {checkMatch}")
        if checkMatch >= exactMatch:
            exactCount += 1
            exactReply.append(botReply)
            print("Likely match: " + userText)
            print("Match is: " + str(checkMatch))
        elif checkMatch >= confidenceLevel:
            successCount += 1
            comeBacks.append(botReply)
            print("Possible match: " + userText)
            print("Match is: " + str(checkMatch))
    if exactCount >= 1:
        botResponsePick = random.choice(exactReply)
    elif successCount >= 1:
        botResponsePick = random.choice(comeBacks)
    else:
        botResponsePick = "IDKresponse"
    return botResponsePick, None
