# Legba The Net-Tracker

Track how long devices have been online on your LAN. Ideal for parents who want to have
and open dialog with their kids about how long they should be online on a day to day
basis. These same parents need to also enjoy setting up random Python projects ;)

Assumes that each device has been statically assigned an IP by your DHCP server.

Named after [Papa Legba](https://en.wikipedia.org/wiki/Papa_Legba)

## Prerequisites

* python
* web accessible directory to view output - defaults to `/var/www/html/index.html`

## Install

1. create a `legba` user who's home directory is `/home/legba`
2. Clone this repo, `cd` into it so you're in `/home/legba/legba`
3. Copy `conf.dist.py` to `conf.py`
4. Add your devices to `conf.py` in the `trackme` variable.
5. Set your output path in `conf.py` in the `html_file` variable
6. Install all the python prerequisites with `pip3 install -r requirements.txt`
7. Copy the systemd file into place, reload systemd, start and enable it:

    ```    
    sudo cp legba.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable legba
    sudo systemctl start legba
    ```

## Todo

- [x] Add github link to output
- [x] Make it a bit more responsive on mobile
- [X] Add first and last time online
- [ ] Maybe AJAX or autorefresh or both?
- [X] Add better running instructions - daemonize this!
