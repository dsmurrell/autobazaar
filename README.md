NB. Windows users: this may or may not work from Windows. I've not been able to test that it works. If you manage to get it to work, please let me know. I will try to test it on Windows soon. I'm happy to set your server up for you if you give me your Digital Ocean API token.

# autobazaar

A tool to install the OpenBazaar Server in the cloud ([Digital Ocean](https://m.do.co/c/ae523dc7d5e4) for starters). This tool lets you bypass the installation tedium and allows you to run a number of permanently online stores on Digital Ocean's cheapest droplet at $5 a month. The installation process should take somewhere between 8 and 11 minutes. The tool creates the droplet for you, logs on and installs and runs the OpenBazaar servers. It also creates upstart scripts which will lauch the servers if your computer reboots or your servers crash for whatever reason.

*authored by* Daniel Murrell of [duosear.ch](https://duosear.ch)

## usage instructions

Follow the numbered steps below. If you encounter any errors see the 'potential blocks' section below. If your problem is not found there shoot me an email at `dsmurrell at gmail dot com`.

1. If you do not already have a [Digital Ocean](https://m.do.co/c/ae523dc7d5e4) account, you can create one with my referral [link](https://m.do.co/c/ae523dc7d5e4) which will give you a free $10 credit equivalent to 2 months of free store hosting.

2. Clone this GitHub repo to any destination on your computer. In the terminal type:
  ```
  git clone https://github.com/dsmurrell/autobazaar.git
  cd autobazaar
  ```

3. Edit the `ab.cfg` file and set up 2 mandatory inputs for autobazaar. 
  - Your write access enabled Digital Ocean API token which can be generated from [Digital Ocean](https://cloud.digitalocean.com/settings/api/tokens)
  - Your public ssh key. If it already exists, you can find it using `at ~/.ssh/id_rsa.pub`. If it does not exist, you can generate an ssh key pair using the following command: `ssh-keygen -t rsa -C 'your_email@example.com'`

4. Install autobazaar's dependencies and run it by typing the following two lines in the terminal:
  ```
  pip install -r requirements.txt
  python autobazaar.py -n num_stores -u username
  ```
  Where `num_stores` is the number of OpenBazaar stores you want to run (5 or less) and `username` is the username that you use to log into them. The `autobazaar.py` script should run for between 8 and 11 minutes and when it's done, it will print out the IP address, usernames and passwords to configure a new server connections.
  
5. Set up new server configurations. If you don't have OpenBazaar you can obtain it from www.openbazaar.org. Once OpenBazaar is installed, add new server configurations by navigating (top right of screen) menu > default > + New Server and entering the IP address, usernames and passwords obtained in the previous step.

6. [Optional] For vendors with existing stores who want to move their store over to the droplet, you can replace the contents of the folders in the `~/store` folder on the droplet with the contents of your database folder on your computer. The database folder can be found in:
  - Window: C:\Users\Username\AppData\Roaming\openbazaar 
  - Linux: ~/.openbazaar
  - OSX: ~/Library/Application Support/OpenBazaar

  Since your public ssh key is already on the droplet, `ssh root@droplet_ip` should ssh you in and you can use `scp` to carry out the transfer. Remember to restart the OpenBazaar server once you have copied the contents over. Restarting the server is most easily done by rebooting the droplet. This can be done using through [Digital Ocean](https://m.do.co/c/ae523dc7d5e4) or by sshing in and using the `sudo reboot` command.

any questions? email me at `dsmurrell at gmail dot com`. 

## potential blocks

- `Permission denied` error message while running `pip install -r requirements.txt`
  Either use `pip install -r requirements.txt --user` or prepend with `sudo`, or use a python environment manangement system like virtualenv or anaconda so that your python libaries install into a location you have write access to.
- `digitalocean.baseapi.DataReadError: Unable to authenticate you.`
  This means that you've not set your Digital Ocean API token in `ab.cfg` correctly.
- `digitalocean.baseapi.DataReadError: The image you specified is not available in the selected region, you can transfer it to this region from the images pages.`
  This means that the image for the smallest Ubuntu instance is not available in the region that you selected in the optional section of the `ab.cfg` file.

block doesn't exist? email me at `dsmurrell at gmail dot com`.

