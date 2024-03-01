from botConfig import confidenceLevel, SEARCH_WORDS, USER_QUERY_STOP_WORDS
import random
from data_loader import nlp, data, data_doc, randomized_responses


def getResponse(sendMsg: str) -> tuple[str, str|int|None]:
    if sendMsg.isdigit():
        movie_id = int(sendMsg)
        return "MOVIEmenu", movie_id

    sendMsg_doc = nlp(sendMsg)

    # directly check for search words
    for token in sendMsg_doc:
        if token.lemma_ in SEARCH_WORDS:
            return "searchMOVIE", sendMsg

    successCount = 0
    exactCount = 0
    comeBacks = []
    exactReply = []
    exactMatch = .9

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

    if botResponsePick == "searchMOVIE":
        # analyze query to extact keywords
        search_query = [token.lemma_ for token in sendMsg_doc if not token.is_stop and not token.is_punct and token.lemma_ not in USER_QUERY_STOP_WORDS]
        search_query = " ".join(search_query).strip()
        return botResponsePick, search_query

    return botResponsePick, None

def getRandomResponses(sendMsg: str) -> str:
    exactMatchCount = 0
    exactReply = []
    for line in randomized_responses:
        if line[0] == sendMsg:
            exactMatchCount += 1
            print(f"Exact match found: {line[0]} {line[1]}")
            exactReply.append(line[1])

    if exactMatchCount == 0:
        raise ValueError("No exact match found")

    return random.choice(exactReply)
