### Installation
Run `chmod +x setup.sh`
Run `./setup.sh`

### Usage
`source .venv/bin/activate` (You must activate the venv where all requirements are installed)

`python3 api.py -url=app.viam.com -org="vijays slam org" -l=abc123 -m=skynet` 

org is case insensitive. 

If you'd like edit the actual config of the robot being uploaded, for now you can edit `template_config.json` to do this(better solution coming).

Make sure to update your Viam CLI before using this since fusionAuth changes went out for the login flow to work. 