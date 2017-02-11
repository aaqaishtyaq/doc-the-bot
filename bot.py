from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler,InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,InlineQueryResultArticle,InputTextMessageContent,ParseMode
import telegram,logging,time,re
from PyDictionary import PyDictionary
import nltk
import json


updater=Updater(token='Telegram-Bot-API-Key')
dispatcher=updater.dispatcher

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

#Sample data set soon to be exported as seperate entity which can be expanded
with open('data.json', 'r') as fp:
    sample_data_set = json.load(fp)

print("I'm On")

pd=PyDictionary()

#dendrite to reach neighbour neurons
def dendrite(context):
    global sample_data_set
    print(context)
    context_domain={'diseases':[],
    'symptoms':[],
    'commonsym':[],}
    for z in range(len(context)):
        for q in range(len(context)):
            sub_context=' '.join(context[z:q+1])
            #print(sub_context)
            for x,y in sample_data_set.items():
                for k in y:
                    if sub_context in k.split() and x=='commonsym':
                        if ('days' or 'week' or 'weeks' or 'month') not in context:
                            context_domain['commonsym'].append(sub_context)

                    if sub_context in k.split() and x=='symptoms':
                        context_domain['diseases'].append(sample_data_set['disease'][sample_data_set['symptoms'].index(k)])
                    elif sub_context in k.split() and x=='disease':
                        context_domain['diseases'].append(sample_data_set['disease'][sample_data_set['disease'].index(k)])
    print(context_domain)
                        
        
#Context Synthesization Engine
def CSE(sentence):
    global pd
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    print(tagged)
    core_context=[]
    for x in tagged:
        if x[0].lower()=='not':
            core_context.append(x[0].lower())
        elif x[1] in ['VB','VBD','VBG','VBN','VBP','VBZ','RB','RBR','RBS','JJ','JJR','JJS','CD','NN','NNP','NNS','NNPS']:
            core_context.append(x[0].lower())
    if len(core_context)==0:
        return 0
    dendrite(core_context)

#Initiating Conversation
def start(bot, update):
    m=update.message.to_dict()
    bot.sendMessage(chat_id=update.message.chat_id, text="""
Hello """+m['from']['first_name']+"""
""")

#Handling next conversations
def reply_handler(bot, update):
    m=update.message.to_dict()
    global CSE
    if CSE(m['text'])==0:
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry I couldn't understand you, would you please elaborate ?")

dispatcher.add_handler(CommandHandler('start',start))
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

updater.start_polling()