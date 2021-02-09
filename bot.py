import requests
from urllib.parse import urlencode
import json

#loop timer
import threading

class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()

event = threading.Event()
#end loop timer

#your bot token
token = 'TOKEN';

base = 'https://api.telegram.org/bot'+token+'/';

#function for sending the message
def send(message):
	try:
		response = requests.get(base+'sendMessage?'+urlencode(message))
		if (response.status_code != 200):
			print('Message sending error: server responded not 200')
			threading.Timer(1, send, message).start()
	except Exception:
		print('Message sending error')
		threading.Timer(1, send, message).start()

#for unique messages, required for Telegram API
lastUpdate = 0

#new messages checker
def getUpdates():
	global lastUpdate
	try:
		response = requests.get(base+'getUpdates?offset='+str(lastUpdate))
		if (response.status_code != 200):
			print('Messages receiving error: server responded not 200')
			return;
	except Exception:
		print('Messages receiving error')
		return;
	updates = json.loads(response.text)['result']
	if (isinstance(updates, list)):
		for i in range(len(updates)):
			#here we're processing the message
			try:
				text = updates[i]['message']['text']
				chat_id = int(updates[i]['message']['chat']['id'])
				update_id = int(updates[i]['update_id'])
				if (lastUpdate <= update_id):
					lastUpdate = update_id + 1
				
				send({'chat_id': chat_id, 'text': respond(updates[i])})
			except ArithmeticError:
				print('Arithmetic error')
			except AttributeError:
				print('AttributeError: object hasn\'t this attribute')
			except NameError:
				print('NameError: variable not found')
			except ValueError:
				print('ValueError: incorrect value')
			except TypeError:
				print('TypeError: incorrect type')
			except Exception:
				print('Other error')
			

#end of new messages checker

	

#loop for our checker, every 2 seconds
bot = ThreadJob(getUpdates, event, 2)
bot.start()

#your message handler
def respond(message):
	#splitting complicated dict to simple variables
	text = message['message']['text']
	#without @ and spaces, just command what to do
	action = text.split(' ')[0].split('@')[0]
	#name, surname and username
	name = message['message']['from']['first_name']
	try:
		surname = message['message']['from']['last_name']
	except Exception:
		surname = ''
	try:
		username = message['message']['from']['username']
	except Exception:
		username = ''
	
	
	#for debugging: print message to console
	print(message)
	
	if (action == '/start'):
		return 'Hello World!'
	
	#user sends /hello Myname, bot responds 'Hello, Myname!', if name is not stated bot responds 'Hello, Noname!'
	if (action == '/hello'):
		if (len(text.split(' ')) > 1):
			helloName = text.split(' ')[1]
		else:
			helloName = 'Noname'
		return 'Hello, ' + helloName + '!'
	
	#info about user
	if (action == '/me'):
		return 'You\'re ' + name + (' ' + surname if surname != '' else '') + (' (@' + username + ')' if username != '' else '');
	
	if (action == '/test'):
		return 'Test response'
	
	#receiving '/sum 1 2 3', sending sum of sequence
	if (action == '/sum'):
		if (len(text.split(' ')) > 1):
			try:
				numbers = list(map(int, text.split(' ')[1:]))
			except Exception:
				return 'You send not integer numbesr sequence'
		else:
			return 'No numbers given'
		return '+'.join([str(int) for int in numbers]) + ' = ' + str(sum(numbers))
	
	if (action == '/weather'):
		return '+25°C'

#end of your message handler
