# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import subprocess, sqlite3, time, conf, os
from datetime import datetime
from sqlite3 import Error
from pathlib import Path


def check_config():
    html_file = Path(conf.html_file)
    if not html_file.is_file():
        print("Error: \"",  conf.html_file, "\" is not a file. See conf.html_file in conf.py.")
        exit(1)
    try:
        html_file = open(conf.html_file, "a")
    except PermissionError:
        print("Error: \"",  conf.html_file, "\" is not writable by Legba. Ensure process can write to it.")
        exit(1)
    if not html_file.writable():
        print("Error:",  conf.html_file, "is not writable by Legba.")
        exit(1)


# thanks https://stackoverflow.com/a/10402323
def ping(host):
    """ Ping a host on the network. Returns boolean """
    command = ["ping", "-c", "1", "-w1", host]
    return subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    sqlite = None
    try:
        sqlite = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    try:
        create_table_sql = """ CREATE TABLE IF NOT EXISTS status (
                id integer PRIMARY KEY,
                name text NOT NULL,
                state text NOT NULL,
                date text
            ); """
        c = sqlite.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

    return sqlite


def record(sqlite, name, state):
    """
    record a new activity
    :param sqlite:
    :param name:
    :param state:
    :return:
    """

    sql = ''' INSERT INTO status(name,state,date)
              VALUES(?,?,?) '''
    cur = sqlite.cursor()
    activity = (name, state, datetime.now())
    cur.execute(sql, activity)
    sqlite.commit()

    return cur.lastrowid


def get_days_activity(sqlite, date):
    """
    record a new activity
    :param sqlite:
    :param date:
    :return rows:
    """

    sql = ''' select name, sum(state) as summed from status where state=1 and date like ? group by name; '''
    cur = sqlite.cursor()
    # todo - maybe cleanse/validate the date var? could lead to more data getting selected than a single date
    cur.execute(sql, [date + "%"])

    return cur.fetchall()


def get_first_and_last(sqlite, date, person):
    """
    record a new activity
    :param sqlite:
    :param date:
    :param person:
    :return rows:
    """

    sql = ''' select time(min(date)) as earliest, time(max(date)) as latest 
        from status 
        where state=1 and date like ? and name = ? '''
    cur = sqlite.cursor()
    # todo - maybe cleanse/validate the date var? could lead to more data getting selected than a single date
    cur.execute(sql, [date + "%", person])
    result = cur.fetchone()
    first_raw = datetime.strptime(result[0], "%H:%M:%S")
    last_raw = datetime.strptime(result[1], "%H:%M:%S")
    return {
        'first': first_raw.strftime("%-I:%M%p")[:-1],
        'last': last_raw.strftime("%-I:%M%p")[:-1],
        'first_label': int(first_raw.strftime("%H")),
        'last_label': int(last_raw.strftime("%H"))
    }


def get_total_by_hour(sqlite, date, person):
    """
    record a new activity
    :param sqlite:
    :param date:
    :param person:
    :return rows:
    """

    sql = ''' select 
            strftime('%H', date) as hour, 
            count(*) as count
        from status 
        where state=1 and date like ? and name = ? 
        GROUP BY hour '''
    cur = sqlite.cursor()
    # todo - maybe cleanse/validate the date var? could lead to more data getting selected than a single date
    cur.execute(sql, [date + "%", person])
    hours = cur.fetchall()

    # todo - this feels kinda clumsy way to prep the final hours_cooked array with while then the for loops
    i = 0
    hours_cooked = []
    while i < 24:
        hours_cooked.append(0)
        i += 1

    for hour in hours:
        cur_hour = int(hour[0])
        hours_cooked[cur_hour] = hour[1]

    return hours_cooked


def is_online(ips):
    for ip in ips:
        if ping(ip):
            return True
    return False


def output_stats_html(sqlite, date):
    stats = {
        'last_update': datetime.now().strftime("%-I:%M %p"),
        'date': datetime.now().strftime("%Y-%m-%d"),
        'people': {}
    }
    for row in get_days_activity(sqlite, date):
        person = row[0]
        total_minutes = row[1]
        stats["people"][person] = {}
        stats["people"][person]['hourly'] = get_total_by_hour(sqlite, date, person)
        stats["people"][person]['labels'] = get_first_and_last(sqlite, date, person)
        # one liner FTW! thanks https://stackoverflow.com/a/65422487
        stats["people"][person]['total'] = "{}h {}m ".format(*divmod(total_minutes, 60))

    html_dir = os.path.dirname(os.path.abspath(conf.html_file))
    ajax = html_dir + "/ajax"
    ajax_file = open(ajax, "w")
    ajax_file.write(json.dumps(stats))

    # copy in happy histogram files if not there
    copy_files = ['HappyDayHistogram.min.css', 'HappyDayHistogram.min.js', 'VeveLegba.svg']
    for file in copy_files:
        temp = html_dir + "/" + file
        if not os.path.exists(temp):
            read_file = open("html/" + file, "r").read()
            open(temp, "w").write(read_file)

    file = open(conf.html_file, "w")
    html_data = open("html/header.html", "r").read()
    html_data += open("html/footer.html", "r").read()
    file.write(html_data)


def main():
    check_config()
    sqlite = create_connection(r"./legba.db")
    print('Legba started')

    output_stats_html(sqlite, datetime.now().strftime("%Y-%m-%d"))
    while 1 == 1:
        count = 0
        online = 0
        for name in conf.trackme.keys():
            ips = conf.trackme[name]
            result = is_online(ips)
            record(sqlite, name, result)
            count += 1
            if result:
                online += 1

        output_stats_html(sqlite, datetime.now().strftime("%Y-%m-%d"))
        print("Legba " + str(online) + " of " + str(count) + " people online")
        time.sleep(60)


if __name__ == '__main__':
    main()
