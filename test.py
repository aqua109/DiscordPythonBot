import sqlite3

conn = sqlite3.connect("tk.db")
c = conn.cursor()
c.execute("SELECT killer, COUNT(killer) FROM tk_record GROUP BY killer")
result = c.fetchall()
conn.close()

for str in result:
    print(str[0], str[1])
