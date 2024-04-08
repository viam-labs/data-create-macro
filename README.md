### Installation
Run `chmod +x setup.sh`
Run `./setup.sh`

### Usage
`source .venv/bin/activate` (You must activate the venv where all requirements are installed)

`python3 api.py -url=app.viam.com -org="vijays slam org" --location_id=abc123 --machine_name=skynet --binary_count=1 --tabular_count=1 --frequency=1`

This command is identical to the above one, but the options are shorthanded. 

`python3 api.py -url=app.viam.com -org="vijays slam org" -l=abc123 -m=skynet -b=1 -t=1 -f=1`

To get all cli options:
`python3 api.py -h`

org is case insensitive. 

Make sure to update your Viam CLI before using this since fusionAuth changes went out for the login flow to work. 