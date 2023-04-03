import json # json library to handle json formats when needed.
import requests # requests library to send http requests to the tool
import time # time library to slow down requests

######################################################################################################
####### Login to the tool                                                                      #######
######################################################################################################

ip = input("Enter the machine ip address\n") # prompts the users for their tool IP address
ip = 'http://' + ip # formats the ip address to make sure it uses the http protocol

# Sending the default admin username and password.
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
####### Gain Local Presence                                                                    #######
######################################################################################################

# Get the current status of the tool
response = httpSess.get(ip + '/api/control/query')
# Converting the recieved json text into a python dictionary
responseJson = response.json()

# Check the current control status
if(responseJson['inControl']):
  print("Already controlling the tool")

else:
  print("Not in control of the tool, requesting control.")
  print("Please press the flashing local pressence button.")
  # Request for local presence
  response = httpSess.get(ip + '/api/control/presence')
  
  # While I don't have control
  while( not responseJson['inControl']):
    # Wait a little while
    time.sleep(5)
    # Repeat checking tool status
    response = httpSess.get(ip + '/api/control/query')
    responseJson = response.json()
    
  print("Control of the tool gained")


######################################################################################################
####### Run a Manual Recipe                                                                    #######
######################################################################################################

# Define a recipe that spins the servo at 100 RPM, waits 30 seconds, then stops the servo.
payload={ 
    "type":"manual", # manual command
    "steps":[ #The recipe steps
        {
        "description":"",
        "primitive":"command", # define what we are doing, a command
        "control":"servo", # define what we commanding, the servo
        "action":"set", # define we are commanding the servo to do, set parameters to 
        "parameters":{"speed":100,"accel":6000,"osc":0} # parameters for a servo set action
        },
        {
        "description":"",
        "primitive":"delay", # define what we are doing, a delay
        "control":"fixedTime", # delay only has 1 control, a fixed time delay
        "action":"delay", # the action is to delay
        "parameters":{"time": 30} # parameters is how long to delay, 30 seconds
        },
        {
        "description":"",
        "primitive":"command", # same as previous servo set
        "control":"servo",
        "action":"set",
        "parameters":{"speed":0,"accel":6000,"osc":0}
        }
    ]
}

# Send the recipe to be run as a manual command
postResponse = httpSess.post(ip + '/api/control/manual',json=payload) 
# Wait a little bit
time.sleep(2) 

# Get the current process state
response = httpSess.get(ip + '/api/control/query')
# Convert to python dictionary
responseJson = response.json()

while(responseJson['processState'] == 'running'):
    # Print approximate time remaining
    print("Process Running, Time Remaining is " + str(responseJson['timeRemaining']))
    time.sleep(5) #wait a few seconds
    response = httpSess.get(ip + '/api/control/query') # Get a fresh status packet.
    responseJson = response.json()
print("Process Done")

######################################################################################################
####### Run a recipe stored on the tool                                                        #######
######################################################################################################

# Get a list of all recipes
response = httpSess.get(ip + '/api/recipe/search')
# Convert to python dictionary
responseJson = response.json()

# Iterate thru all recipes
for recipe in responseJson:
    # Print their unique id, aka name
    print(recipe['uid'])

# Print the name of the first recipe returned
print("Running Recipe " + responseJson[0]['uid'])
# Tell the tool to set the recipe as the active/selected recipe
postResponse = httpSess.post(ip + '/api/control/select', json = responseJson[0]['recipe']) 
# Start the recipe
postResponse = httpSess.post(ip + '/api/control/run', json = []) 
# Print the response
print(postResponse.text) 

# Get the current process state
response = httpSess.get(ip + '/api/control/query')
# Convert to python dictionary
responseJson = response.json()

# While in the running state
while(responseJson['processState'] == 'running'):
    
    time.sleep(5) # Wait a few seconds
    
    # Refresh Status Information
    response = httpSess.get(ip + '/api/control/query') 
    responseJson = response.json()
    
    # Check for actions needed to be performed (in this case, the end of process acknowledgement)
    if(responseJson['pendingAction']): 
        print(responseJson['pendingAction']) # print the pending action
        
         # If a process complete action
        if(responseJson['pendingAction']['action'] == 'processComplete'):
            
            # Acknowledge the end of the process
            postResponse = httpSess.post(ip + '/api/control/response', json = {
                # id must equal the processStep, so you acknowledge the message of that step.
                'id': responseJson['processStep'],
                # type of response is a userResponse
                'type': 'userResponse',
                # responseType is acknowledge
                'payload': { 
                    'responseType': 'ack',
                    }
                }
            )