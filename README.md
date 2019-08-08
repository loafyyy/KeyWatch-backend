# KeyWatch-backend

This guide helps you setup the backend server for the Chrome extension. The actual API is in the section below.   

### 1. Set up PostgreSQL (version 11)
##### Mac:  
* Download PostgreSQL: https://postgresapp.com/downloads.html  
* Set up the command line interface (CLI): https://postgresapp.com/documentation/cli-tools.html  

##### Windows:  
* Follow this tutorial:  
https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm

### 2. Clone this repo and install dependencies
* Create a virtual environment for Python 3: https://docs.python.org/3/library/venv.html  
  * virtual environments help manage dependencies and make sure Python code works across computers   
* Activate that virtual environment  
* Clone this repo somewhere  
* cd into the repo   
* Run "pip install -r requirements.txt" - this command downloads all the Python libraries needed to run the backend server  

### 3. Run the server
* cd into the repo if not in there already  
* Run "source setup.sh" - this sets up the environment variables   
* Run "python api.py"  

### 4. Testing to make sure it worked
* Open up another terminal window while the server is running  
* Activate your virtual environment  
* cd into the repo  
* Run "flask resetdb"   
* Run "flask add"  
* Go to "http://127.0.0.1:5000/" in your browser  
* You should see a JSON object - if you do, then it worked!  


# API   

### Resource URL   
http://127.0.0.1:5000/   

### Resource Information   

Response formats: JSON  
Requires authentication: No

### Parameters
| Name | Required | Description | Default Value | Example |
|------|----------|-------------|---------------|---------|
| start_date | No | Start date of keystrokes (inclusive) | None | 2019-08-05 |
| end_date | No | End date of keystrokes (inclusive) | None | 2019-08-07 |
  
If both start_date and end_date are not given, the last 100 keystrokes are returned.  
