#!/usr/bin/env python3

import telepot
from telepot.loop import MessageLoop
import Strava
import Storage
import StravaDb
import time
import re
from pprint import pprint
import traceback
import json

print('Initializing data')
storage = Storage.Storage()
strava = Strava.Strava(storage)
stravaDb = StravaDb.StravaDb(storage, strava)
secret = "<secret>"
bot = telepot.Bot(secret)
last_rank_cmd = 0

def findTag(reg, command_all):
    exists = False
    match = re.search(reg, command_all)
    try:
        if match.group(1) != None:
            exists = True
    except:
        exists = False

    return exists

def handle(msg):
    logFile = open("grc.txt", "a")
    try:
        logFile.write(json.dumps(msg, sort_keys=True, indent=4))
        pprint(msg)

        if (msg is None) or ('chat' not in msg.keys()) or ('id' not in msg['chat'].keys()) or ('text' not in msg.keys()):
            return

        command_all = msg['text']
        command_line = list(filter(lambda x: len(x) > 0, command_all.split(' ')))
        if len(command_line) < 1:
            return

        command = command_line[0]
        chat_id = msg['chat']['id']
        ret = None
        cmdMsg = 'Processing ' + command_all + ' for ' + str(chat_id)
        print(cmdMsg)
        logFile.write(cmdMsg + "\n")

        if command.startswith('/rank'):
            global last_rank_cmd
            one_per = 10
            if time.time() - last_rank_cmd < one_per :
                ret = u'Вас багато, а я один! Не більше однієї команди на {} секунд'.format(one_per)
            else:
                last_rank_cmd = time.time()

                prev = findTag(r'\/rank.*(попередн|previous)', command_all)
                year = findTag(r'\/rank.*(рік|year)', command_all)
                month = False#findTag(r'\/rank.*(місяць|month)', command_all)
                everything = findTag(r'\/rank.*(все|everything|all)', command_all)

                count = 0
                match = re.search(r'(\d+)', command_all)
                try:
                    count = int(match.group(1))
                except:
                    count = 0
                if count < 1 or count > 50:
                    count = 50

                board = ''
                if year == True or everything == True or month == True:
                    board = stravaDb.getBoard(everything, year, month, prev, count)
                else:
                    board = strava.getLeaderboard(prev, count)
                if len(board) == 0:
                    board = [u'тут поки ніхто не бігав']
                ret = '<pre>' + '\n'.join(board) + '</pre>'
        else:
            ret = None# u'Не зовсім зрозумів запитання, я поки вчуся та знаю лише /rank команду'

        if ret is not None:
            print('Sending back')
            logFile.write(ret + "\n")
            bot.sendMessage(chat_id, ret, parse_mode='HTML')
        else:
            print('Do not send anything back')
            logFile.write('Do not send anything back' + "\n")
    except Exception as e:
        print('Error processing request')
        print(e)
        logFile.write('Error processing request' + "\n")
        traceback.print_exc()
    logFile.write("\n\n")
    logFile.close()

bot.message_loop(handle)
while 1:
   time.sleep(5000)
