#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from urllib.parse import quote_plus
import requests, logging
from bs4 import BeautifulSoup
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
from telegram.ext import Updater, CommandHandler,MessageHandler,Filters



token = "948524958:AAHjNH_bag_dKMaxs9ibjXxkbbPCePCxxGY"



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
def help(bot, update):
    msg = "Usage: /book <keyword> and I will give you links to EPUB/PDF/MOBI/AZW3 :)\n Enter /cancel to cancel search"
    update.message.reply_text(msg)

def cancel(bot, update,user_data):
	user = update.message.from_user
	#logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Cancellation Successful :) ',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


mlist=[]
def book(bot, update, user_data):
    mdict={}
    line = update["message"]["text"].split()
    
    if len(line) < 2:
        update.message.reply_text('Hey! I need a keyword >:(')
        return
  
    url = "https://libgen.is"
    bookname = quote_plus(' '.join(line[1:]))
    query = url+"/search?req="+bookname.replace(' ','+')
    print(query)
    r = requests.get(query)
    html = r.text
    soup = BeautifulSoup(html)

    items = soup.find("table", {"class": "c"})
    msg = ""
    #print(items)

    # for row in items.findAll("tr")[1:]:
    #     for col in row.findAll("td")[:9]:
    #         print(col.text)

    results = {}
    for row in items.findAll('tr'):
        results={}
        aux = row.findAll('td')
        results['id'] = str(aux[0].text)
        results["author"]=str(aux[1].text)
        results["title"]=str(aux[2].a.text)
        results["publisher"]=str(aux[3].text)
        results["year"] = str(aux[4].string)
        results['language']=str(aux[5].string)
        results['size']=str(aux[7].string)
        results['extension']=str(aux[8].string)
        if len(aux)>12:
            results['mirrors']={
                '1':str(aux[9].a['href']),
                '2':str(aux[10].a['href']),
                '3':str(aux[11].a['href']),
                '4':str(aux[12].a['href']),
                '5':str(aux[13].a['href'])
            }
        else:
            results['mirrors']={}
        mlist.append(results)

    #print(mlist)
    user_data['mlist']=mlist[1:]
    for i in range(len(mlist)-1):
        update.message.reply_text("id:"+mlist[i+1]["id"]+"\nauthor:"+mlist[i+1]["author"]+"\ntitle:"+mlist[i+1]["title"]+"\npublisher:"+mlist[i+1]["publisher"]+"\nyear:"+mlist[i+1]["year"]+"\nlanguage:"+mlist[i+1]["language"]+"\nsize:"+mlist[i+1]["size"]+"\nextension:"+mlist[i+1]["extension"])#+str(mlist[i+1]["mirrors"]))
    update.message.reply_text("Enter id:")
    return 1


GET_TEXT=1
def get_text(bot, update,user_data):
    user = update.message.from_user
    user_text=update.message.text
    mlist = user_data['mlist']

    #update.message.reply_text("hello  "+user_text)

    foundid=False
    index = -999
    for i in range(len(mlist)):
        if mlist[i]["id"]==user_text:
            foundid =True
            index = i
            break
    if not foundid:
        update.message.reply_text("Invalid ID")
        return ConversationHandler.END
    else:
        print("valid")
        mirrors = mlist[int(index)]["mirrors"]
        for i in range(len(mirrors)):
            try:
                print(mirrors[str(i)])
                r = requests.get(mirrors[str(i)])
                html = r.text
                soup = BeautifulSoup(html)
                print("============================================================================")
                link = soup.findAll('a')[0]
                url = 'http://'+mirrors[str(i)].split('/')[2]+link.get('href')
                #print(url)
                update.message.reply_text(url)
                break
                print("============================================================================")
                #print(html)
            except Exception as e:
                print(e)
    return GET_TEXT  

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('book', book,pass_user_data=True)],
		states={
			GET_TEXT: [MessageHandler(Filters.text, get_text,pass_user_data=True),CommandHandler('cancel', cancel,pass_user_data=True)]},
		fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True)]
	)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    #dp.add_handler(CommandHandler("book", book))
    dp.add_handler(conv_handler)


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


    
if __name__ == '__main__':
    main()
