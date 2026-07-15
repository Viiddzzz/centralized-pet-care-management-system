import json
from datetime import date
from pathlib import Path
from datetime import datetime, timedelta
import base64
from flask import Flask, request, render_template, session, redirect, url_for
import firebase_admin
import random
from firebase_admin import credentials, firestore
from MailSent import send_email
import time
import os
from datetime import datetime, date, timedelta
import razorpay
import operator as op

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)
app.secret_key = "MySecretKey@123"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

pettypes = ["Dog","Cat"]
specializations=["MBBS","MD", "MPhil"]
accessoriestypes = ["Clothes","Toys","Food","Soap","BodyCream"]

expinyears=["Fresher",">=1", ">=2",">=3",">=5",">=10"]
RAZOR_KEY_ID="rzp_test_bwFUQvFdcBdnqI"
RAZOR_KEY_SECRET="NN9Yi7mL7s15FtqgWGOLr5Zp"
razorpay_client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))

@app.route('/userdeletefromcart', methods=['POST','GET'])
def userdeletefromcart():
    try:
        id=request.args['id']
        aid=request.args['aid']
        rqty=request.args['rqty']
        db = firestore.client()
        dbref = db.collection('newaccessory')        
        adata = db.collection('newaccessory').document(aid).get().to_dict()        
        aqty = adata['Quantity']        
        db = firestore.client()
        data_ref = db.collection(u'newaccessory').document(aid)
        data_ref.update({u'Quantity': (int(aqty)+int(rqty))})
        db = firestore.client()
        dbref = db.collection('newaddtocart')
        dbref.document(id).delete()
        return redirect(url_for("userviewaddtocart"))
    except Exception as e:
        return str(e)

@app.route('/userviewaddtocart', methods=['POST','GET'])
def userviewaddtocart():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newaddtocart')
        newdata = newdata_ref.get()
        userid = session['userid']
        data,total,context=[],0,{}
        for doc in newdata:
            temp = doc.to_dict()
            if(temp['UserId']==userid and temp['PaymentStatus']=='PaymentNotDone'):
                data.append(doc.to_dict())
                total+= int(temp['Total'])
        print("Cart Data " , data)
        currency = 'INR'
        amount = 200*100  # Rs. 200
        if(total>0):
            amount=total*100
        session['total']=amount
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'usermakepayment1'
        # we need to pass these details to frontend.
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        return render_template("userviewaddtocart.html", data=data, total=total, context=context)
    except Exception as e:
        return str(e)

@app.route('/usermakepayment1', methods=['POST','GET'])
def usermakepayment1():
    # only accept POST request.
    if request.method == "POST":
        try:
            id = int(session['userid'])
            db = firestore.client()
            data_ref = db.collection('newaddtocart')
            newdata = data_ref.get()
            array=[]
            for doc in newdata:
                temp = doc.to_dict()
                print("Temp : ", temp)
                if (int(temp['UserId']) == id and temp['PaymentStatus'] == 'PaymentNotDone'):
                    array.append(temp['id'])
            print("Ids : ",array)
            for x in array:
                db = firestore.client()
                data_ref = db.collection(u'newaddtocart').document(x)
                data_ref.update({u'PaymentStatus': 'PaymentDone'})

            total=session['total']
            # get the required parameters from post request.
            payment_id = request.form['razorpay_payment_id', '']
            razorpay_order_id = request.form['razorpay_order_id', '']
            signature = request.form['razorpay_signature', '']
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.payment.capture(payment_id, total)
            print("Res : ", json.dumps(razorpay_client.payment.fetch(payment_id)))
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            print("Result : ", result)
            if result is not None:
                amount = total  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    # render success page on successful caputre of payment
                    return render_template('paymentsuccess.html')
                except:
                    # if there is an error while capturing payment.
                    return render_template('paymentsuccess.html')
            else:
                # if signature verification fails.
                return render_template('paymentsuccess.html')
        except:
            # if we don't find the required parameters in POST data
            #return HttpResponseBadRequest()
            return render_template('paymentsuccess.html')
    else:
        # if other than POST request is made.
        #return HttpResponseBadRequest()
        return render_template('paymentsuccess.html')

@app.route('/useraddtocart1', methods=['POST','GET'])
def useraddtocart1():
    try:
        msg=""
        print("Add New Add To Cart page")
        if request.method == 'POST':
            userid = session['userid']
            aid = request.form['aid']
            aname = request.form['aname']
            atype = request.form['accessorytype']
            qty = request.form['qty']
            price = request.form['price']
            rqty = request.form['rqty']
            total = request.form['total']            
            id = str(round(time.time()))
            json = {'id': id, 'UserId':userid,
                    'AccessoryId':aid,
                    'AccessoryName':aname,
                    'AccessoryType': atype, 'RequiredQty': rqty,
                    'Total': total, 'Price': price,
                    'PaymentStatus': "PaymentNotDone"}
            db = firestore.client()
            newuser_ref = db.collection('newaddtocart')
            newuser_ref.document(id).set(json)            
            db = firestore.client()            
            data_ref = db.collection(u'newaccessory').document(aid)
            data_ref.update({u'Quantity': (int(qty)-int(rqty))})
        return redirect(url_for("userviewaddtocart"))
    except Exception as e:
        return str(e)

@app.route('/useraddtocart', methods=['GET','POST'])
def useraddtocart():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newaccessory')
        data = dbref.document(id).get().to_dict()
        print("User Data ", data)
        return render_template("useraddtocart.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/usersearchaccessories', methods=['POST','GET'])
def usersearchaccessories():
    try:
        db = firestore.client()
        data=[]
        if(request.method=="POST"):
            aname = request.form["aname"]
            newdata_ref = db.collection('newaccessory')
            newdata = newdata_ref.get()        
            for doc in newdata:
                temp = doc.to_dict()                
                if (op.contains(temp['AccessoryName'], aname) or op.contains(temp['AccessoryType'],aname)):
                    data.append(temp)
        else:
            newdata_ref = db.collection('newaccessory')
            newdata = newdata_ref.get()        
            for doc in newdata:
                temp = doc.to_dict()
                data.append(temp)
        print("Accessory Data " , data)        
        return render_template("usersearchaccessories.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewappointments', methods=['POST','GET'])
def adminviewappointments():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newappointment')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            temp = doc.to_dict()
            data.append(temp)
        print("Pet Data " , data)
        return render_template("adminviewappointments.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewprescription', methods=['GET','POST'])
def adminviewprescription():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newappointment')
        data = dbref.document(id).get().to_dict()
        print("Appointment Data ", data)
        return render_template("adminviewprescription.html", row=data)
    except Exception as e:
        return str(e)

@app.route('/adminaddaccessories', methods=['POST','GET'])
def adminaddaccessories():
    try:
        msg=""
        print("Add New Accessory page")
        if request.method == 'POST':
            aname = request.form['aname']
            accessory = request.form['accessory']
            qty = request.form['qty']
            price = request.form['price']
            description = request.form['description']
            file = request.files['file']
            
            id = str(round(time.time()))
            file_path = Path(file.filename)
            extension = file_path.suffix
            filename="Image"+id+extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            json = {'id': id,
                        'AccessoryName': aname, 'Quantity': qty,
                        'AccessoryType': accessory, 'Price': price,
                        'Description': description, 'FileName':filename}
            db = firestore.client()
            newuser_ref = db.collection('newaccessory')
            newuser_ref.document(id).set(json)
            print("User Accessory Success")
            msg = "New Accessory Inserted Success"
        return render_template("adminaddaccessories.html", msg=msg, 
                               accessoriestypes=accessoriestypes)
    except Exception as e:
        return str(e)

@app.route('/doctorviewprescription', methods=['GET','POST'])
def doctorviewprescription():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newappointment')
        data = dbref.document(id).get().to_dict()
        print("Appointment Data ", data)
        return render_template("doctorviewprescription.html", row=data)
    except Exception as e:
        return str(e)

@app.route('/userviewprescription', methods=['GET','POST'])
def userviewprescription():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newappointment')
        data = dbref.document(id).get().to_dict()
        print("Appointment Data ", data)
        return render_template("userviewprescription.html", row=data)
    except Exception as e:
        return str(e)

@app.route('/doctorupdateprescription1', methods=["POST","GET"])
def doctorupdateprescription1():
    try:
        appid = request.form['appid']
        print("App Id : ", appid)
        type1 = request.form['type1']
        pres1 = request.form['pres1']
        routine1 = request.form['routine1']
        type2 = request.form['type2']
        pres2 = request.form['pres2']
        routine2 = request.form['routine2']
        type3 = request.form['type3']
        pres3 = request.form['pres3']
        routine3 = request.form['routine3']
        db = firestore.client()
        data_ref = db.collection(u'newappointment').document(appid)
        data_ref.update({u'PrescriptionStatus': "Updated"})
        data_ref.update({u'Type1': type1})
        data_ref.update({u'Prescription1': pres1})
        data_ref.update({u'Routine1': routine1})
        
        data_ref.update({u'Type2': type2})
        data_ref.update({u'Prescription2': pres2})
        data_ref.update({u'Routine2': routine2})
        
        data_ref.update({u'Type3': type3})
        data_ref.update({u'Prescription3': pres3})
        data_ref.update({u'Routine3': routine3})
        
        return redirect(url_for("doctorapplyprescription"))
    except Exception as e:
        return str(e)

@app.route('/doctorupdateprescription', methods=["POST","GET"])
def doctorupdateprescription():
    try:
        id = request.args['id']
        db = firestore.client()
        dbref = db.collection('newappointment')
        data = dbref.document(id).get().to_dict()
        print("Doctor Data ", data)
        return render_template("doctorupdateprescription.html", data=data)
    except Exception as e:
        return str(e)
    
@app.route('/doctorupdatestatus', methods=['GET','POST'])
def doctorupdatestatus():
    try:
        id=request.args['id']
        status=request.args['status']
        db = firestore.client()
        print("Id : ",id, " Status : ", status)
        data_ref = db.collection(u'newappointment').document(id)
        data_ref.update({u'AppointmentStatus': status})
        return redirect(url_for("doctorviewappointments"))
    except Exception as e:
        return str(e)

@app.route('/doctorapplyprescription', methods=['POST','GET'])
def doctorapplyprescription():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newappointment')
        newdata = newdata_ref.get()
        userid = session['userid']
        print("User Id : ", userid)
        data=[]
        for doc in newdata:
            temp = doc.to_dict()
            if(temp['DoctorId']==userid and temp['AppointmentStatus']=='Accepted'):
                data.append(doc.to_dict())
        print("Appointment Data " , data)
        return render_template("doctorapplyprescription.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/doctorviewappointments', methods=['POST','GET'])
def doctorviewappointments():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newappointment')
        newdata = newdata_ref.get()
        userid = session['userid']
        print("User Id : ", userid)
        data=[]
        for doc in newdata:
            temp = doc.to_dict()
            if(temp['DoctorId']==userid and temp['PaymentStatus']=='PaymentDone'):
                data.append(doc.to_dict())
        print("Pet Data " , data)
        return render_template("doctorviewappointments.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewappointments', methods=['POST','GET'])
def userviewappointments():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newappointment')
        newdata = newdata_ref.get()
        userid = session['userid']
        data,total,context=[],0,{}
        for doc in newdata:
            temp = doc.to_dict()
            if(temp['UserId']==userid and temp['AppointmentStatus'] == 'Requested'
               and temp['PaymentStatus']=='PaymentNotDone'):
                data.append(doc.to_dict())
                total+= int(temp['DoctorFees'])
        print("Pet Data " , data)
        currency = 'INR'
        amount = 200*100  # Rs. 200
        if(total>0):
            amount=total*100
        session['total']=amount
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture='0'))
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'usermakepayment'
        # we need to pass these details to frontend.
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        return render_template("userviewappointments.html", data=data, total=total, context=context)
    except Exception as e:
        return str(e)

@app.route('/usermakepayment', methods=['POST','GET'])
def usermakepayment():
    # only accept POST request.
    if request.method == "POST":
        try:
            id = int(session['userid'])
            db = firestore.client()
            data_ref = db.collection('newappointment')
            newdata = data_ref.get()
            array=[]
            for doc in newdata:
                temp = doc.to_dict()
                print("Temp : ", temp)
                if (int(temp['UserId']) == id and temp['AppointmentStatus'] == 'Requested'):
                    array.append(temp['id'])

            print("Ids : ",array)

            for x in array:
                db = firestore.client()
                data_ref = db.collection(u'newappointment').document(x)
                data_ref.update({u'PaymentStatus': 'PaymentDone'})

            total=session['total']
            # get the required parameters from post request.
            payment_id = request.form['razorpay_payment_id', '']
            razorpay_order_id = request.form['razorpay_order_id', '']
            signature = request.form['razorpay_signature', '']
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.payment.capture(payment_id, total)
            print("Res : ", json.dumps(razorpay_client.payment.fetch(payment_id)))
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            print("Result : ", result)
            if result is not None:
                amount = total  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    # render success page on successful caputre of payment
                    return render_template('paymentsuccess.html')
                except:
                    # if there is an error while capturing payment.
                    return render_template('paymentsuccess.html')
            else:
                # if signature verification fails.
                return render_template('paymentsuccess.html')
        except:
            # if we don't find the required parameters in POST data
            #return HttpResponseBadRequest()
            return render_template('paymentsuccess.html')
    else:
        # if other than POST request is made.
        #return HttpResponseBadRequest()
        return render_template('paymentsuccess.html')

@app.route('/userdeleteappointment', methods=['POST','GET'])
def userdeleteappointment():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newappointment')
        dbref.document(id).delete()
        return redirect(url_for("userviewappointments"))
    except Exception as e:
        return str(e)

@app.route('/usermakeappointment1', methods=['POST','GET'])
def usermakeappointment1():
    try:
        id=request.args['id']
        session['petid']=id
        db = firestore.client()
        dbref = db.collection('newpet')
        petdata = dbref.document(id).get().to_dict()        
        print("Pet Data " , petdata)
        newdata_ref = db.collection('newdoctor')
        newdata = newdata_ref.get()
        doctordata=[]
        for doc in newdata:
            doctordata.append(doc.to_dict())
        print("Doctor Data " , doctordata)
        return render_template("usermakeappointment1.html", doctordata=doctordata,
                               petdata=petdata)
    except Exception as e:
        return str(e)

@app.route('/usermakeappointment2', methods=['POST','GET'])
def usermakeappointment2():
    try:
        id=request.args['id']
        petid=session['petid']
        db = firestore.client()
        dbref = db.collection('newpet')
        petdata = dbref.document(petid).get().to_dict()
        print("Selected Pet Data " , petdata)
        dbref = db.collection('newdoctor')
        doctordata = dbref.document(id).get().to_dict()        
        print("Selected Doctor Data " , doctordata)
        today = date.today()
        print(today)            # Output: 2024-03-23 (or the current date)
        print(today.isoformat())
        return render_template("usermakeappointment2.html", doctordata=doctordata,
                               petdata=petdata, today=today)
    except Exception as e:
        return str(e)

@app.route('/usermakeappointment3', methods=['POST','GET'])
def usermakeappointment3():
    try:
        msg=""
        print("Add New Appointment page")
        if request.method == 'POST':
            doctorid = request.form['doctorid']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            phnum = request.form['phnum']
            specialization = request.form['specialization']
            expinyear = request.form['expinyears']
            appdate= request.form['appdate']
            apptime= request.form['apptime']
            doctorfees= request.form['doctorfees']
            userid = session['userid']
            petid = session['petid']
            db = firestore.client()
            dbref = db.collection('newpet')
            petdata = dbref.document(petid).get().to_dict()
            print("Selected Pet Data " , petdata)
            id = str(round(time.time()))
            
            json = {'id': id, 'UserId':userid, 'PetId':petid,
                    'DoctorId':doctorid,'PetName': petdata['PetName'],'PetType': petdata['PetType'],
                   'PetWeight': petdata['PetWeight'], 'PetHeight': petdata['PetHeight'],
                   'PetColor': petdata['PetColor'], 'Description': petdata['Description'],
                   'FirstName': fname, 'LastName': lname,'EmailId': email, 'PhoneNumber': phnum,
                   'Specialization':specialization,'ExpInYears':expinyear,
                   'DoctorFees':doctorfees, 'AppointmentDate':appdate,
                   'AppointmentTime':apptime, 'AppointmentStatus':"Requested",
                   "DoctorPrescription":None,'PaymentStatus':"PaymentNotDone",
                   "PrescriptionStatus":"NotUpdated",
                   "Type1":None,"Prescription1":None,"Routine1":None,
                   "Type2":None,"Prescription2":None,"Routine2":None,
                   "Type3":None,"Prescription3":None,"Routine3":None}
            db = firestore.client()
            newuser_ref = db.collection('newappointment')
            newuser_ref.document(id).set(json)
            print("User Requested Appointment Success")
            #msg = "User Requested Appointment Success"
        return redirect(url_for("userviewappointments"))
    except Exception as e:
        return str(e)

@app.route('/useraddpet', methods=['POST','GET'])
def useraddpet():
    try:
        msg=""
        print("Add New Staff page")
        if request.method == 'POST':
            pname = request.form['pname']
            pettype = request.form['pettype']
            petweight = request.form['petweight']
            petheight = request.form['petheight']
            petcolor = request.form['petcolor']
            description = request.form['description']
            file = request.files['file']
            userid = session['userid']
            id = str(round(time.time()))
            file_path = Path(file.filename)
            extension = file_path.suffix
            filename="Image"+id+extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            json = {'id': id, 'UserId':userid,
                   'PetName': pname, 'PetType': pettype,
                   'PetWeight': petweight, 'PetHeight': petheight,
                   'PetColor': petcolor, 'Description': description,
                   'FileName':filename}
            db = firestore.client()
            newuser_ref = db.collection('newpet')
            newuser_ref.document(id).set(json)
            print("User Add New Pet Success")
            msg = "User Add New Pet Success"
        return render_template("useraddpet.html", msg=msg, pettypes=pettypes)
    except Exception as e:
        return str(e)

@app.route('/adminviewpets', methods=['POST','GET'])
def adminviewpets():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newpet')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Pet Data " , data)
        return render_template("adminviewpets.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewaccessories', methods=['POST','GET'])
def adminviewaccessories():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newaccessory')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Pet Data " , data)
        return render_template("adminviewaccessories.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewpets', methods=['POST','GET'])
def userviewpets():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newpet')
        newdata = newdata_ref.get()
        userid = session['userid']
        data=[]
        for doc in newdata:
            if(doc.to_dict()['UserId']==userid):
                data.append(doc.to_dict())
        print("Pet Data " , data)
        return render_template("userviewpets.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/usermakeappointment', methods=['POST','GET'])
def usermakeappointment():
    try:        
        db = firestore.client()
        newdata_ref = db.collection('newpet')
        newdata = newdata_ref.get()
        userid = session['userid']
        data=[]
        for doc in newdata:
            if(doc.to_dict()['UserId']==userid):
                data.append(doc.to_dict())
        print("Pet Data " , data)
        return render_template("usermakeappointment.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminadddoctor', methods=['POST','GET'])
def adminadddoctor():
    try:
        msg=""
        print("Add New Staff page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            file = request.files['file']
            specialization = request.form['specialization']
            expinyear = request.form['expinyear']
            doctorfees= request.form['doctorfees']
            
            db = firestore.client()
            dbref = db.collection('newdoctor')
            userdata = dbref.get()
            is_present=False
            for doc in userdata:
                temp=doc.to_dict()
                if(temp['UserName']==uname or temp['PhoneNumber']==phnum or temp['EmailId']==email):
                    is_present=True
                    break
            if(not is_present):
                encode = base64.b64encode(pwd.encode("utf-8"))
                #print("str-byte : ", encode)
                id = str(round(time.time()))
                file_path = Path(file.filename)
                extension = file_path.suffix
                filename="Resume"+id+extension
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                json = {'id': id,
                        'FirstName': fname, 'LastName': lname,
                        'UserName': uname, 'Password': encode,
                        'EmailId': email, 'PhoneNumber': phnum,
                        'Specialization':specialization,'ExpInYears':expinyear,
                        'DoctorFees':doctorfees,
                        'Address': address, 'FileName':filename}
                db = firestore.client()
                newuser_ref = db.collection('newdoctor')
                newuser_ref.document(id).set(json)
                print("User Doctor Success")
                msg = "New Doctor Inserted Success"
            else:
                msg = "UserName/Emailid/PhoneNumber already exists"
        return render_template("adminadddoctor.html", msg=msg, 
                               specializations=specializations,
                               expinyears=expinyears)
    except Exception as e:
        return str(e)

@app.route('/userforgotpassword', methods=['POST','GET'])
def userforgotpassword():
    try:
        msg=""
        if(request.method=="POST"):
            uname = request.form['uname']            
            db = firestore.client()
            dbref = db.collection('newuser')
            userdata = dbref.get()
            data = []
            for doc in userdata:
                print(doc.to_dict())
                print(f'{doc.id} => {doc.to_dict()}')
                data.append(doc.to_dict())
            flag = False
            for temp in data:
                if uname == temp['UserName']:                
                    session['emailid'] = temp['EmailId']
                    emailid=temp['EmailId']
                    session['userid'] = temp['id']
                    session['username'] = temp['FirstName'] + " " + temp['LastName']
                    flag = True
                    break
            if (flag):
                return render_template("usersendotppage.html", emailid=emailid)
            else:
                msg = "UserName is Invalid"
        return render_template("userforgotpassword.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/usersendotppage', methods=['POST','GET'])
def usersendotppage():
    try:
        msg=""
        if(request.method=="POST"):
            otp = str(random.randint(1000,9999))
            session["otp"]=otp
            toemail = request.form["email"]
            body = "OTP to change the password : " + otp
            subject = "Change Password"
            receipients = [toemail]
            send_email(subject, body, receipients)
            return render_template("userenterotppage.html", msg=msg)    
        return render_template("userforgotpassword.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/usercheckotp', methods=['POST','GET'])
def usercheckotp():
    try:
        msg=""
        if(request.method=="POST"):
            storedotp = session["otp"]
            enteredotp = request.form["otp"]
            flag=False
            if(str(storedotp)==str(enteredotp)):
                flag=True
            if(flag):
                return render_template("userchangepasswordpage.html", msg=msg)
            else:
                msg="OTP is not matching"
        return render_template("userenterotppage.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/userchangepasswordpage', methods=['POST','GET'])
def userchangepasswordpage():
    try:
        msg=""
        if(request.method=="POST"):
            userid = session['userid']
            pwd = request.form["pwd"]
            cpwd = request.form["cpwd"]            
            if(pwd==cpwd):            
                db = firestore.client()
                data_ref = db.collection(u'newuser').document(userid)
                encode = base64.b64encode(pwd.encode("utf-8"))
                data_ref.update({u'Password': encode})
                return render_template("userlogin.html", msg=msg)        
            else:
                msg="Password & Confirm Password are not Matching"
        return render_template("userchangepasswordpage.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/userviewreports', methods=['POST','GET'])
def userviewreports():
    try:
        db = firestore.client()
        data_ref = db.collection('newappointment')
        newdata = data_ref.get()
        id = int(session['userid'])
        print('UserId : ', id)
        data = []
        for doc in newdata:
            temp = doc.to_dict()
            print("Temp : ", temp)
            if (int(temp['UserId']) == id):
                data.append(doc.to_dict())
        
        db = firestore.client()
        data_ref = db.collection('newaddtocart')
        newdata = data_ref.get()
        cartdata=[]
        for doc in newdata:
            temp = doc.to_dict()
            cartdata.append(temp)
        
        return render_template("userviewreports.html", data=data, cartdata=cartdata)
    except Exception as e:
        return str(e)

@app.route('/')
@app.route('/index')
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/usermainpage')
def usermainpage():
    try:
        return render_template("usermainpage.html")
    except Exception as e:
        return str(e)

@app.route('/logout')
def logoutpage():
    try:
        session['id']=None
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/about')
def aboutpage():
    try:
        return render_template("about.html")
    except Exception as e:
        return str(e)

@app.route('/services')
def servicespage():
    try:
        return render_template("services.html")
    except Exception as e:
        return str(e)

@app.route('/gallery')
def gallerypage():
    try:
        return render_template("gallery.html")
    except Exception as e:
        return str(e)

@app.route('/adminlogin', methods=['GET','POST'])
def adminloginpage():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname'].lower()
        pwd = request.form['pwd'].lower()
        print("Uname : ", uname, " Pwd : ", pwd)
        if uname == "admin" and pwd == "admin":
            return render_template("adminmainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("adminlogin.html", msg=msg)

@app.route('/userlogin', methods=['GET','POST'])
def userlogin():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            print("Pwd : ", temp['Password'])            
            decode = base64.b64decode(temp['Password']).decode("utf-8")
            if uname == temp['UserName'] and pwd == decode:
                session['userid'] = temp['id']
                session['emailid'] = temp['EmailId']
                session['username'] = temp['FirstName'] + " " + temp['LastName']
                flag = True
                break
        if (flag):
            return render_template("usermainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("userlogin.html", msg=msg)

@app.route('/doctorlogin', methods=['GET','POST'])
def doctorlogin():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        dbref = db.collection('newdoctor')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            print("Pwd : ", temp['Password'])            
            decode = base64.b64decode(temp['Password']).decode("utf-8")
            if uname == temp['UserName'] and pwd == decode:
                session['userid'] = temp['id']
                print("Doctor Id : ", temp['id'])
                flag = True
                break
        if (flag):
            return render_template("doctormainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("doctorlogin.html", msg=msg)

@app.route('/companyviewprofile', methods=['GET','POST'])
def companyviewprofile():
    try:
        id=session['userid']
        db = firestore.client()
        dbref = db.collection('newcompany')
        data = dbref.document(id).get().to_dict()
        print("User Data ", data)
        return render_template("companyviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewprofile', methods=['GET','POST'])
def userviewprofile():
    try:
        id=session['userid']
        db = firestore.client()
        dbref = db.collection('newuser')
        data = dbref.document(id).get().to_dict()
        print("User Data ", data)
        return render_template("userviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/doctorviewprofile', methods=['GET','POST'])
def doctorviewprofile():
    try:
        id=session['userid']
        db = firestore.client()
        dbref = db.collection('newdoctor')
        data = dbref.document(id).get().to_dict()
        print("Doctor Data ", data)
        return render_template("doctorviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewfullreport', methods=['GET','POST'])
def adminviewfullreport():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newreport')
        data = dbref.document(id).get().to_dict()
        print("Report Data ", data)
        return render_template("adminviewfullreport.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewfullreport', methods=['GET','POST'])
def userviewfullreport():
    try:
        id=request.args['id']
        db = firestore.client()
        dbref = db.collection('newreport')
        data = dbref.document(id).get().to_dict()
        print("Report Data ", data)
        return render_template("userviewfullreport.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/newuser', methods=['POST','GET'])
def newuser():
    try:
        msg=""
        print("Add New user page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            file = request.files['file']            
            
            db = firestore.client()
            dbref = db.collection('newuser')
            userdata = dbref.get()
            is_present=False
            for doc in userdata:
                temp=doc.to_dict()                
                if(temp['UserName']==uname or temp['PhoneNumber']==phnum or temp['EmailId']==email):
                    is_present=True
                    break
            if(not is_present):
                encode = base64.b64encode(pwd.encode("utf-8"))
                #print("str-byte : ", encode)
                id = str(round(time.time()))
                file_path = Path(file.filename)
                extension = file_path.suffix
                filename="Resume"+id+extension
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                json = {'id': id,
                        'FirstName': fname, 'LastName': lname,
                        'UserName': uname, 'Password': encode,
                        'EmailId': email, 'PhoneNumber': phnum,
                        'Address': address, 'FileName':filename}
                db = firestore.client()
                newuser_ref = db.collection('newuser')
                newuser_ref.document(id).set(json)
                print("User user Success")
                msg = "New user Inserted Success"
            else:
                msg = "UserName/Emailid/PhoneNumber already exists"
        return render_template("newuser.html", msg=msg)
    except Exception as e:
        return str(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/contact', methods=['POST','GET'])
def contactpage():
    try:
        msg=""
        if request.method == 'POST':
            cname = str(request.form['cname'])# + " " + str(request.form['lname'])
            subject = request.form['subject']
            message = request.form['message']
            email = request.form['email']
            id = str(round(time.time()))
            json = {'id': id,
                    'ContactName': cname, 'Subject': subject,
                    'Message': message,
                    'EmailId': email}
            db = firestore.client()
            newdb_ref = db.collection('newcontact')
            id = json['id']
            newdb_ref.document(id).set(json)
            body = "Thank you for contacting us, " + str(cname) + " We will keep in touch with in 24 Hrs"
            receipients = [email]
            send_email(subject,body,recipients=receipients)
            msg = "New Contact Added Success"
        return render_template("contact.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/adminviewusers', methods=['POST','GET'])
def adminviewusers():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newuser')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Users Data " , data)
        return render_template("adminviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewdoctors', methods=['POST','GET'])
def adminviewdoctors():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newdoctor')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Doctor Data " , data)
        return render_template("adminviewdoctors.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewcontacts', methods=['POST','GET'])
def adminviewcontacts():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newcontact')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Contact Data " , data)
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewreports', methods=['POST','GET'])
def adminviewreports():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newreport')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Report Data " , data)        
        return render_template("adminviewreports.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminmainpage')
def adminmainpage():
    try:
        return render_template("adminmainpage.html")
    except Exception as e:
        return str(e)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.debug = True
    app.run()