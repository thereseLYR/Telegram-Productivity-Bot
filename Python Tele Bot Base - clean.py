# Thal's Tele Bot API key: :)
# Based on long polling
# to-do list: store tasklist and progress in CSV,   DONE
# retrieve tasklist and progress via file opening.  DONE
# user tasklist lookup,
# progress checking, i.e SHOWDAY                    Kind of? shows ALL progress, unformatted. show last line instead?
# clearing tasklist                                 DONE
# multi-users                                       DONE
# custom keyboards to 1-click write progress        probably needs the library to do that
# formatting SHOWTASKS                              DONE

import requests as requests
import csv
import datetime

APIurl = 'https://api.telegram.org/bot[INSERT YOUR OWN URL HERE]'


def set_filepath(chatid):  # place this at the beginning of every update cycle
    # chat_ID is an integer
    path = str(chatid) + '.csv'
    print('Set filepath as: ', path)
    return path


def write_tasks(task_text, path):
    f = open(path, "a+")
    f.write(task_text + ",")
    f.close()


def write_progress(task_text, given_datetime, filepath):
    # to-do: lookup and amend the correct entry instead of having to do things sequentially
    f = open(filepath, "a")
    f.write(task_text + '(' + str(given_datetime) + ')' + ",")
    f.close()


def write_newline(path):
    f = open(path, "a")
    f.write('\n')
    f.close()


def show_tasks(update, path):  # returns the first line of .csv, which should be tasks
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        row1 = next(reader)  # gets the first line
        print(row1, type(row1))
    send_message(get_chat_ID(update), str(row1))


def show_day(update, path):  # returns last line of CSV file as a message
    with open(path, 'r') as f:
        last_line = f.readlines()[-1]
    print(last_line, type(last_line))
    send_message(get_chat_ID(update), str(last_line))


def show_progress(update, path):  # still needs to be formatted
    with open(path, 'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        lst = list(readCSV)
    send_message(get_chat_ID(update), str(lst))


def clear_all_tasks(path):
    with open(path, "w"):  # deletes everything, leaving a blank .csv file
        pass


def format_datetime(unix_timestamp):  # takes a unix timestamp string and returns a formatted datetime string
    timestamp = datetime.datetime.fromtimestamp(int(unix_timestamp))
    formatted_datetime_string = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime_string


def get_username(update):  # unused so far, can be used later
    username = update["message"]["chat"]["username"]
    return username


def get_datetime(update):  # returns a datetime unix timestamp as integer
    temp_datetime = update["message"]["date"]
    return temp_datetime


def get_chat_ID(update):
    chat_ID = update["message"]["chat"]["id"]
    return chat_ID  # chat_ID is an integer.


def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text


def get_last_update(req):
    response = requests.get(req + 'getUpdates')
    response = response.json()
    result = response['result']
    total_updates = len(result) - 1
    return result[total_updates]  # gets last recorded message update


def send_message(chat_id, message_text):
    response = requests.post(APIurl + 'sendMessage?chat_id=' + str(chat_id) + '&text=' + message_text)
    return response


def main():
    update_ID = get_last_update(APIurl)["update_id"]
    # print('current update ID: ' + str(update_ID))
    while True:
        update = get_last_update(APIurl)
        if update_ID == update['update_id']:

            filepath = set_filepath(get_chat_ID(update))  # refresh filepath after every message

            if get_message_text(update) == "START":
                send_message(get_chat_ID(update), 'Hello! Please send me your tasks. \n\nStart each task with TASK%, '
                                                  'followed by the task name. \nWhen you are done, reply with '
                                                  'RETURNTASKLIST')
                temp_tasklist = []

            elif get_message_text(update).startswith('TASK%'):
                rawmessage = get_message_text(update)
                newtask = rawmessage[5:]  # strip first 5 characters, ie TASK%
                write_tasks(newtask, filepath)  # TO_DO: check if there is prior history
                if temp_tasklist is []:
                    temp_tasklist.append(newtask)
                    send_message(get_chat_ID(update), 'New Task Added.')
                else:
                    send_message(get_chat_ID(update), 'Please start your tasklist first.')

            elif get_message_text(update) == 'RETURNTASKLIST':  # DOES NOT INTERFACE WITH CSV
                tasklist_string = ''
                for task in temp_tasklist:
                    tasklist_string = tasklist_string + str(task) + '\n'
                tempmessage = 'Check over your tasks: \n' + tasklist_string
                send_message(get_chat_ID(update), tempmessage)
                send_message(get_chat_ID(update), 'If all is OK, reply STARTACCOUNTABILITY')
                # to do: change this confirmation to button interface

            elif get_message_text(update) == 'STARTACCOUNTABILITY':
                temp_tasklist = []
                write_newline(filepath)
                send_message(get_chat_ID(update),
                             "Okay, tell me when you've done what you set out to do. \nSend each task as a separate "
                             "message, and start with DONE%")

            elif get_message_text(update) == 'ENDDAY':
                write_newline(filepath)
                send_message(get_chat_ID(update), "That's all for today!")
                # expand by checking task progress against task list.

            elif get_message_text(update) == 'SHOWTASKS':
                show_tasks(update, filepath)

            elif get_message_text(update) == 'SHOWDAY':
                show_day(update, filepath)

            elif get_message_text(update) == 'SHOWPROGRESS':
                show_progress(update, filepath)

            elif get_message_text(update).startswith('DONE%'):
                rawmessage = get_message_text(update)
                donetask = rawmessage[5:]  # strip first 5 characters, ie DONE%
                unix_timestamp_string = get_datetime(
                    update)  # this will be a string, need to convert to int to use with the datetime module
                final_datetime = format_datetime(unix_timestamp_string)
                write_progress(donetask, unix_timestamp_string, filepath)
                message = 'You finished ' + donetask + ' at ' + final_datetime + '!'
                send_message(get_chat_ID(update), message)

            elif get_message_text(update) == 'DELETETASKS':
                clear_all_tasks()
                temp_tasklist = []
                send_message(get_chat_ID(update), "All tasks deleted.")

            else:
                send_message(get_chat_ID(update),
                             'I have no idea what you want me to do. Help.\n\nPlease message my owner, @usnfn, '
                             'for instructions on how to use me.')
            update_ID += 1


if __name__ == '__main__':
    main()
