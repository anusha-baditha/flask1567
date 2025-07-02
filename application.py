from flask import Flask,request,render_template,redirect,url_for,flash,session,Response
import mysql.connector
from otp import genotp
from cmail import send_mail
from  flask_session import Session
import bcrypt
from stoken import entoken,dtoken
import os
import razorpay
import pdfkit
import re
client = razorpay.Client(auth=("rzp_test_IW39YgU8i2HhFs", "gtE4ty01rVjtxpu9BbTdgNrR"))
application=Flask(__name__)
#config=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
application.config['SESSION_TYPE']='filesystem'
Session(application)
application.secret_key='codegnan@2025'
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
port=os.environ.get('RDS_PORT')
host=os.environ.get('RDS_HOSTNAME')
with mysql.connector.connect(user=user,port=port,db=db,password=password,host=host) as conn:
    cursor=conn.cursor()
    cursor.execute("CREATE TABLE if not exists admin_details (admin_username varchar(30) NOT NULL,admin_email varchar(50) NOT NULL,admin_password varbinary(255) DEFAULT NULL,created_at datetime DEFAULT CURRENT_TIMESTAMP,address text,PRIMARY KEY (admin_email),UNIQUE KEY admin_email (admin_email))")
    cursor.execute("CREATE TABLE if not exists items (itemid binary(16) NOT NULL,item_name mediumtext NOT NULL,description longtext NOT NULL,item_cost decimal(20,4) NOT NULL,item_quantity mediumint unsigned DEFAULT NULL,item_category enum('Home applicationliances','Electronics','Sports','Fashion','Grocery') DEFAULT NULL,added_by varchar(50) DEFAULT NULL,created_at datetime DEFAULT CURRENT_TIMESTAMP,imgname varchar(20) DEFAULT NULL,PRIMARY KEY (itemid),KEY items_addedby (added_by),CONSTRAINT items_addedby FOREIGN KEY (added_by) REFERENCES admin_details (admin_email))")
    cursor.execute("CREATE TABLE if not exists users (useremail varchar(30) NOT NULL,username varchar(30) NOT NULL,password varbinary(255) DEFAULT NULL,address text NOT NULL,created_at datetime DEFAULT CURRENT_TIMESTAMP,gender enum('Male','Female','Other') DEFAULT NULL,PRIMARY KEY (useremail))")
    cursor.execute("CREATE TABLE if not exists orders (order_id int unsigned NOT NULL AUTO_INCREMENT,order_date datetime DEFAULT CURRENT_TIMESTAMP,item_id binary(16) NOT NULL,item_name varchar(255) NOT NULL,total decimal(10,2) DEFAULT NULL,payment_by varchar(30) DEFAULT NULL,PRIMARY KEY (order_id),KEY payment_by (payment_by),KEY item_id (item_id),CONSTRAINT orders_ibfk_1 FOREIGN KEY (payment_by) REFERENCES users (useremail) ON DELETE SET NULL ON UPDATE CASCADE,CONSTRAINT orders_ibfk_2 FOREIGN KEY (item_id) REFERENCES items(itemid) ON UPDATE CASCADE)")
    cursor.execute("CREATE TABLE if not exists reviews (r_id int unsigned NOT NULL AUTO_INCREMENT,review_text text,create_at datetime DEFAULT CURRENT_TIMESTAMP,itemid binary(16) DEFAULT NULL,added_by varchar(30) DEFAULT NULL,rating enum('1','2','3','4','5') DEFAULT NULL,PRIMARY KEY (r_id),KEY itemis (itemid),KEY added_by (added_by),CONSTRAINT reviews_ibfk_1 FOREIGN KEY (itemid) REFERENCES items (itemid) ON DELETE SET NULL ON UPDATE CASCADE,CONSTRAINT reviews_ibfk_2 FOREIGN KEY (added_by) REFERENCES users (useremail) ON DELETE SET NULL ON UPDATE CASCADE)")
mydb=mysql.connector.connect(user=user,host=host,password=password,db=db,port=port)
@application.route('/')
def home():
    return render_template('welcome.html')
@application.route('/index')
def index():
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,created_at,imgname from items')
        items_data=cursor.fetchall()
    except Exception as e:
        print(f'Error is :{e}')
        flash('Could not fetch the items')
        return redirect(url_for('index'))
    else:
        return render_template('index.html',items_data=items_data)
@application.route('/category/<ctype>')
def category(ctype):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,created_at,imgname from items where item_category=%s',[ctype])
        items_data=cursor.fetchall()
    except Exception as e:
        print(f'Error is :{e}')
        flash('Could not fetch the items')
        return redirect(url_for('index'))
    return render_template('dashboard.html',items_data=items_data)
@application.route('/addcart/<itemid>/<name>/<price>/<category>/<img>')
def addcart(itemid,name,price,category,img):
    print(session)
    if session.get('user'):
        if itemid not in session[session.get('user')]:
            session[session.get('user')][itemid]=[name,price,1,img,category] #adding cart item using session data
            session.modify=True
            flash(f'{name[0:10]} item added to cart')
            return redirect(url_for('index'))
        else:
            
            session[session.get('user')][itemid][2]+=1 # if item already in cart increment the quantity
            session.modify=True
            flash(f'item already in cart')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('userlogin'))

@application.route('/viewcart')
def viewcart():
    if session.get('user'):
        items=session[session.get('user')]
        if items:
            return render_template('cart.html',items=items)
        else:
            flash('NO items in cart')
            return redirect(url_for('index'))
    else:
        flash('pls login fisrt')
        return redirect(url_for('userlogin'))
@application.route('/removecart/<itemid>')
def removecart(itemid):
    if session.get('user'):
        if session[session.get('user')]:
            session[session.get('user')].pop(itemid)
            session.modify=True
            flash(f'{itemid} removed from cart')
            return redirect(url_for('viewcart'))
        else:
            flash('No items in cart')
            return redirect(url_for('viewcart'))
    else:
        flash(f'pls login first')
        return redirect(url_for('userlogin'))
@application.route('/description/<itemid>')
def description(itemid):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,imgname,created_at from items where itemid=uuid_to_bin(%s)',[itemid])
        itemdata=cursor.fetchone() #(1,'applicationle','sdfghj',345,789,'grocery','applicationle.jpg','2025-09-23')
    except Exception as e:
        print(f'ERROR:{e}')
        flash("counld n't fetch details")
        return redirect(url_for('index'))
    else:
        return render_template('description.html',itemdata=itemdata)
@application.route('/addreview/<itemid>',methods=['GET','POST'])   
def addreview(itemid):
    if session.get('user'):
        if request.method=='POST':
            review_text=request.form['review']
            rating=request.form['rate']
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into reviews(review_text,itemid,added_by,rating) values(%s,uuid_to_bin(%s),%s,%s)',[review_text,itemid,session.get('user'),rating])
            mydb.commit()
            flash('review added successfully')
            return redirect(url_for('description',itemid=itemid))
        return render_template('review.html')
    else:
        flash('pls login to add review')
        return redirect(url_for('description',itemid=itemid))
@application.route('/readreviews/<itemid>')
def readreviews(itemid):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,imgname,created_at from items where itemid=uuid_to_bin(%s)',[itemid])
        itemdata=cursor.fetchone()
        cursor.execute('select * from reviews where itemid=uuid_to_bin(%s)',[itemid])
        reviewdata=cursor.fetchall()
        
    except Exception as e:
        print(f'Error is {e}')
        flash('could not fetch data')
        return redirect(url_for('description',itemid=itemid))    
    else:
        return render_template('readreview.html',reviewdata=reviewdata,itemdata=itemdata)

















@application.route('/admincreate',methods=['GET','POST'])
def admincreate():
    if request.method=='POST':
        username=request.form['username']
        useremail=request.form['email'] #anusha@codegnan.com
        password=request.form['password']
        address=request.form['address']
        agreed=request.form['agree']
        print(request.form)
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(admin_email) from admin_details where admin_email=%s',[useremail])
            email_count=cursor.fetchone() #(0,)
        except Exception as e:
            print(f'actual error is {e}')
            flash('Could not fetch the data pls try again')
            return redirect(url_for('admincreate'))
        else:
            if email_count[0]==0:
                gotp=genotp()
                admindata={'username':username,'useremail':useremail,'password':password,'address':address,'agreed':agreed,'otp':gotp}
                print(admindata)
                subject='OTP for Admin Verification'
                body=f'Use the given otp for admin verify {gotp}'
                send_mail(to=useremail,subject=subject,body=body)
                flash(f'OTP has been sent given email {useremail}')
                return redirect(url_for('otpverify',endata=entoken(admindata)))
            elif email_count[0]==1:
                flash(f'Email already existed {useremail}')
                return redirect(url_for('admincreate'))
            

    return render_template('admincreate.html')
@application.route('/otpverify/<endata>',methods=['GET','POST'])
def otpverify(endata):
    if request.method=='POST':
        uotp=request.form['otp']
        ddata=dtoken(data=endata)
        #ddata={'username': 'anusha', 'useremail': 'anusha@codegnan.com', 'password': '111', 'address': 'asfhjdsd', 'agreed': 'on', 'otp': 'Rr0Wf1'}
        hashed=bcrypt.hashpw(ddata['password'].encode(),bcrypt.gensalt())
        print(hashed)
        print(type(hashed)) #binary string type
        if ddata['otp']==uotp:
            try:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into admin_details(admin_username,admin_email,admin_password,address) values(%s,%s,%s,%s)',[ddata['username'],ddata['useremail'],hashed,ddata['address']])
                mydb.commit()
                cursor.close()
            except Exception as e:
                print(f'the error is{e}')
                flash('Unable to store data')
                return redirect(url_for('admincreate'))
            else:
                flash(f'Admin details successfully stored')
                return redirect(url_for('adminlogin'))
        else:
            flash(f'OTP Wrong ')
    return render_template('adminotp.html')
@application.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        try:
            useremail=request.form['email'] #anusha@codegnan
            password=request.form['password'].encode() #b'1111'
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(admin_email) from admin_Details where admin_email=%s',[useremail])
            email_count=cursor.fetchone() #(0,) or (1,)
        except Exception as e:
            print(e)
            flash('something went wrong')
            return redirect(url_for('adminlogin'))
        else:
            if email_count[0]==1:
                cursor.execute('select admin_password from admin_details where admin_email=%s',[useremail])
                stored_password=cursor.fetchone()[0] #('111',)
                print(password,stored_password)
                if bcrypt.checkpw(password,stored_password):
                    session['admin']=useremail
                    return redirect(url_for('admindashboard'))
                else:
                    flash(f'password wrong')
                    return redirect(url_for('adminlogin'))
            elif email_count[0]==0:
                flash(f'{useremail} not found ')
                return redirect(url_for('adminlogin'))

    return render_template('adminlogin.html')
@application.route('/admindashboard')
def admindashboard():
    return render_template('adminpanel.html')
@application.route('/additem',methods=['GET','POST'])
def additem():
    if request.method=='POST':
        item_name=request.form['title']
        item_desc=request.form['Discription']
        item_quantity=request.form['quantity']
        item_cost=request.form['price']
        item_category=request.form['category']
        item_image=request.files['file']
        #print(item_image.filename.split('.')[-1])
        filename=genotp()+'.'+item_image.filename.split('.')[-1]  #'Fy6Gr5.jpeg'
        try:
            path=os.path.abspath(__file__) #C:\Users\User\Desktop\ecom\application.py
            dname=os.path.dirname(path) #C:\Users\User\Desktop\ecom
            print(dname)
            static_path=os.path.join(dname,'static')
            print(static_path)
            item_image.save(os.path.join(static_path,filename))
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into items(itemid,item_name,description,item_cost,item_quantity,item_category,added_by,imgname) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s)',[item_name,item_desc,item_cost,item_quantity,item_category,session.get('admin'),filename])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(f'Error:{e}')
            flash('could not added item')
            return redirect(url_for('additem'))
        else:
            flash(f'{item_name[:10]}.. added successfully')
            return redirect(url_for('additem'))


    return render_template('additem.html')
@application.route('/viewitems')
def viewitems():
    if session.get('admin'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select bin_to_uuid(itemid),item_name,item_cost,imgname from items where added_by=%s',[session.get('admin')])
            itemsdata=cursor.fetchall()
        except Exception as e:
            print(f'the error is {e}')
            flash('Could not fetch the data')
            return redirect(url_for('admindashboard'))
        else:
            return render_template('viewall_items.html',itemsdata=itemsdata)
    else:
        flash(f'pls login first')
        return redirect(url_For('adminlogin'))
@application.route('/view_item/<itemid>')
def view_item(itemid):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,imgname,created_at from items where itemid=uuid_to_bin(%s) and added_by=%s',[itemid,session.get('admin')])
        itemdata=cursor.fetchone()
    except Exception as e:
        print(f'ERROR:{e}')
        flash("counld n't fetch details")
        return redirect(url_for('viewitems'))
    else:
        return render_template('view_item.html',itemdata=itemdata)
@application.route('/updateitem/<itemid>',methods=['GET','POST'])
def updateitem(itemid):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,imgname,created_at from items where itemid=uuid_to_bin(%s) and added_by=%s',[itemid,session.get('admin')])
        itemdata=cursor.fetchone()
    except Exception as e:
        print(f'ERROR:{e}')
        flash("counld n't fetch details")
        return redirect(url_for('viewitems'))
    else:
        if request.method=='POST':
            item_name=request.form['title']
            item_description=request.form['Description']
            item_price=request.form['price']
            item_category=request.form['category']
            print(item_category)
            item_quantity=request.form['quantity']
            item_img=request.files['file']
            if item_img.filename=='':
                filename=itemdata[6]
            else:
                filename=genotp()+'.'+item_img.filename.split('.')[-1]
                path=os.path.abspath(__file__) #C:\Users\User\Desktop\ecom\application.py
                dname=os.path.dirname(path) #C:\Users\User\Desktop\ecom
                print(dname)
                static_path=os.path.join(dname,'static')
                print(static_path)
                item_img.save(os.path.join(static_path,filename))
                os.remove(os.path.join(static_path,itemdata[6]))
            cursor=mydb.cursor(buffered=True)
            cursor.execute('update items set item_name=%s,description=%s,item_cost=%s,item_quantity=%s,item_category=%s,imgname=%s where itemid=uuid_to_bin(%s) and added_by=%s',[item_name,item_description,item_price,item_quantity,item_category,filename,itemid,session.get('admin')])
            mydb.commit()
            cursor.close()
            flash('item updated')
            return redirect(url_for('view_item',itemid=itemid))
        return render_template('update_item.html',item_data=itemdata)
@application.route('/deleteitem/<itemid>')
def deleteitem(itemid):
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select imgname from items where itemid=uuid_to_bin(%s) and added_by=%s',[itemid,session.get('admin')])
        stored_imgname=cursor.fetchone()[0]
        path=os.path.abspath(__file__) #C:\Users\User\Desktop\ecom\application.py
        dname=os.path.dirname(path) #C:\Users\User\Desktop\ecom
        static_path=os.path.join(dname,'static') #C:\Users\User\Desktop\ecom\static
        os.remove(os.path.join(static_path, stored_imgname))
        cursor.execute('delete from items where itemid=uuid_to_bin(%s) and added_by=%s',[itemid,session.get('admin')])
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(e)
        flash(f'item could not delete ')
        return redirect(url_for('viewitems'))
    else:
        flash('item deleted successfully')
        return redirect(url_for('viewitems'))
@application.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('To logout pls login first')
        return redirect(url_for('adminlogin'))
@application.route('/usercreate',methods=['GET','POST'])
def usercreate():
    if request.method=='POST':
        username=request.form['name']
        useremail=request.form['email'] #anusha@codegnan.com
        password=request.form['password']
        address=request.form['address']
        gender=request.form['usergender']
        print(request.form)
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(useremail) from users where useremail=%s',[useremail])
            email_count=cursor.fetchone() #(0,)
        except Exception as e:
            print(f'actual error is {e}')
            flash('Could not fetch the data pls try again')
            return redirect(url_for('usercreate'))
        else:
            if email_count[0]==0:
                gotp=genotp()
                userdata={'username':username,'useremail':useremail,'password':password,'address':address,'gender':gender,'otp':gotp}
                print(userdata)
                subject='OTP for Admin Verification'
                body=f'Use the given otp for admin verify {gotp}'
                send_mail(to=useremail,subject=subject,body=body)
                flash(f'OTP has been sent given email {useremail}')
                return redirect(url_for('userotpverify',endata=entoken(userdata)))
            elif email_count[0]==1:
                flash(f'Email already existed {useremail}')
                return redirect(url_for('usercreate'))
            

    return render_template('usersignup.html')
@application.route('/userotpverify/<endata>',methods=['GET','POST'])
def userotpverify(endata):
    if request.method=='POST':
        uotp=request.form['otp']
        ddata=dtoken(data=endata)
        hashed=bcrypt.hashpw(ddata['password'].encode(),bcrypt.gensalt())
        print(hashed)
        print(type(hashed)) #binary string type
        if ddata['otp']==uotp:
            try:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into users(username,useremail,password,address,gender) values(%s,%s,%s,%s,%s)',[ddata['username'],ddata['useremail'],hashed,ddata['address'],ddata['gender']])
                mydb.commit()
                cursor.close()
            except Exception as e:
                print(f'the error is{e}')
                flash('Unable to store data')
                return redirect(url_for('usercreate'))
            else:
                flash(f'user details successfully stored')
                return redirect(url_for('userlogin'))
        else:
            flash(f'OTP Wrong ')
    return render_template('userotp.html')
@application.route('/userlogin',methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        try:
            useremail=request.form['email'] #anusha@codegnan
            password=request.form['password'].encode() #b'1111'
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(useremail) from users where useremail=%s',[useremail])
            email_count=cursor.fetchone() #(0,) or (1,)
        except Exception as e:
            print(e)
            flash('something went wrong')
            return redirect(url_for('userlogin'))
        else:
            if email_count[0]==1:
                cursor.execute('select password from users where useremail=%s',[useremail])
                stored_password=cursor.fetchone()[0] #('111',)
                print(password,stored_password)
                if bcrypt.checkpw(password,stored_password):
                    print(session)
                    session['user']=useremail#{'user':anusha@codegnan.com}

                    if not session.get(useremail):
                        session[useremail]={} #{'user':'anusha@codegnan.com','anusha@codegnan.com':{}}
                        session.modify=True
                    print(session)
                    return redirect(url_for('index'))
                else:
                    flash(f'password wrong')
                    return redirect(url_for('userlogin'))
            elif email_count[0]==0:
                flash(f'{useremail} not found ')
                return redirect(url_for('userlogin'))

    return render_template('userlogin.html')
@application.route('/userlogout')
def userlogout():
    if session.get('user'):
        session.pop('user')
        session.modify=True
        return redirect(url_for('userlogin'))
    else:
        return redirect(url_for('userlogin'))
@application.route('/pay/<itemid>/<name>/<float:price>/<quantity>',methods=['GET','POST'])
def pay(itemid,name,price,quantity):
    if session.get('user'):
        try:
            if request.method=='POST':
                qyt=int(request.form['qyt'])
            else:
                qyt=int(quantity)
            price=price*100
            amount=price*qyt
            print(amount,qyt)
            print(f'creating payment for item:{itemid}, name :{name},price:{amount}')
            order=client.order.create({
                "amount": amount,
                "currency": "INR",
                'payment_capture':'1'})
            print(f"order created: {order}")
            return render_template('pay.html',order=order,itemid=itemid,name=name,total_amount=amount)
        except Exception as e:
            print(f'could not place order {e}')
            return redirect(url_for('viewcart'))

    else:
        flash('pls login first')
        return redirect(url_for('userlogin'))
@application.route('/success',methods=['GET','POST'])
def success():
    if request.method=='POST':
        payment_id=request.form['razorpay_payment_id']
        order_id=request.form['razorpay_order_id']
        order_signature=request.form['razorpay_signature']
        itemid=request.form['itemid']
        name=request.form['name']
        total_amount=request.form['total_amount']
        params_dict={
            'razorpay_payment_id':payment_id,
            'razorpay_order_id':order_id,
            'razorpay_signature':order_signature

        }
        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return 'Payment verification failed!',400
        else:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into orders(item_id,item_name,total,payment_by) values(uuid_to_bin(%s),%s,%s,%s)',[itemid,name,total_amount,session.get('user')])
            mydb.commit()
            flash(f'order placed with {total_amount}')
            return redirect(url_for('index'))
@application.route('/orders')
def orders():
    if session.get('user'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select * from orders where payment_by=%s',[session.get('user')])
            orders_data=cursor.fetchall()
        except Exception as e:
            print(f'{e}')
            flash('could not fetch orders')
            return redirect(url_for('index'))
        else:
            return render_template('orders.html',orders_data=orders_data)
    else:
        flash('pls login first')
        return redirect(url_for('userlogin'))
'''@application.route('/getinvoice/<ordid>.pdf')
def getinvoice(ordid):
    if session.get('user'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select * from orders where order_id=%s and payment_by=%s',[ordid,session.get('user')])
            order_data=cursor.fetchone()
            cursor.execute('select useremail,username,address,gender from users where useremail=%s',[session.get('user')])
            user_data=cursor.fetchone()
            html=render_template('bill.html',order_data=order_data,user_data=user_data)
            pdf=pdfkit.from_string(html,False,configuration=config)
            response=Response(pdf,content_type='applicationlication/pdf')
            response.headers['Content-Disposition']='inline; filename=output.pdf'
            return response
        except Exception as e:
            print(f'error{e}')
            flash('could not convert pdf')
            return redirect(url_for('orders'))
    else:
        flash('pls login first')
        return redirect(url_for('userlogin'))'''
@application.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        sdata=request.form['search']
        strg=['A-Za-z0-9']
        pattern= re.compile(f'^{strg}',re.IGNORECASE)
        if (pattern.search(sdata)):
            print('hi')
            try:
                cursor=mydb.cursor(buffered=True)
                cursor.execute('select bin_to_uuid(itemid),item_name,description,item_cost,item_quantity,item_category,created_at,imgname from items where itemid like %s or item_name like %s or description like %s or  item_cost like %s or item_category like %s or  created_at like %s ',['%'+sdata+'%','%'+sdata+'%','%'+sdata+'%','%'+sdata+'%','%'+sdata+'%','%'+sdata+'%'])
                items_data=cursor.fetchall()
            except Exception as e:
                print(f'error is {e}')
                flash(f'could fetch search data')
                return redirect(url_for('index'))
            else:
                return render_template('dashboard.html',items_data=items_data)

        else:
            flash('No data given')
            return redirect(url_for('index'))
    


        
if __name__=='__main__':
    application.run()