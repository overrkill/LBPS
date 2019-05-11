from flask import Flask, flash, render_template,request, redirect, url_for
from pyduino import *
import datetime as dt
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.sql import exists
from werkzeug.security import generate_password_hash,check_password_hash
#from flask_login import LoginManager,login_required,login_user,logout_user
import time as t
state=[0,1,2,3]
state[1]=0
state[2]=0
state[3]=0
#count=0
slot=0
app = Flask(__name__)
app.secret_key="secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parker.sqlite3'
a=Arduino()
db = SQLAlchemy(app)
class parker(db.Model):
    
   id = db.Column('slot_no', db.Integer, primary_key = True)
   parked_at = db.Column(db.DateTime)
   parked_till= db.Column(db.DateTime)
   status = db.Column(db.Boolean) 
   owner=db.Column(db.Integer,db.ForeignKey('user.id'))

   def __init__(self, slot_no, appr_time,status):
    self.slot_no=slot_no
    self.appr_time=appr_time
    self.status=status
  

class user(db.Model):
    u_id=db.Column('id',db.Integer,primary_key=True,autoincrement=True)
    name=db.Column('name',db.String(20))
    username=db.Column('uname',db.String(40),unique=True)
    password=db.Column('pass',db.String(200))
    slot=db.relationship('parker',backref='onr')

    def __init__(self,name,username,password):
        
        self.name=name
        self.username=username
        self.password=password


t.sleep(3)
def check():
    count=0
    for i in range(0,2):
        state[i]=a.analog_read(i)
        print state[i]
        if state[i]>50:
            count=1

        else:
            pass
    return count
def giv():
    min=0
    for i in range(0,3):
        
        if state[i+1]!=0 and state[i+1]>=state[i]:
            min=i+1
    print min+1
    return min+1



@app.route('/', methods=['POST','GET'])
def index():
    author="group 2"
    
    if request.method == 'POST':
        if request.form['submit']=='signin':
            username = request.form['username']
            temp=user.query.filter_by(username=username).first()
            if temp is None:
                password=False
            else:    
                password = check_password_hash(temp.password,request.form['pass'])

            print password
            
            if  password==False  :
                return render_template('invalid.html')
            else:
                return render_template('index.html',author=author)
        elif request.form['submit']=='signup':
            return render_template('signup.html')
        elif request.form['submit']=='signon':
            exist=db.session.query(
    db.session.query(user).filter_by(username=request.form['username']).exists()
).scalar()
            if not request.form['name'] or not request.form['username'] or not request.form['pass']:
                
                return render_template('afk.html')
            elif exist:
                return render_template('user_exists.html')
            else:
                user1=user(name=request.form['name'],username=request.form['username'],password=generate_password_hash(request.form['pass']))
                db.session.add(user1)
                db.session.commit()
                return render_template('index.html')
                
    
    return render_template('main_page.html')

@app.route('/checker')

def checker():
    if check()>0:
        return render_template('time_page.html')
    else:
        return render_template('error.html')

@app.route('/time_page',methods=['POST','GET'])

def time_page():
    if request.method == 'POST':
        if request.form['submit']=='park':
            temp=request.form['ptime']

            return redirect(url_for('alloc'))

@app.route('/allocate')

def alloc():

    slot=giv()
    return render_template('allocate.html',slot=slot)


if __name__ == "__main__":
    # lets launch our webpage!
    # do 0.0.0.0 so that we can log into thi    s webpage
    # using another computer on the same network later
    db.create_all() 
    app.run(debug=True,host='0.0.0.0')