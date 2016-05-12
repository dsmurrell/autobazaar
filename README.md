# autobazaar

A tool to install the OpenBazaar Server in the cloud ([Digital Ocean](https://m.do.co/c/ae523dc7d5e4) for starters). This tool lets you bypass the installation tedium and allows you to run a permanently online store on Digital Ocean's cheapest droplet at $5 a month. The installation process should take somewhere between 8 and 11 minutes.

## usage instructions

Before using this tool you will need to create a Digital Ocean account. First run:

```
git clone https://github.com/dsmurrell/autobazaar.git
cd autobazaar
```

Edit the `ab.cfg` file and input your write access enabled Digital Ocean API token (generated from the [`API` tab](https://cloud.digitalocean.com/settings/api/tokens) at Digital Ocean), public ssh_key, OpenBazaar-Server username, and OpenBazaar-Server password. Then run:

```
pip install -r requirements.txt
python spin.py
```

If installing the requirements fails due to a `Permission denied` error, either use sudo (not recommended) or use a python environment manangement system like virtualenv or anaconda.

