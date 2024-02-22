from flask import Flask,redirect,render_template,url_for,request,flash,session
from flask_mysqldb import MySQL
import requests

app=Flask(__name__)
app.secret_key='maha@27'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='nilavu@9894662122'
app.config['MYSQL_DB']='mutual_fund'
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)

def is_loggedin():
    return 'username' in session

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        cur=mysql.connection.cursor()
        cur.execute("select * from signup where username=%s",(username,))
        data=cur.fetchone()
        mysql.connection.commit()
        cur.close()

        if data:
            return 'Username is already exists..!'
        else:
            cur=mysql.connection.cursor()
            cur.execute('insert into signup (username,password) values (%s,%s)',(username,password))
            mysql.connection.commit()
            cur.close()                                                                             
            
        return redirect(url_for('login'))
    return render_template('signup.html')

    

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        cur=mysql.connection.cursor()
        cur.execute('select * from signup where username=%s',(username,))
        data=cur.fetchone()
        mysql.connection.commit()
        cur.close()

        if data:
            session['username']=username
            return redirect(url_for('home'))
        else:
            return 'Invalid Username or Password'
        
    return render_template('login.html')


@app.route('/home',methods=['GET','POST'])
def home():
    if is_loggedin():
        username=session['username']
        
        cur=mysql.connection.cursor()
        cur.execute('select * from fund_details where Name=%s',(username,))
        data=cur.fetchall()
        mysql.connection.commit()
        cur.close()
    return render_template('home.html',data=data)


mutualURL="https://api.mfapi.in/mf/"

@app.route('/addUser',methods=['GET','POST'])
def addUser():
    if request.method== 'POST':
        
        name= request.form.get("name")
        invested_amount= request.form.get("invested_amount")
        units_held=request.form.get("units_held")
        fund_code= request.form.get("fund_code")

        data= requests.get(mutualURL+str(fund_code))
        fund_house= data.json().get("meta")["fund_house"]
        nav= data.json().get("data")[0].get("nav")
        currentValue= float(nav) * int(units_held)
        growth= float(currentValue) - int(invested_amount)

        cur=mysql.connection.cursor()
        cur.execute("insert into fund_details (Name,Fund_code,Invested_amount,Units_held,Fund_house,Nav,Current_value,Growth) values (%s,%s,%s,%s,%s,%s,%s,%s)",(name,fund_code,invested_amount,units_held,fund_house,nav,currentValue,growth))
        mysql.connection.commit()
        cur.close()

        flash("Created Successfully...!")

        return redirect(url_for('home'))
    return render_template('addUser.html')

@app.route('/editUser/<string:Id>',methods=['GET','POST'])
def editUser(Id):
    if request.method== 'POST':
        
        name= request.form.get("name")
        invested_amount= request.form.get("invested_amount")
        units_held=request.form.get("units_held")
        fund_code= request.form.get("fund_code")
        data= requests.get(mutualURL+str(fund_code))
        fund_house= data.json().get("meta")["fund_house"]
        nav= data.json().get("data")[0].get("nav")
        currentValue= float(nav) * int(units_held)
        growth= float(currentValue) - int(invested_amount)

        cur=mysql.connection.cursor()
        cur.execute("update fund_details set Name=%s,Fund_code=%s,Invested_amount=%s,Units_held=%s,Fund_house=%s,Nav=%s,Current_value=%s,Growth=%s where Id=%s",(name,fund_code,invested_amount,units_held,fund_house,nav,currentValue,growth,Id))
        mysql.connection.commit()
        cur.close()

        flash("Updated Successfully...!")
        return redirect(url_for('home'))
    
    cur=mysql.connection.cursor()
    cur.execute('select * from fund_details where Id=%s',(Id,))
    data=cur.fetchone()
    mysql.connection.commit()
    cur.close()

    return render_template('editUser.html',data=data)

@app.route('/deleteUser/<int:Id>',methods=['GET','POST'])
def deleteUser(Id):

    cur = mysql.connection.cursor()
    cur.execute("delete from fund_details where Id=%s", (Id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('home'))

@app.route('/')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True,port=5001)