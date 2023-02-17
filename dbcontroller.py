from contextlib import closing
import os
import sqlite3

class Constants:
    DB_ERROR_MSG = "Unable to connect to Database. Please Database file path!!"
    DB_EMPTY_MSG = "Database name cannot be empty. Please provide db name"

class DBController:

    def __init__(self,database:str="") -> None:
        if (database == ""): raise RuntimeError(Constants.DB_EMPTY_MSG)
        if not os.path.exists(database): raise RuntimeError(Constants.DB_ERROR_MSG) 
        self.database = database

    def executeQuery(self,query:str=""):
        if(query==""): return None
        with closing(sqlite3.connect(database=self.database,check_same_thread=False)) as con:
            con.row_factory = sqlite3.Row
            with closing(con.cursor()) as cursor:
                rows = cursor.execute(query).fetchall()
                con.commit()
                return rows

    def executeQueryWithParams(self,query:str="",params=[]):
        if(query=="" or len(params)==0): return None
        with closing(sqlite3.connect(database=self.database,check_same_thread=False)) as con:
            con.row_factory = sqlite3.Row
            with closing(con.cursor()) as cursor:
                rows = cursor.execute(query,params).fetchall()
                con.commit()
                return rows

    def insert(self,table:str="",data = {}):
        if(table=="" or len(data)==0): return False
        columns = ", ".join(data.keys())
        placeholders = ":"+", :".join(data.keys())
        query = "INSERT INTO %s (%s) VALUES (%s)" % (table,columns,placeholders)
        print("==== ==== ==== DBCONTROLLER: INSERT QUERY ==== ==== ====")
        print(query)
        print(tuple(data.values()))
        print("==== ==== ==== ==== ==== ==== ==== ==== ")
        with closing(sqlite3.connect(database=self.database,check_same_thread=False)) as con:
            with closing(con.cursor()) as cursor:
                cursor.execute(query,data)
                con.commit()
                return True 