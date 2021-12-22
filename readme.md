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

2. Clone this repo, `cd` into it
3. copy `conf.dist.py` to `conf.py`
4. add your devices to `conf.py`
5. set your output path
6. Run `python main.py`...forever

## Todo

- [x] Add github link to output
- [x] Make it a bit more responsive on mobile
- [ ] Add hourly breakdown, first and last time online
- [ ] Pretty up the output, maybe AJAX or autorefresh or both?
- [ ] Add better running instructions - daemonize this!