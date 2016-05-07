# autobazaar

A tool to install the OpenBazaar Server in the cloud ([Digital Ocean](https://cloud.digitalocean.com) for starters). This tool let's you bypass the installation tedium and allows you to run a permanently online store on Digital Ocean's cheapest droplet at $5 a month. The installation process should take somewhere between 8 and 11 minutes.

## usage instructions

Before using this tool you will need to create a Digital Ocean account. First run:

```
git clone https://github.com/dsmurrell/autobazaar.git
cd autobazaar
```

Edit the `ab.cfg` file and input your write access enabled Digital Ocean API token (generated from the [`API` tab](https://cloud.digitalocean.com/settings/api/tokens) at Digital Ocean), public ssh_key, OpenBazaar-Server username, and OpenBazaar-Server password. Then run:

```
sudo pip install -r requirements.txt
python spin.py
```

