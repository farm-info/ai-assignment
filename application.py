#! /usr/bin/python3
from flask import Flask, render_template, request
import csv
import urllib.parse
from botConfig import myBotName, chatBG, botAvatar, useGoogle, confidenceLevel
from botRespond import getResponse, getRandomResponses

#Bot functions
from dateTime import getTime, getDate
from recommendationEngine import *

application = Flask(__name__)

chatbotName = myBotName
print("Bot Name set to: " + chatbotName)
print("Background is " + chatBG)
print("Avatar is " + botAvatar)
print("Confidence level set to " + str(confidenceLevel))

#Create Log file
try:
    file = open('BotLog.csv', 'r')
except IOError:
    file = open('BotLog.csv', 'w')

def tryGoogle(myQuery):
    myQuery = myQuery.replace("'", "%27")
    showQuery = urllib.parse.unquote(myQuery)
    return "<br><br>You can try this from my friend Google: <a target='_blank' href='https://www.google.com/search?q=" + myQuery + "'>" + showQuery + "</a>"

@application.route("/")
def home():
    return render_template("index.html", botName = chatbotName, chatBG = chatBG, botAvatar = botAvatar)

@application.route("/get")
def get_bot_response():
    userText = request.args.get("msg", "")
    userText = urllib.parse.unquote(userText)
    if userText is None:
        userText = ""
    elif userText == "getWELCOMEMESSAGE":
        botReply = str(getRandomResponses(userText))

    botReply, query = getResponse(userText)

    if botReply == "IDKresponse":
        botReply = str(getRandomResponses(botReply))
        if useGoogle == "yes":
            botReply = botReply + tryGoogle(userText)
    elif botReply == "getGOODBYE":
        botReply = str(getRandomResponses(botReply))

    # intent functions
    elif botReply == "getTIME":
        botReply = getTime()
        print(botReply)
    elif botReply == "getDATE":
        botReply = getDate()
        print(botReply)
    # Recommendation engine functions
    elif botReply == "searchMOVIE":
        botReply = search_movie(str(query))
        print(query)
    elif botReply == "randomMOVIE":
        botReply = random_movie()
        print(botReply)
    elif botReply == "recommendMOVIE":
        botReply = recommend_movie()
        print(botReply)
    elif botReply == "MOVIEmenu":
        # why the fuck is the type checking broken
        botReply = movie_menu(query) # type: ignore
        print(botReply) # type: ignore
    ##Log to CSV file
    print("Logging to CSV file now")
    with open('BotLog.csv', 'a', newline='') as logFile:
        newFileWriter = csv.writer(logFile)
        newFileWriter.writerow([userText, botReply])
        logFile.close()
    return botReply


if __name__ == "__main__":
    # load data before the site starts
    import data_loader
    application.run()
