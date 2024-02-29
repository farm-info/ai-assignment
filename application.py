#! /usr/bin/python3
from flask import Flask, render_template, request
import random
import csv
import os
import urllib.parse
from botConfig import myBotName, chatBG, botAvatar, useGoogle, confidenceLevel
from botRespond import getResponse

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
    userText = request.args.get('msg')
    if userText is None:
        userText = ""
    botReply, movie_id = getResponse(userText)

    if botReply == "IDKresponse":
        # send the "i don't know" code back to the bot
        # TODO stop doing this, which would require a new function and a new csv file
        botReply = str(getResponse('IDKnull')[0])
        if useGoogle == "yes":
            botReply = botReply + tryGoogle(userText)
    elif botReply == "getTIME":
        botReply = getTime()
        print(getTime())
    elif botReply == "getDATE":
        botReply = getDate()
        print(getDate())
    # Recommendation engine functions
    elif botReply == "searchMOVIE":
        botReply = search_movie()
        print(search_movie())
    elif botReply == "randomMOVIE":
        botReply = random_movie()
        print(random_movie())
    elif botReply == "recommendMOVIE":
        botReply = recommend_movie()
        print(recommend_movie())
    elif botReply == "MOVIEmenu":
        # why the fuck is the type checking broken
        botReply = movie_menu(movie_id) # type: ignore
        print(movie_menu(movie_id)) # type: ignore
    ##Log to CSV file
    print("Logging to CSV file now")
    with open('BotLog.csv', 'a', newline='') as logFile:
        newFileWriter = csv.writer(logFile)
        newFileWriter.writerow([userText, botReply])
        logFile.close()
    return botReply


if __name__ == "__main__":
    application.run()
