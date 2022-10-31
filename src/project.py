import collections
from re import M
from time import sleep
from json2html import * 
import requests, psycopg2, json
from flask import Flask, render_template, request,redirect,flash,current_app,url_for
import bcrypt
import hashlib


url = "https://solana-gateway.moralis.io/nft/mainnet/{}/metadata"
headers = {
    "accept": "application/json",
    "X-API-Key": "WBgAeLB5DJxduGfcgTMlc4XmW9PVa3kCstYJF1e170NmNIYEbxWYNytr2oxtvd1i"
}



conn = psycopg2.connect(database="nft", user = "postgres", password = "qwerty123", host = "localhost", port = "5432")
cur = conn.cursor()


cur.execute('CREATE TABLE IF NOT EXISTS nft(address TEXT PRIMARY KEY, discription VARCHAR(1000))')
conn.commit()

cur.execute('CREATE TABLE IF NOT EXISTS usr(login VARCHAR(250) PRIMARY KEY, password VARCHAR(250))')
conn.commit()

app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' 
@app.route('/', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        login=request.form.get('login')
        password=request.form.get('password')
    
        cur=conn.cursor()
        error = None

        if not login:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        cur.execute('SELECT login FROM usr WHERE login = (%s);', (login,))
        if cur.fetchone() is not None:
            error = 'User {} is already registered.'.format(login)
        
        if error is None:
            password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')
            cur.execute(
                'INSERT INTO usr (login, password) VALUES (%s, %s);',
                (login, password))
            conn.commit()
            current_app.logger.info("User %s has been created.", login)
            return redirect(url_for('login'))
        current_app.logger.error(error)
        flash(error)
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        login=request.form.get('login')
        password=request.form.get('password')
        cur=conn.cursor()
        error = None

        cur.execute('SELECT password FROM usr WHERE login = (%s);', (login,))
        user = cur.fetchone()
        
        if login is None:
            error = 'Incorrect login.'
        if password is None:
            error = 'Incorrect password.'
        if not user:
            error = 'User not found.'
        
        
        if not bcrypt.checkpw(password.encode('utf8'), user[0].encode('utf8')):
            error = 'Incorrect password.'
        if error is None:
            print("User %s (%s) has logged in.", login)
            return redirect(url_for('search'))
        current_app.logger.error(error)
        flash(error)
    return render_template('login.html')


@app.route('/search', methods=['GET','POST'])
def search():
    if request.method=='POST':
        address=request.form.get('address')
        response=requests.get(url.format(address), headers=headers).json()
        cur=conn.cursor()
        res=str(response)
        db1 = bool(cur.rowcount)
        db2 = False
        if db1:
            cur.execute('SELECT discription FROM nft WHERE address=%s ',(address,))
            db2 = (cur.fetchone() is not None)   
        if db2:
            cur.execute('SELECT discription FROM nft WHERE address=%s ',(address,))
            rows=cur.fetchall
        else:    
            cur.execute('INSERT INTO nft(address, discription) VALUES (%s,%s);',(address,res))
            conn.commit()
        
        
            

        return render_template('output.html', out = response)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)