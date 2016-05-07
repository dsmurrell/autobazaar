# autobazaar

A tool to install OpenBazaar in the cloud (Digital Ocean for starters).

## usage instructions

```
git clone git@github.com:dsmurrell/autobazaar.git
cd autobazaar
```

Edit the `ab.cfg` file and input your Digital Ocean API token, public ssh_key, OpenBazaar-Server username, and OpenBazaar-Server password.

```
pip install -r requirements.txt
python spin.py
```

