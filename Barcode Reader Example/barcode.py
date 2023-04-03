'''
Example code for using a barcode scanner with the DataStream API to load Recipes.
This code takes an IP address, and then logs into the machine as the admin user.
After logging in, the code sits and loops thru reading barcodes and sending recipes to the tool.

To accomplish this, first a barcode is entered, then a request for local presence is sent to the tool.
The operator would then walk to the tool and press the local presence button.
Once the button is pressed, a recipe is sent to the tool, started, and control is released back to the tool.
The recipe sent has the name field changed to match the barcode, this changes the display on the machine, and would affect the generated log file.

For this demo, a default recipe is used, but any advanced recipes could be used, and multiple ways of using this functionality are possible.
A couple simple implementations would be a barcode for the recipe name to run, which could be stored on the server or the tool.
Otherwise a lot number of the wafers could be used in the recipe name, making searching thru logfiles easier to trace to specific wafers.

A more complicated system could search a database for the wafers, determine which recipe was needed for that specific wafer, and load to the tool.
'''

######################################################################################################
####### Loading libraries and defining utility functions                                       #######
######################################################################################################

import json # json library to handle json formats when needed.
import requests # requests library to send http requests to the tool.
import time # time library to add delays between requests.
import os # OS library to check if file exists.

def runRecipe(httpSess, ip, recipe):
    # Load the recipe onto the tool
    postResponse = httpSess.post(ip + '/api/control/select', json = recipe)
    # Start the recipe
    postResponse = httpSess.post(ip + '/api/control/run', json = [])
    # Release control to tool so prompts will appear locally
    response = httpSess.get(ip + '/api/control/release')

    # Wait a couple seconds to make sure process state updates
    time.sleep(2)
    # Get the current process state
    response = httpSess.get(ip + '/api/control/query') 
    # Convert to python dictionary
    responseJson = response.json() 

    # While in the running state
    while(responseJson['processState'] == 'running'): 
        # Wait a few seconds
        time.sleep(5)
        # Refresh Status Information
        response = httpSess.get(ip + '/api/control/query')
        responseJson = response.json()

# Function for gaining Local Presence from a tool. 
def getLocalPresence(httpSess, ip):
    # Getting the current status of the tool
    response = httpSess.get(ip + '/api/control/query')
    # Converting the recieved json text into a python dictionary
    responseJson = response.json()

    # Check the current control status
    if(responseJson['inControl']):
      print("Already controlling the tool")

    else:
      print("Not in control of the tool, requesting control.")
      print("Please press the flashing local presence button.")
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
####### Program entry point, checks that the recipe file exists, then logs into tool           #######
######################################################################################################

if(not os.path.isfile("ManualDispenseAdvanced.json")):
    print("Recipe File not found, exiting")
    time.sleep(10)
    exit()

# Open the ManualDispenseAdvanced recipe, and load the json.
with open("ManualDispenseAdvanced.json", "r") as recipeFile:
    recipe = json.load(recipeFile)

# Prompts the users for their tool IP address.
ip = input("Enter the machine ip address\n")
# Formats the ip address to the http protocol.
ip = 'http://' + ip

# Sending the default admin username and password. 
# If you have changed tool users, change this to match.
user = {
  'username': 'admin',
  'password': 'admin2'
}

# Create a session using the requests library.
httpSess = requests.Session()

# Submit a post request to the login interface.
postResponse = httpSess.post(ip + '/auth/login', data = user)

# Check to see if login was successful.
if(postResponse.status_code == 404):
  # Print a message if login failed.
  print("Error logging in, Please check your user credentials. Exiting")
  time.sleep(10)
  exit()

######################################################################################################
####### Loop for reading barcode and running recipe                                            #######
######################################################################################################

while True:
    # Scan a barcode.
    barcode = input("Scan the barcode then press enter\n")

    # Rename the recipe based on the barcode scanned.
    recipe["name"] = "barcode_" + str(barcode) + "_recipe"
    
    # Get Local Presence to send recipe to tool.
    getLocalPresence(httpSess, ip)
    
    # Send the recipe to the tool, and then release control back to tool.
    runRecipe(httpSess, ip, recipe)

