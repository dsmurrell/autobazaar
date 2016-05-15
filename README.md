# autobazaar

A tool to install the OpenBazaar Server in the cloud on [Digital Ocean](https://m.do.co/c/ae523dc7d5e4) for starters (that link is my referral link and gives you a free 10$ or 2 months store time if you are new to Digital Ocean). This tool lets you bypass the installation tedium and allows you to run a permanently online store on Digital Ocean's cheapest droplet at $5 a month. The installation process should take somewhere between 8 and 11 minutes.

## usage instructions

Follow the numbered steps below. If you encounter any errors see the 'potential blocks' section below. If your problem is not found there shoot me an email at `dsmurrell at gmail dot com`.

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

## potential blocks

### `Permission denied` error message while running `pip install -r requirements.txt`

Either use `pip install -r requirements.txt --user` or prepend with `sudo`, or use a python environment manangement system like virtualenv or anaconda so that your python libaries install into a location you have write access to.

