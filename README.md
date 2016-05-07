# autobazaar

A tool to install OpenBazaar in the cloud (Digital Ocean for starters). This tool let's you bypass the installation tedium and allows you to run a permanently online store on Digital Ocean's cheapest droplet at $5 a month.

## usage instructions

Before using this script you will need to create a Digital Ocean account.

```
git clone git@github.com:dsmurrell/autobazaar.git
cd autobazaar
```

Edit the `ab.cfg` file and input your Digital Ocean API token (obtained from the [`API` tab](https://cloud.digitalocean.com/settings/api/tokens) at Digital Ocean), public ssh_key, OpenBazaar-Server username, and OpenBazaar-Server password.

```
pip install -r requirements.txt
python spin.py
```

