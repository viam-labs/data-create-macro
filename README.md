### Installation
Create a virtual environment using `python3.12 -m venv "YOUR_NAME_HERE"`
Activate your venv using `source YOUR_NAME_HERE/bin/activate`
Install dependencies using `python3 -m pip install -r requirements.txt`
Create a .env file that looks like this:
```
URL=...(Include https in your url)
ORG_NAME=the org name you want to add a robot too
```
Editing your env file is the main way of passing info to the script for the time being. For the url, copy paste from the deploy comment link into that file, delete the trailing / (Ill add validation for this later). Org name is case insensitive. If you'd like edit the actual config of the robot being uploaded, for now you can edit `template_config.json` to do this(better solution coming).

Make sure to update your Viam CLI before using this since fusionAuth changes went out for the login flow to work. 

Example command: `python3 api.py`