import sqlite3

def tk_recorder(msg):
    # Add a new tk record
    if msg[:3] == "tk ":
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        split = msg.split("@")
        try:
            killer = split[1].strip()
            victim = split[2].strip()
        except IndexError:
            return
        date = date.today().strftime("%d/%m/%Y")
        c.execute("INSERT INTO tk_record (killer, victim, date) VALUES (?, ?, ?)", (killer, victim, date))
        conn.commit()
        c.close()

    # tk leaderboard
    elif msg == "tk-leaderboard":
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record GROUP BY killer")
        result = c.fetchall()
        c.close()

        print("TK Leaderboard")
        for str in result:
            print(str[0], str[1])

    # un-targeted tk query
    elif "tk-record" in msg and len(msg.split("@")) == 2:
        killer = msg.split("@")[1].strip()
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record WHERE killer == $", (killer,))
        result = c.fetchall()
        c.close()

        if result[0][1] == 0:
            print(f"{killer} has never teamkilled \n\nprobably")
        elif result[0][1] == 1:
            print(f"{killer} has teamkilled 1 time")
        else:
            print(f"{killer} has teamkilled {result[0][1]} times")

    # targeted tk query
    elif "tk-record" in msg and len(msg.split("@")) == 3:
        killer = msg.split("@")[1].strip()
        victim = msg.split("@")[2].strip()
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record WHERE killer == $ AND victim == $", (killer, victim))
        result = c.fetchall()
        c.close()

        if result[0][1] == 0:
            print(f"{killer} has never teamkilled {victim} \n\nprobably")
        elif result[0][1] == 1:
            print(f"{killer} has teamkilled {victim} 1 time")
        else:
            print(f"{killer} has teamkilled {victim} {result[0][1]} times")


tk_recorder("tk-leaderboard")
