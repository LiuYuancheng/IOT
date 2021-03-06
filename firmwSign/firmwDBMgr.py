#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        firmwDBMgr.py
#
# Purpose:     firmware Sign dataBase manager. 
# Author:      Yuancheng Liu
#
# Created:     2019/05/08
# Copyright:   NUS – Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import os
import hashlib
import sqlite3
from sqlite3 import Error
from Constants import RAN_LEN
import firmwGlobal as gv
DE_USER = ("admin", os.urandom(RAN_LEN).hex(), '123')   # defualt user.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class firmwDBMgr(object):
    """ Firmware sign system dataBase manager. """
    def __init__(self):
        """ Check whether the data base has been created and connect to database.
            (create the DB+table if needed.)
        """
        self.sql_firwareInfo_table = None
        self.sql_user_table = None
        if not os.path.exists(gv.DB_PATH):
            print("DBmgr: Data base file is missing, create new data base file")
            # Table to save the firmware sign data.
            self.sql_firwareInfo_table = """CREATE TABLE IF NOT EXISTS firmwareInfo (
                                id integer PRIMARY KEY,
                                sensorID integer NOT NULL,
                                signerID integer NOT NULL,
                                challenge text NOT NULL,
                                swatt text NOT NULL,
                                date text NOT NULL,
                                type text,
                                version text NOT NULL,
                                certPath text NOT NULL,
                                signatureClient text NOT NULL,
                                signatureServer text NOT NULL
                            );"""
            # Table to save the user name and password.
            self.sql_user_table = """ CREATE TABLE IF NOT EXISTS userInFo(
                                user text PRIMARY KEY,
                                salt text NOT NULL,
                                pwdHash text NOT NULL
                            );"""
        # Connect to database.
        self.conn = self.createConnection(gv.DB_PATH)
        # create the table if the BD is first time created one.
        if self.sql_firwareInfo_table and self.conn:
            self.createTable(self.sql_firwareInfo_table)
            self.createTable(self.sql_user_table)
            # Add default user if create the new database.
            self.addUser(DE_USER)
        # Test whether the user is in database.
        self.addUser(('123', os.urandom(RAN_LEN).hex(), '123'))
        print(self.authorizeUser('123', '123'))

#--firmwDBMgr------------------------------------------------------------------
    def addUser(self, args):
        """ Add a new user and its password in the DB. """
        if len(args) != 3:
            print("DBmgr: User register parameters missing <%s>" %str(args))
            return False
        user, salt, pwd = args
        pwdhash = hashlib.sha256(bytes.fromhex(salt) + str(pwd).encode('utf-8')).hexdigest()
        # Check wether user in the DB already:
        selectSQL = '''SELECT * FROM userInFo WHERE user=?'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(selectSQL, (str(user),))
            rows = cur.fetchall()
            if len(rows):
                print("DBmgr: The user <%s> is in database." % str(user))
                return False
        print("DBmgr: Add user <%s> into the data base." % str(user))
        insertSQL = ''' INSERT INTO userInFo(user, salt, pwdHash)
                VALUES(?,?,?) '''
        with self.conn: # use 'with' will do the auto-commit to database.
            cur = self.conn.cursor()
            cur.execute(insertSQL, (str(user), salt, str(pwdhash)))
        return True

#--firmwDBMgr------------------------------------------------------------------
    def authorizeUser(self, user, pwd):
        """ Authorize user and its password. """
        # Check wether user in the DB already:
        selectSQL = '''SELECT * FROM userInFo WHERE user=?'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(selectSQL, (str(user),))
            rows = cur.fetchall()
            if len(rows):
                _, salt, pwdhash = rows[0] # user ID is unique in the database.
                if pwdhash == hashlib.sha256(bytes.fromhex(salt) + str(pwd).encode('utf-8')).hexdigest():
                    return True
        return False

#--firmwDBMgr------------------------------------------------------------------
    def authorizeSensor(self, args):
        """ Authorize whether a sensor has been registered."""
        if len(args) != 5:
            print("DBmgr: Sensor register parameter missing %s" %str(args))
            return False
        signature ,seId, seType, seFwVersion, time = args
        selectSQL = '''SELECT * FROM firmwareInfo WHERE signatureServer=?'''
        conn = sqlite3.connect(gv.DB_PATH, check_same_thread=False)
        # Create a new connection as this function is called by the sub-thread. 
        # To avoid the error: "ProgrammingError: SQLite objects created in 
        # a thread can only be used in that same thread"  
        with conn:
            cur = conn.cursor()
            cur.execute(selectSQL, (signature,))
            rows = cur.fetchall()
            if len(rows):
                print("DBmgr: find the sensor signature")
                for row in rows: 
                    if seId == row[1] and seType == row[6] and str(seFwVersion) == row[7]:
                        return True
                    else:
                        return False
        return False

#--firmwDBMgr------------------------------------------------------------------
    def checkUser(self, userName):
        """ Check whehter the user is in the data base. """
        selectSQL = '''SELECT * FROM userInFo WHERE user=?'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(selectSQL, (str(userName),))
            rows = cur.fetchall()
            if len(rows):
                print("DBmgr: The user %s is exists" % str(userName))
                return True
        return False

#--firmwDBMgr------------------------------------------------------------------
    def createTable(self, create_table_sql):
        """ Create a table base on the input sql requst."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(create_table_sql)
        except Error as e:
            print(e)

#--firmwDBMgr------------------------------------------------------------------
    def createConnection(self, db_file):
        """ Create a database connection to a SQLite database """
        try:
            return sqlite3.connect(db_file)
        except Error as e:
            print(e)
            return None

#--firmwDBMgr------------------------------------------------------------------
    def createFmSignRcd(self, rcdArgs):
        """ Create a firmware sign record in the data base."""
        if len(rcdArgs) != 10: 
            print("DBmgr: The firmware sign inforamtion <%s> element missing." %str(rcdArgs))
            return None
        # Insert sql request.
        sql = ''' INSERT INTO firmwareInfo( sensorID, signerID,challenge, swatt, date, type, version, certPath, signatureClient, signatureServer)
                VALUES(?,?,?,?,?,?,?,?,?,?) '''
        #rcdArgs = ( 203, 'default challenge', '0x1245', '2015-01-01', 'XKAK_PPL_COUNT', '1.01')
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, rcdArgs)
            print("DBmgr: This is the cursir UD: <%s>" %str(cur.lastrowid))
            return cur.lastrowid
   
#--firmwDBMgr------------------------------------------------------------------
    def updateRecd(self,rcd):
        """ Udate the firware sign recode(currently not used)"""
        sql = ''' UPDATE firmwareInfo
                SET sensorID = ? ,
                    challenge = ? ,
                    swatt = ?
                WHERE id = ?'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, rcd)

#def testCase():
#    if conn is not None: 
#         createTable(conn, sql_firwareInfo_table)
#    
#    with conn:
#        signRecord = ( 203, 'default challenge', '0x1245', '2015-01-01', 'XKAK_PPL_COUNT', '1.01')
#        signIdx = createFmSignRcd(conn, signRecord)
#        print("this is signIdx"+str(signIdx))
#        #changedRcd = ()
#        updateRecd(conn, (202, 'change challenge', '0X234',1))
    #else:
    #    print("Error! Can not create the database connection.")
    
if __name__ == '__main__':
    pass
    #testCase()
