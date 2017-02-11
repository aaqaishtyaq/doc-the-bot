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
with open('dataset.json', 'r') as fp:
    sample_data_set = json.load(fp)

print("I'm On")

pd=PyDictionary()

user_session=[]

def learning(domain_context):
    #print(domain_context)
    if (len(domain_context['symptoms']) or len(domain_context['commonsym']) or len(domain_context['diseases'])) == 0:
        return 2
    max_rate={}
    for x,y in domain_context.items():
        for z in y:
            if max_rate.get(z,0)==0:
                max_rate[z]=1
            else: max_rate[z]+=1
    max_x=''
    max_y=0
    for x,y in max_rate.items():
        if y>max_y:
            max_y=y
            max_x=x
    #print(max_x)
    for x,y in domain_context.items():
        for z in y:
            if z==max_x:
                return [x,max_x]

#dendrite to reach neighbour neurons
def dendrite(context, t_id):
    global sample_data_set
    print(context)
    global user_session
    context_domain={
        'diseases':[],
        'symptoms':[],
        'commonsym':[],
    }
    #print(user_session)
    if t_id in user_session:
        context_domain=user_session[user_session.index(t_id)+1]
    for z in range(len(context)):
        for q in range(len(context)):
            sub_context=' '.join(context[z:q+1])
            #print(sub_context)
            for x,y in sample_data_set.items():
                for k in y:
                    if sub_context in k.split() and x=='commonsym':
                        context_domain['commonsym'].append(sub_context)
                    if sub_context in k.split() and x=='symptoms':
                        context_domain['diseases'].append(sample_data_set['disease'][sample_data_set['symptoms'].index(k)])
                    elif sub_context in k.split() and x=='disease':
                        context_domain['diseases'].append(sample_data_set['disease'][sample_data_set['disease'].index(k)])
    print(context_domain)
    result=learning(context_domain)
    if t_id not in user_session:
        user_session.append(t_id)
        user_session.append(context_domain)
    if result==2:
        return 2
    elif ('days' or 'week' or 'weeks' or 'month') not in context:
        return 0
    else:
        if t_id in user_session:
            del user_session[user_session.index(t_id)+1]
            del user_session[user_session.index(t_id)]
        return result
    
        
#Context Synthesization Engine
def CSE(sentence, t_id):
    global pd
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    #print(tagged)
    core_context=[]
    for x in tagged:
        if x[0].lower()=='not':
            core_context.append(x[0].lower())
        elif x[1] in ['VB','VBD','VBG','VBN','VBP','VBZ','RB','RBR','RBS','JJ','JJR','JJS','CD','NN','NNP','NNS','NNPS']:
            core_context.append(x[0].lower())
    if len(core_context)==0:
        return 0
    result=dendrite(core_context,t_id)
    if result==0:
        return 'd'
    else:
        return result
            

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
    result=CSE(m['text'], update.message.chat_id)
    if result==2:
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry I couldn't understand you, would you please elaborate ?")
    elif result=='d':
        bot.sendMessage(chat_id=update.message.chat_id, text="Since how many days ?")
    else:
        if result[0]=='commonsym':
            bot.sendMessage(chat_id=update.message.chat_id, text="It's mostly normar to have "+result[1]+", eat well and excersice and you'll be better than ever before. :)")
        elif result[0]=='diseases':
            bot.sendMessage(chat_id=update.message.chat_id, text="Your symptoms points in the direction of "+result[1]+", I recommend you sould visit a doctor soon.")

dispatcher.add_handler(CommandHandler('start',start))
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

updater.start_polling()