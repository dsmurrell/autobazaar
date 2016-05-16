# autobazaar

A tool to install the OpenBazaar Server in the cloud ([Digital Ocean](https://m.do.co/c/ae523dc7d5e4) for starters). This tool lets you bypass the installation tedium and allows you to run a permanently online store on Digital Ocean's cheapest droplet at $5 a month. The installation process should take somewhere between 8 and 11 minutes. The tool creates the droplet for you, logs on and installs and runs the OpenBazaar-Server, and sets up an init script which will lauch the server if your computer reboots for whatever reason.

Authored by Daniel Murrell of [duosear.ch](https://duosear.ch)

## usage instructions

Follow the numbered steps below. If you encounter any errors see the 'potential blocks' section below. If your problem is not found there shoot me an email at `dsmurrell at gmail dot com`.

1. If you do not already have a [Digital Ocean](https://m.do.co/c/ae523dc7d5e4) account, you can create one with my referral [link](https://m.do.co/c/ae523dc7d5e4) which will give you a free $10 credit equivalent to 2 months of free store hosting.

2. Clone this GitHub repo to any destination on your computer. In the terminal type:
```
git clone https://github.com/dsmurrell/autobazaar.git
cd autobazaar
```

3. Edit the `ab.cfg` file and set up 4 mandatory inputs for autobazaar. 
  - Your write access enabled Digital Ocean API token (generated from the [`API` tab](https://cloud.digitalocean.com/settings/api/tokens) at Digital Ocean), 
  - Your public ssh key. If it already exists, you can find it in the file ~/.ssh/rsa_id.pub If it does not exist, you can generate an ssh key pair using the following command: `ssh-keygen -t rsa -C 'your_email@example.com'`
  - The OpenBazaar-Server username you desire
  - The OpenBazaar-Server password you desire

```
pip install -r requirements.txt
python spin.py
```

## potential blocks

- `Permission denied` error message while running `pip install -r requirements.txt`
  Either use `pip install -r requirements.txt --user` or prepend with `sudo`, or use a python environment manangement system like virtualenv or anaconda so that your python libaries install into a location you have write access to.
- `digitalocean.baseapi.DataReadError: Unable to authenticate you.`
  This means that you've not set your Digital Ocean API token in `ab.cfg` correctly.

