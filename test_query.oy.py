import sqlite3

movie = "fight club"
conn = sqlite3.connect('instance/users.db')
cursor = conn.cursor()
query = f'''
SELECT *
  FROM Movies  
 WHERE instr(crew, 'Brad Pitt') > 0;'''
cursor.execute(query)
results = cursor.fetchall()
print(results)
list1 = []
for result in results:
    data = {
        "title": result[0],
        "release-date": result[1],
        "rating": result[2],
        "genre": result[3],
        "description": result[4],
        "cast-crew": result[5]
    }
    list1.append(data)

print(list1)

conn.close()