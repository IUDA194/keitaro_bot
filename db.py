import sqlite3 as sql
import datetime
from texts import USER_404_TEXT
from datetime import timedelta

db = sql.connect('DataBase.db', check_same_thread=False)
with db:
    cur = db.cursor()
    cur.execute("""CREATE TABLE if not exists requests (
        sub_id_10 TEXT,
        sub_id_11 TEXT,
        sub_id_12 TEXT,
        sub_id_13 TEXT,
        sub_id_14 TEXT,
        sub_id_15 TEXT,
        subid TEXT,
        status TEXT,
        revenue TEXT,
        date DATE
        )""")
    cur.execute("""CREATE TABLE if not exists users (
        chat_id TEXT,
        sub_id_10 TEXT
        )""")
    db.commit()
    
    
class database: 
    def create_user(self, chat_id, sub_id_10):
        cur.execute(""" SELECT * FROM users WHERE chat_id = ? """, (chat_id,))
        if len(cur.fetchall()) < 1:
            cur.execute(""" INSERT INTO users ("chat_id", "sub_id_10") VALUES (?,?) """, (chat_id, sub_id_10))
        else: 
            cur.execute(""" UPDATE users SET sub_id_10 = ? WHERE chat_id = ?""", (sub_id_10, chat_id))
        db.commit()
        return {"status" : True}
    
    def select_user(self, chat_id):
        cur.execute(""" SELECT * FROM users WHERE chat_id = ? """, (chat_id,))
        data = cur.fetchall()
        if len(data) >= 1: return {"status" : True, "name" : data[0][1]}
        else: return {"status" : False, "text" : USER_404_TEXT}

    def create_request(self,
                       sub_id_10,
                       sub_id_11,
                       sub_id_12,
                       sub_id_13,
                       sub_id_14,
                       sub_id_15,
                       subid,
                       status,
                       revenue):
        cur.execute(""" SELECT * FROM requests WHERE 
                    sub_id_10 = ? AND
                    sub_id_11 = ? AND
                    sub_id_12 = ? AND
                    sub_id_13 = ? AND
                    sub_id_14 = ? AND
                    sub_id_15 = ? AND
                    subid = ? AND
                    revenue = ?""", 
                       (sub_id_10,
                       sub_id_11,
                       sub_id_12,
                       sub_id_13,
                       sub_id_14,
                       sub_id_15,
                       subid,
                       revenue)
                    )
        if len(cur.fetchall()) < 1:
            cur.execute(""" INSERT INTO requests
                        ("sub_id_10",
                        "sub_id_11",
                        "sub_id_12",
                        "sub_id_13",
                        "sub_id_14",
                        "sub_id_15",
                        "subid",
                        "status",
                        "revenue",
                        "date") VALUES (?,?,?,?,?,?,?,?,?,?) """,
                        (  sub_id_10,
                        sub_id_11,
                        sub_id_12,
                        sub_id_13,
                        sub_id_14,
                        sub_id_15,
                        subid,
                        status,
                        revenue,
                        datetime.datetime.now().strftime('%Y-%m-%d')))
        else: 
            cur.execute(""" UPDATE requests SET status = ? WHERE 
                    sub_id_10 = ? AND
                    sub_id_11 = ? AND
                    sub_id_12 = ? AND
                    sub_id_13 = ? AND
                    sub_id_14 = ? AND
                    sub_id_15 = ? AND
                    subid = ? AND
                    revenue = ? """, (status,
                       sub_id_10,
                       sub_id_11,
                       sub_id_12,
                       sub_id_13,
                       sub_id_14,
                       sub_id_15,
                       subid,
                       revenue))
        db.commit()
        return {"status" : True}
    
    def select_request(self, sub_id_10 : str, time_delta : int):
        if sub_id_10 and time_delta:

            results_col = 0
            revenue_temp = []    
            revenue = 0    
            statuses = []    

            cur.execute("""
                SELECT *
                FROM requests
                WHERE date BETWEEN ? AND ? AND sub_id_10 = ? 
            """, ((datetime.datetime.now() - timedelta(days=time_delta)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d'), sub_id_10))
            results = cur.fetchall()
            results_col = len(results)
            for result in results:
                statuses.append(result[7])
                if result[7] == "approve":
                    try: revenue_temp.append(float(result[8]))
                    except TypeError: pass
                    except: pass
            revenue = sum(revenue_temp)
            return {"status" : True,
                    "data" : {"revenue" :int(round(revenue)),
                              "statuses" : statuses,
                              "results_col" : results_col},
                    "text" : f"""Пользователь: {sub_id_10}
Период: {time_delta}
Конверсии: {results_col}
Треш: {statuses.count("trash")}
Холд: {statuses.count("waiting")}
Апрув: {statuses.count("approve")}
Баланс: {revenue} """}
        else:
            return {"status" : "Error", "text" : "Простите что-то пошло не так, попробуйте попытку позже"}


print(database().select_request("test_value", 1))