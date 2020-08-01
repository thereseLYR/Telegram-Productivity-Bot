#   Thal's Tele Bot API key: 1385620216:AAFrwzH2kPNdW9W8jAvGgckvH2akfi3ybH8
#   Based on long polling
#   to-do list: store tasklist and progress in CSV, retrieve tasklist and progress via file opening. user tasklist lookup, progress checking, clearing tasklist

import requests as requests

APIurl = 'https://api.telegram.org/bot1385620216:AAFrwzH2kPNdW9W8jAvGgckvH2akfi3ybH8/'
# OWNERchatID = '511564399'
tasklist = []

def get_chat_ID(update):
    chat_ID = update["message"]["chat"]["id"]
    #print(chat_ID)
    return chat_ID

def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text

def get_last_update(req):
    response = requests.get(req + 'getUpdates')
    response = response.json()
    result = response['result']
    total_updates = len(result) - 1
    return result[total_updates] #gets last recorded message update

# def send_message(chat_id, message_text):
#     params = {'chat_id':chat_id, 'text':message_text}
#     response = requests.post(APIurl + 'sendMessage', data=params)
#     return response

def send_message(chat_id, message_text):
    response = requests.post(APIurl + 'sendMessage?chat_id=' + str(chat_id) + '&text=' + message_text)
    return response

def main():
    update_ID = get_last_update(APIurl)["update_id"]
    print('current update ID: ' + str(update_ID))
    while True:
        update = get_last_update(APIurl)
        if update_ID == update['update_id']:
            if get_message_text(update) == "START":
                send_message(get_chat_ID(update), 'Hello! Please send me your tasks. \nStart each task with TASK%, followed by the task name. \nWhen you are done, reply with RETURNTASKLIST')
            elif get_message_text(update).startswith('TASK%'):
                rawmessage = get_message_text(update)
                newtask = rawmessage[5:]
                tasklist.append(newtask)
                send_message(get_chat_ID(update), 'New Task Added.')
            elif get_message_text(update) == 'RETURNTASKLIST':
                tasklist_string = ''
                for task in tasklist:
                    tasklist_string = tasklist_string + str(task) + '\n'
                tempmessage = 'Check over your tasks \n' + tasklist_string
                send_message(get_chat_ID(update),tempmessage)
                send_message(get_chat_ID(update), 'If all is OK, reply STARTACCOUNTABILITY')
            elif get_message_text(update) == 'STARTACCOUNTABILITY':
                send_message(get_chat_ID(update), "I'll be working on this!")
            else:
                send_message(get_chat_ID(update), 'I have no idea what you want me to do. Help.')
            update_ID += 1

# main()

if __name__ == '__main__':
    main()