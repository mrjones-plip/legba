# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import subprocess, sqlite3, time, conf, os
from datetime import datetime
from sqlite3 import Error


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
    return {
        'first': datetime.strptime(result[0], "%H:%M:%S").strftime("%-I:%M%p")[:-1],
        'last': datetime.strptime(result[1], "%H:%M:%S").strftime("%-I:%M%p")[:-1]
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
        if hour[0] == '00':
            cur_hour = 0
        else:
            cur_hour = int(hour[0].lstrip('0'))
        hours_cooked[cur_hour] = hour[1]

    return hours_cooked


def is_online(ips):
    for ip in ips:
        if ping(ip):
            return True
    return False


def output_stats_html(sqlite, date):
    # select name,strftime('%m-%d-%Y %H', date) as thedate,sum(state) as summed from status where state=1 group by name,thedate order by name,thedate;
    # select name, sum(state) as summed from status where state=1 and date like '2021-12-20%' group by name;
    counts_by_day = get_days_activity(sqlite, date)
    usage = []
    for row in counts_by_day:
        person = row[0]
        total_minutes = row[1]
        first_last = get_first_and_last(sqlite, date, person)
        hourly_breakdown = get_total_by_hour(sqlite, date, person)
        # one liner FTW! thanks https://stackoverflow.com/a/65422487
        total_formatted = "{}h {}m ".format(*divmod(total_minutes, 60))
        usage[person]['hourly'] = hourly_breakdown
        usage[person]['first'] = first_last['first']
        usage[person]['last'] = first_last['last']
        usage[person]['total'] = total_formatted
    usage['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    table = pandas.DataFrame(tableData, columns=tableHead)
    html_data = open("html/header.html", "r").read()
    html_data += "\n<script> " + json.dumps(js_data) + "</script>"
    html_data += "<h2>Activity for " + str(date) + "</h2>"
    html_data += "<p>Last Updated: " + datetime.now().strftime("%-I:%M %p") + "<p>"
    html_data += table.to_html()

    # todo - gracefully handle when these file can't be written to conf.html_file and it's dir

    # copy in happy histogram if not there
    html_dir = os.path.dirname(os.path.abspath(conf.html_file))
    hh_css = html_dir + "/HappyDayHistogram.min.css"
    hh_js = html_dir + "/HappyDayHistogram.min.js"
    if not os.path.exists(hh_css):
        read_file = open("html/HappyDayHistogram.min.css", "r").read()
        open(hh_css, "w").write(read_file)

    if not os.path.exists(hh_js):
        read_file = open("html/HappyDayHistogram.min.js", "r").read()
        open(hh_js, "w").write(read_file)

    file = open(conf.html_file, "w")
    html_data += open("html/footer.html", "r").read()
    return file.write(html_data)


def main():
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
