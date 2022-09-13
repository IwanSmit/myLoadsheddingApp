#myLoadsheddingApp
#import libraries
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import json
from bs4 import BeautifulSoup
import time
import schedule
import time
import os
import sys
import openpyxl
import datetime


SCOPES = ['https://www.googleapis.com/auth/calendar']

# global stage, to test for repeating stages
prev_status = ""

# global var to check whether times on stages have passed
old_time = True

# loading in excel file with loadshedding times
wrkbk = openpyxl.load_workbook("Loadshedding.xlsx")

# global var to check whether or not same stage was previously implimented
stage_num = 0

# path to root, Not permanent fix, needs better solution - check dir for .txt file
url = 'C:\\Users\[OwnDir]\Documents'

# Closes app
def End():
    print("Exiting Program")
    sys.exit()

# Return time in HH:MM:SS - 17:45:17
def check_time():

    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M:%S")
    return current_time

# Returns date 2022-09-06 #YYYY, MM, DD
def currDate():
    currentDate = str(datetime.date.today())
    return currentDate

# Returns day - 09 - for 9th
def check_day():

    currentDate = currDate()

    res = currentDate[8:]
    if res[0] == '0':
        res = res[1 : : ]
        day = int(res)
        return day
    else:
        day = int(res)
        return day

# checks if scheduled time have passed or not
def check_old_time(start_time):

    global old_time

    start_time = start_time
    current_time = check_time()
    if start_time[0:5] >= current_time[0:5]:
        old_time = False
        return old_time
    else:
        return old_time

# Returns stage via API - exp, 3
def get_load_status():

    res = requests.get('https://loadshedding.eskom.co.za/LoadShedding/GetStatus')

    stage = res.text[:1]

    return stage

# Calls this function every 5 minutes
def call_status():

    global stage_num

    status = get_load_status() #3

    if status != '99':
        tmp_int = int(status) # 3

        stage_num = tmp_int - 1 #0 -> 3 ->  2

        print('Stage currently is: Stage ' + str(stage_num))

        day = check_day() #7

        main_sys(status, day) # ( 3, 7)

        print('End Of Call')
    else:
        print('API is broken, App will be stopped')
        End()

# Function to simplify code and to do all logic
def main_sys_call(day):

    global wrkbk
    global stage_num
    global old_time
    day = day

    #prev_status = prev_status
    #status = "stage 1"
    #compare status

    ws = wrkbk['Stage_' + str(stage_num)]

    #loop through excel
    for row in ws.iter_rows():
        val = row[(day + 1)].value
        if val == stage_num:
            start_time = str(row[0].value)
            end_time = str(row[1].value)  # Need to have global variables
            start_date = str(currDate())
            end_date = str(currDate())
            print(f'{start_time} {end_time}')
            #2022-09-09 #YYYY, MM, DD
            if end_time[0:5] == '00:30':
                temp_end_date = end_date[8:]# getting date
                temp_end_date = str(int(temp_end_date)+1) # converting to int and adding 1 then back to str
                end_date = con_date[0:8] + temp_end_date
                #call calander function with time information and add to calander
                create_calendar_events(start_time, end_time, start_date, end_date)
            else:
                check_old_time(start_time)
                if old_time == False:
                    create_calendar_events(start_time, end_time, start_date, end_date)
                else:
                    print('Old Time')

# Main sys
def main_sys(status, day):

    status = status
    day = day
    global prev_status

    if status != '1': # 1 = not loadshedding
        if status == '2' and prev_status != status: # stage 1
            prev_status = status
            main_sys_call(day) # call to test all conditions

        elif status == '3' and prev_status != status: # stage 2
            prev_status = status
            main_sys_call(day)

        elif status == '4' and prev_status != status: # stage 3
            prev_status = status
            main_sys_call(day)

        elif status == '5' and prev_status != status: # stage 4
            prev_status = status
            main_sys_call(day)

        elif status == '6' and prev_status != status: # stage 5
            prev_status = status
            main_sys_call(day)

        elif status == '7' and prev_status != status: # stage 6
            prev_status = status
            main_sys_call(day)

        else:
            if prev_status == status:
                print('Stage Already Implimented')
            else:
                print('No stage found')
    else:
        if status == '1':
            print('No Loadshedding!')
        else:
            print('Something Went Wrong!')

# function to create events
def create_calendar_events(start_time, end_time, start_date, end_date):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    ###
    event = {
      'summary': 'LOADSHEDDING',
      'location': 'Home',
      'description': 'Loadshedding APP.',
      'start': {
        'dateTime': start_date + 'T' + start_time,
        'timeZone': 'Africa/Windhoek',
      },
      'end': {
        'dateTime': end_date + 'T' + end_time,
        'timeZone': 'Africa/Windhoek',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
      ],
##      'attendees': [
##        {'email': 'lpage@example.com'},
##        {'email': 'sbrin@example.com'},
##      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 0.5 * 60},
          {'method': 'popup', 'minutes': 5},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    #####
    
    print('Getting the upcoming 5 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


# Main function, being initialized by __nam__ == '__main__'
def main():
    schedule.every(0.166666).minutes.do(call_status)

    while True:
            schedule.run_pending()
            for fname in os.listdir(url):
                    if fname.endswith('.txt'):
                            time.sleep(0.3)
                            End()
            time.sleep(1)

if __name__ == '__main__':
    main()