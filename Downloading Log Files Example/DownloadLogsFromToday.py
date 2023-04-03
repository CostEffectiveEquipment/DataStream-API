import json # json library to handle json formats when needed.
import requests # requests library to send http requests to the tool
import time # time library to slow down requests
import datetime # date library to get today's date

######################################################################################################
####### Login to the tool                                                                      #######
######################################################################################################

ip = input("Enter the machine ip address\n") # prompts the users for their tool IP address
ip = 'http://' + ip # formats the ip address to make sure it uses the http protocol

# Sending the default admin username and password
# If you have changed tool users, change this to match
payload = { 
  'username': 'admin',
  'password': 'admin2'
}

# Create a session using the requests library
httpSess = requests.Session()

# Submit a post request to the login interface
postResponse = httpSess.post(ip + '/auth/login', data=payload)

# Check to see if login was successful
if(postResponse.status_code == 403): 
  print("Error logging in.") # Print a message if login failed.

######################################################################################################
####### Download Today's Logs                                                                  #######
######################################################################################################

# Get today's date
now = datetime.datetime.now()

# Format a payload to request logs from today, with excel format
payload = { 
  'timestamp': now.strftime('%m-%d-%Y %H:%M'), #Formatting today's date to the format required by the endpoint
  'format': 'xlsx' # choosing xlsx format
}

# Post the request to the download all logs for a specific day endpoint
postResponse = httpSess.post(ip + '/api/logging/downloadDay', data=payload)

# Open a file to write the received zip file, and automatically close when done
with open("ApogeeLogs_" + now.strftime('%m-%d-%Y') + ".zip", 'wb') as zipFile:
    # Write the content received to the zip file
    zipFile.write(postResponse.content)