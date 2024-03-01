from botConfig import confidenceLevel
import csv
import random
from spacy_loader import nlp


# TODO where should i even put this code
print("Loading chatbot dataset...")
with open('data/chatbot.csv') as g:
    lines = list(csv.reader(g))
    lineCount = 0
    for i in reversed(range(len(lines))):
        if not (lines[i][0] and lines[i][1]):
            print(f"WARNING: {lines[i]} skipped due to missing data")
            del lines[i]
    data = lines[2:] # list slicing to filter out headings


with open('data/chatbot_randomized_responses.csv') as g:
    lines = list(csv.reader(g))
    lineCount = 0
    for i in reversed(range(len(lines))):
        if not (lines[i][0] and lines[i][1]):
            print(f"WARNING: {lines[i]} skipped due to missing data")
            del lines[i]
    randomized_responses = lines[2:] # list slicing to filter out headings


print("Analyzing chatbot dataset with spaCy...")
data_humansays_only = [line[0] for line in data]
data_doc = list(nlp.pipe(data_humansays_only))

def getResponse(sendMsg: str) -> tuple[str, int|None]:
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

def getRandomResponses(sendMsg: str) -> str:
    exactMatchCount = 0
    exactReply = []
    for line in randomized_responses:
        if line[0] == sendMsg:
            exactMatchCount += 1
            print("Exact match found: " + line[0] + line[1])
            exactReply.append(line[1])

    if exactMatchCount == 0:
        raise ValueError("No exact match found")

    return random.choice(exactReply)
