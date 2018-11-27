
import os
from flask import Flask, flash, redirect, render_template, g,request, session, abort, Response,url_for
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import time 
import random
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

  #Create a table to store comments 
  # to do

# Setup with flask-login extension
import flask_login

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# flask_login.current_user
class User(flask_login.UserMixin):
  pass 

@login_manager.user_loader
def user_loader(username):
    # check if the username existed in db
    user = User()
    user.id = username
    return user

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def home():
    # if not session.get('logged_in'):
    #     return render_template('mainpage.html')
    # else:
    return render_template('login.html', message=" there! Help yourself !")
 
@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
      message = "Please login or register"
      username = request.form['username']
      password = request.form['password']

      cursor = g.conn.execute("SELECT uid,password FROM dxuser WHERE uid=%s AND password=%s", (username, password))
      row = cursor.fetchone()
      if row:
        user = User()
        user.id = username
        flask_login.login_user(user)
        print "Successfully login"
        return redirect(url_for('mainpage'))
      else:
        message = 'Invalid username or password. Please try again!'
        return render_template('login.html', message=message)
  else:
    if request.args.get("next"):
      return render_template("login.html", error = login_manager.login_message, next = request.args.get("next"))
    else:
      return render_template("login.html")

@app.route('/register', methods= ['GET', 'POST'])
def register():
  num = g.conn.execute("SELECT max(uid) as max from dxuser")
  for res in num:
    uid = res['max']
  uid = int(uid)+1
  num.close()
  if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      address = request.form['address']
      phone = int(request.form['phone'])      
      company = request.form['company']
      name = request.form['name']
      info = (uid,address,phone,email,company,name,password)
      try:
        # INSERT INTO test VALUES (10001,'0','3W 109th NY 10027',9173286666,'13717881379@126.com','','Da Xiong');
        g.conn.execute("INSERT INTO dxuser VALUES (%s, %s, %s, %s, %s, %s, %s)", info)
        good = str(uid)+' '+name+' ! '+'Successfully register. Welcome and Please login with ur ID!'    
        return render_template('login.html', message = good)
      except Exception as e:
        print e
        message = str(info)+' '+'Email existed. Please try another one!'
        return render_template('login.html', message = message)
        error = 'Username existed. Please try another one!'
  else:
    return render_template('login.html', message = 'enjoy')

#mainpage is the page where i list all the products
@app.route('/mainpage',methods=['GET','POST'])
@flask_login.login_required
def mainpage():
    cursor = g.conn.execute("SELECT item_id, model_name FROM graphiccard;")
    cards = {}
    for res in cursor:
        cards[res['item_id']] = res['model_name']
    cursor.close()

    context = dict(data = cards)
    return render_template("mainpage.html", **context)

@app.route('/details',methods=['POST','GET'])
@flask_login.login_required
def details():                                       
    iid = request.args.get('item_id')
    cursor = g.conn.execute("""SELECT * 
                              FROM graphiccard as g natural join oem as o
                              WHERE item_id=%s ;""" ,iid)
    detail = {}
    detail['item_id'] = iid

    for res in cursor:
        detail['model_name'] = res['model_name']
        detail['memory'] = res['memory']
        detail['clock_freq'] = res['clock_freq']
        detail['tdp'] = res['tdp']
        detail['Owner'] = res['uid'] 
        detail['Price'] = res['price']
        detail['OEM'] = res['o_name']
    cursor.close()
    context = dict(data=detail)
    return render_template("details.html",**context)

# @app.route('/another',methods=['POST','GET'])
# @flask_login.login_required
# def another():
#   return render_template("details.html")

@app.route('/logout',methods=['POST','GET']) 
@flask_login.login_required
def logout():
  flask_login.logout_user()
  return render_template("login.html")

@app.route('/buy',methods=['POST','GET'])
@flask_login.login_required
def buy():
  info={}
  uid = request.args.get('uid')  
  # asign order number
  cursor = g.conn.execute("SELECT max(oorder) as max from test")
  for res in cursor:
    oorder = res['max']
  cursor.close()  
  od = int(oorder)+1
  info['order']=od
  # asign carrier
  carr = random.randint(101,110)
  car = g.conn.execute("SELECT c_name from carrier where c_id=%s",carr)
  for res in car:
      info['carrier'] = res['c_name']
  car.close()
  
  iid = request.args.get('iid')
 
  cursor = g.conn.execute("""SELECT * from graphiccard where item_id=%s;""",iid)
  for res in cursor:
    info['price'] = res['price']
    info['sell_id'] = res['uid']
  cursor.close()
  info['item_id']=iid
  info['t'] = time.strftime("%Y-%m-%d", time.localtime())
  info['cid'] = carr

  return render_template("buy.html",info=info)

@app.route('/search',methods=['POST','GET'])
@flask_login.login_required
def search():
  info={}
  text = request.form['search']
  pattern1 = '%'+text+'%'
  pattern2 = '%'+text
  pattern3 = text+'%'
  pattern = (text,pattern1,pattern2,pattern3)
  cursor = g.conn.execute("""SELECT * 
                            from graphiccard, oem 
                            where model_name like %s or model_name like %s 
                            or model_name like %s or model_name like %s  ;""",pattern)
  for res in cursor:
    info[res['item_id']] = res['model_name']
  cursor.close()
  if info:
    x = True
  else:
    x = False
  return render_template("search.html", data = info, x=x)

@app.route('/user',methods=['POST','GET'])
@flask_login.login_required
def user():
  uid = request.args.get('uid')
  cursor = g.conn.execute("""SELECT * 
                            FROM dxuser
                            WHERE uid=%s ;""" ,uid)
  userinfo={}  
  userinfo['uid'] = uid  
  for res in cursor:
    userinfo['phone']=res['u_phone']
    userinfo['email']=res['u_email']
    userinfo['address'] = res['address']
    userinfo['company'] =  res['company_name']
    userinfo['name'] = res['indv_name']
  cursor.close()

  cards = {}
  cc = g.conn.execute("""SELECT * FROM test,carrier where uid=%s;""",uid)
  for res in cc:
    cards[res['item_id']] = (res['sell_id'],res['stime'],res['c_name'])
  cc.close()

  cards2 = {}
  cc = g.conn.execute("""SELECT * FROM graphiccard where uid=%s;""", uid)
  for res in cc:
    cards2[res['item_id']] = (res['uid'],res['s_time'])
  cc.close()

  return render_template('user.html', data = userinfo, cards = cards, cards2=cards2)

@app.route('/post',methods=['POST','GET'])
@flask_login.login_required
def post():
  num = g.conn.execute("SELECT max(item_id) as max from graphiccard")
  for res in num:
    item_id = res['max']
  item_id = int(item_id)+1
  num.close()  
  modelname = request.form['modelname']
  memory = request.form['memory'] + 'GB'
  tdp = request.form['tdp']
  clock_freq = request.form['clock_freq']
  oem = request.form['OEM']
  oid = 101
  price = request.form['price']
  uid = flask_login.current_user.id
  t = time.strftime("%Y-%m-%d", time.localtime())
  info = (modelname,item_id,memory,clock_freq,tdp,uid,t,price,oid)
  g.conn.execute("""insert into graphiccard VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",info)

  return redirect(url_for('mainpage'))

@app.route('/confirm',methods=['POST','GET'])
@flask_login.login_required
def confirm():
  uid = request.args.get('uid')
  item_id = request.args.get('iid')
  t = time.strftime("%Y-%m-%d", time.localtime())
  sid = request.args.get('sell_id')
  cid = request.args.get('c_id')
  price = request.args.get('price')
  oorder= request.args.get('order')
  data = (uid,sid,item_id,cid,price,t,oorder)
  g.conn.execute("""INSERT into test VALUES (%s, %s, %s, %s, %s, %s,%s) ;""",data)
  return redirect(url_for('mainpage'))

@app.route('/contact',methods=['POST','GET'])
@flask_login.login_required
def contact():
  cursor = g.conn.execute("""select sid from service""")
  ss=[]
  for res in cursor:
    ss.append(res['sid'])
  cursor.close()
  sid = ss[random.randint(1,10)]

  uid = flask_login.current_user.id
  t = time.strftime("%Y-%m-%d", time.localtime())
  iid = request.form['itemid']
  details = request.form['details']
  data = (uid,sid,t,details)
  g.conn.execute("""insert into ucontactservice VALUES (%s,%s,%s,%s);""",data)
  return redirect(url_for('mainpage'))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)