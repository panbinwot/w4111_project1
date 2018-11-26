import os
from flask import Flask, flash, redirect, render_template, g,request, session, abort, Response,url_for
from sqlalchemy import *
from sqlalchemy.pool import NullPool

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "dx2183"
DB_PASSWORD = "u3s190s7"

#DB_USER = "bp2551"
#DB_PASSWORD = "aiucq0il"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
print DATABASEURI
engine = create_engine(DATABASEURI)

# engine.execute("""ALTER TABLE test add oorder int;""")
  # engine.execute("""INSERT INTO dxuser VALUES (10012,'x',3,'x@bandb.com','','xx','0');""")
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#     uid int not NULL,
#     sell_id text not NULL,
#     item_id text not null,
#     c_id text not NULL,
#     price text not null,
#     stime date not null,
#     oorder int not null,
#     PRIMARY KEY (oorder) 
#     );""")
# engine.execute("""
# INSERT INTO test VALUES (10001,10002,107,101,100,'2018-11-26',1);
# INSERT INTO test VALUES (10002,10003,108,102,100,'2018-11-26',2);
# INSERT INTO test VALUES (10003,10002,111,103,100,'2018-11-26',3);
# INSERT INTO test VALUES (10004,10002,117,104,100,'2018-11-26',4);
# INSERT INTO test VALUES (10005,10002,109,105,100,'2018-11-26',5);
# INSERT INTO test VALUES (10006,10002,108,106,100,'2018-11-26',6);
# INSERT INTO test VALUES (10007,10002,112,107,100,'2018-11-26',7);
# INSERT INTO test VALUES (10008,10002,114,108,100,'2018-11-26',8);
# INSERT INTO test VALUES (10009,10002,115,109,100,'2018-11-26',9);
# INSERT INTO test VALUES (10010,10002,107,110,100,'2018-11-26',10);
#   """)
