from application import app
from flask import render_template, request, jsonify, session, flash
from chat import *
from flask import Flask, render_template, request, Response, redirect, url_for
from flask_bootstrap import Bootstrap
import time
import cv2
import numpy as np
import os
from flask_mysqldb import MySQL
from flask import Flask,render_template,request,redirect,session,flash,url_for
from functools import wraps



from application.object_detection import *
from application.camera_settings import *


app.secret_key='many random bytes'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_sample'
app.config['MYSQL_CURSORCLASS']='DictCursor'

Bootstrap(app)
mysql=MySQL(app)


@app.route('/') 
@app.route('/login',methods=['POST','GET'])
def login():
    status=True
    if request.method=='POST':
        email=request.form["email"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("select * from users where email=%s and password=%s",(email,pwd))
        data=cur.fetchone()
        if data:
            session['logged_in']=True
            session['username']=data["username"]
            return redirect('index')
        else:
            flash('Invalid Login. Try Again','danger')
    return render_template("login.html")

def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/reg',methods=['POST','GET'])
def reg():
    status=False
    if request.method=='POST':
        name=request.form["username"]
        email=request.form["email"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("insert into users(username,email,password) values(%s,%s,%s)",(name,email,pwd))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...','success')
        return redirect(url_for('login'))
    return render_template("register.html",status=status)

@app.route('/index')
@is_logged_in
def index():
    return render_template('index.html')

@app.route("/logout")
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))

@app.route('/opencam')
def opencam():
    TITLE = 'Object detection'
    return render_template('opencam.html', TITLE=TITLE)

@app.post('/predict')
def predict():
    text =  request.get_json().get('message')
    # TODO: check if text is valid
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)



@app.route('/data')
def db():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM trash")
    data = cur.fetchall()
    cur.close()




    return render_template('index2.html', trash=data )




@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        lok = request.form['lok']
        ket = request.form['ket']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO trash (name, lok, ket) VALUES (%s, %s, %s)", (name, lok, ket))
        mysql.connection.commit()
        return redirect(url_for('db'))




@app.route('/delete/<string:id>', methods = ['GET'])
def delete(id):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM trash WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('db'))





@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        lok = request.form['lok']
        ket = request.form['ket']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE trash
               SET name=%s, lok=%s, ket=%s
               WHERE id=%s
            """, (name, lok, ket, id))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('db'))



check_settings()
VIDEO = VideoStreaming()

@app.route('/video_feed')
def video_feed():
    '''
    Video streaming route.
    '''
    return Response(
        VIDEO.show(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# Button requests called from ajax
@app.route('/request_preview_switch')
def request_preview_switch():
    VIDEO.preview = not VIDEO.preview
    print('*'*10, VIDEO.preview)
    return "nothing"

@app.route('/request_flipH_switch')
def request_flipH_switch():
    VIDEO.flipH = not VIDEO.flipH
    print('*'*10, VIDEO.flipH)
    return "nothing"

@app.route('/request_model_switch')
def request_model_switch():
    VIDEO.detect = not VIDEO.detect
    print('*'*10, VIDEO.detect)
    return "nothing"

@app.route('/request_exposure_down')
def request_exposure_down():
    VIDEO.exposure -= 1
    print('*'*10, VIDEO.exposure)
    return "nothing"

@app.route('/request_exposure_up')
def request_exposure_up():
    VIDEO.exposure += 1
    print('*'*10, VIDEO.exposure)
    return "nothing"

@app.route('/request_contrast_down')
def request_contrast_down():
    VIDEO.contrast -= 4
    print('*'*10, VIDEO.contrast)
    return "nothing"

@app.route('/request_contrast_up')
def request_contrast_up():
    VIDEO.contrast += 4
    print('*'*10, VIDEO.contrast)
    return "nothing"

@app.route('/reset_camera')
def reset_camera():
    STATUS = reset_settings()
    print('*'*10, STATUS)
    return "nothing"



if __name__ == "__main__":
    app.run(debug=True)