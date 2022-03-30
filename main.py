import collections
import json
import sys
from typing import Collection
from binascii import a2b_base64
from chat import make_responese
import cv2
# from simple_facerec import SimpleFacerec
# from simple_facerec import *
from firebase import Firebase
import firebase_admin
# from firebase_admin import credentials, initialize_app, storage, firestore
from firebase_admin import storage as admin_storage, credentials, firestore, initialize_app
import face_recognition
import os
import glob
import flask
import numpy as np
from flask_mail import Mail, Message
from flask import Flask, flash, redirect, request_finished, send_from_directory, session, url_for, render_template, request, Response, stream_with_context
from flask import Flask, redirect, url_for, render_template, request, Response
import firebase_config
from urllib import request as req
from base64 import b64decode
from threading import Thread
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from datetime import datetime
import joblib




# cred = credentials.Certificate("serviceAccountKey.json")
cred = credentials.Certificate("fypars-660c5-firebase-adminsdk-lpst1-222746bb64.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'gs://fypars-660c5.appspot.com/'})


# db.collection('user').add({'name': 'John', 'age': 40})

# principal_db = db.collection("users").document(email_register)
#      principal_db.set({
#             'email': email_register,
#             'password': password_register
#                       })
db = firestore.client()
app = Flask(__name__, static_url_path='', static_folder='static')
s= URLSafeTimedSerializer('Thisisasecret')
app.config['SECRET_KEY'] = 'hardsecretkey'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'kaiyin3014@gmail.com'
# put password for the gmail acount provided above
app.config['MAIL_PASSWORD'] = '301429604'
#you need to put your reall gmail account for testing here
app.config['MAIL_DEFAULT_SENDER'] = 'kaiyin3014@gmail.com'
Flight_ref = db.collection('FlightSchedule')
Seat_ref = db.collection('FlightSeat')
Seat_ref2 = db.collection('ecoseats').document()
signedupUsers = []
compareUsers = []
facename='wow'
mail = Mail(app)


class SimpleFacerec:

    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Resize frame for a faster speed
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        # Load Images
        images_path = glob.glob(os.path.join(images_path, "*.*"))

        print("{} encoding images found.".format(len(images_path)))

        # Store image encoding and names
        for img_path in images_path:
            img = cv2.imread(img_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get the filename only from the initial file path.
            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)
            # Get encoding
            # img_encoding = face_recognition.face_encodings(rgb_img)[0]
            test_encoding = face_recognition.face_encodings(rgb_img)
            if len(test_encoding)>0:
                img_encoding= test_encoding[0]
                self.known_face_encodings.append(img_encoding)
                self.known_face_names.append(filename)
                print("Encoding images loaded")
            else:
                print("error")
            # Store file name and file encoding
        

    def detect_known_faces(self, frame):
        global facename
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            facename = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                facename = self.known_face_names[best_match_index]
                name="Detected"
                # name = "Detected"
            # return redirect(url_for('login'))
            # else
            #     return redirect(url_for('/'))
            face_names.append(name)


       
        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names



def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
    
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # gather all the data
        photo_register = request.form["source"]
        email_register = request.form.get("email_register")
        password_register = request.form.get("password_register")
        phone_register = request.form.get("phone_register")
        name_register = request.form.get("name_register")

        data_uri = photo_register
        # print(data_uri)



        with req.urlopen(data_uri) as response:
            data = response.read()
        with open("images/" + name_register + ".jpeg", "wb") as f:
            f.write(data)
        cloud_path = "images/" + name_register + ".jpeg"
        local_path = "images/" + name_register + ".jpeg"

        firebase_config.storage.child(cloud_path).put(local_path)
        db1 = firebase_config.firebase.database()
        
        insertdata = {
        "name": name_register,
        "phone": phone_register,
        "email": email_register,
        "password":password_register,
        "gender":'',
        "region":'',
        "address":'',
        "dateofbirth":'',
        "nationality":'',
        "alert":''
}
        db.collection("user").document(name_register).set(insertdata)

        data = {
            "name": name_register,
            "phone": phone_register
        }

        db1.child("users").child(email_register.replace(".com", "")).set(data)
        return redirect(url_for("login"))
    else:
        print("Failedgg")
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # print (simple_facerec.__name__)
        # print(compareUsers)
        # print(signedupUsers)
       
         
        # match = next((i for i in compareUsers if i in signedupUsers), None)
        # if match is not None:
        #     # print(match)
        #     return render_template("home.html")
        # else:
        email_signin = request.form.get("email_signin")
        # password_signin = request.form.get("password_signin")

        if email_signin == "":
       
                return render_template("login.html", error="Please fill your username")
        elif  email_signin==facename:
            global login_id
            login_id = email_signin
            getuserID = db.collection('user').document(login_id).get()
            username = getuserID.get('name')
            return render_template("userhome.html", username=username)
        else:
            getuser= db.collection('user').document(email_signin).get() 
            alertstatus = getuser.get('alert')
            print(alertstatus)
            if alertstatus=='On':
                print("sendemail")
                print("Im here weihao")
                getuserEmail = db.collection('user').document(email_signin).get()
                email= getuserEmail.get('email')
                subject="Unauthorized Access"
                msg = Message(subject, recipients=[email])
                msg.body = 'We detected an Unauthorized user is trying to use your username to access your account'
                mail.send(msg)
            elif alertstatus== "" or alertstatus=='Off':
                print("not logged in")
            return render_template("login.html", error="Wrong Username, Please Enter Correct Username")

       
    else:
        return render_template("login.html")

@app.route('/boostap.min.css')

@app.route("/", methods=["POST", "GET"])
def home():
        country = ()
     
        airport_data = db.collection("FlightAirport").get()

        for Flight in airport_data:
            country_list = Flight.get('AirportLocation')

            country = country + (country_list,)
    
   

        return render_template("home.html",  country=country)

@app.route("/userhome", methods=["POST", "GET"])
def userhome():
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
    country = ()
     
    airport_data = db.collection("FlightAirport").get()

    for Flight in airport_data:
            country_list = Flight.get('AirportLocation')

            country = country + (country_list,)

    # if request.method == "POST":
    #      if request.form['submitsignout'] == 'signout':
    #         login_id=""
    #      return render_template("home.html")


    return render_template("userhome.html", username=username, country=country)

@app.route("/staffhome")
def staffhome():
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
    country = ()
     
    airport_data = db.collection("FlightAirport").get()

    for Flight in airport_data:
            country_list = Flight.get('AirportLocation')

            country = country + (country_list,)

    # if request.method == "POST":
    #      if request.form['submitsignout'] == 'signout':
    #         login_id=""
    #      return render_template("home.html")


    return render_template("staffhome.html", username=username, country=country)


@app.route("/purchaseRecord")
def purchaseRecord():
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
    data=()
    data1 = ()

    userRecord = db.collection(u'OrderList').where(u'email', u'==', username).stream()


    for getUser in userRecord:
        # getMovie = db.collection('OrderList').document().get()
        if getUser.get('seatNo0') == 1:
            data = data + ('seat1',)
        if getUser.get('seatNo1') == 1:
            data = data + ('seat2',)
        if getUser.get('seatNo2') == 1:
            data = data + ('seat3',)
        if getUser.get('seatNo3') == 1:
            data = data + ('seat4',)
        if getUser.get('seatNo4') == 1:
            data = data + ('seat5',)
        if getUser.get('seatNo5') == 1:
            data = data + ('seat6',)
        if getUser.get('seatNo7') == 1:
            data = data + ('seat8',)
        if getUser.get('seatNo8') == 1:
            data = data + ('seat9',)
        if getUser.get('seatNo9') == 1:
            data = data + ('seat10',)
        if getUser.get('seatNo10') == 1:
            data = data + ('seat11',)
        if getUser.get('seatNo11') == 1:
            data = data + ('seat12',)
        if getUser.get('seatNo12') == 1:
            data = data + ('seat13',)
        if getUser.get('seatNo13') == 1:
            data = data + ('seat14',)
        if getUser.get('seatNo14') == 1:
            data = data + ('seat15',)
        if getUser.get('seatNo15') == 1:
            data = data + ('seat16',)
        if getUser.get('seatNo16') == 1:
            data = data + ('seat17',)
        if getUser.get('seatNo17') == 1:
            data = data + ('seat18',)
        if getUser.get('seatNo18') == 1:
            data = data + ('seat19',)
        if getUser.get('seatNo19') == 1:
            data = data + ('seat20',)
        if getUser.get('seatNo20') == 1:
            data = data + ('seat21',)
        if getUser.get('seatNo21') == 1:
            data = data + ('seat22',)
        if getUser.get('seatNo22') == 1:
            data = data + ('seat23',)
        if getUser.get('seatNo23') == 1:
            data = data + ('seat24',)
        if getUser.get('seatNo24') == 1:
            data = data + ('seat25',)
        if getUser.get('seatNo25') == 1:
            data = data + ('seat26',)
        if getUser.get('seatNo26') == 1:
            data = data + ('seat27',)
        if getUser.get('seatNo27') == 1:
            data = data + ('seat28',)
        if getUser.get('seatNo28') == 1:
            data = data + ('seat29',)
        if getUser.get('seatNo29') == 1:
            data = data + ('seat30',)
        if getUser.get('seatNo30') == 1:
            data = data + ('seat31',)
        if getUser.get('seatNo31') == 1:
            data = data + ('seat32',)
        if getUser.get('seatNo32') == 1:
            data = data + ('seat33',)
        if getUser.get('seatNo33') == 1:
            data = data + ('seat34',)
        if getUser.get('seatNo34') == 1:
            data = data + ('seat35',)
        if getUser.get('seatNo35') == 1:
            data = data + ('seat36',)
        if getUser.get('seatNo36') == 1:
            data = data + ('seat37',)
        if getUser.get('seatNo37') == 1:
            data = data + ('seat38',)
        if getUser.get('seatNo38') == 1:
            data = data + ('seat39',)
        if getUser.get('seatNo39') == 1:
            data = data + ('seat40',)
        if getUser.get('seatNo40') == 1:
            data = data + ('seat41',)
        if getUser.get('seatNo41') == 1:
            data = data + ('seat42',)
        if getUser.get('seatNo42') == 1:
            data = data + ('seat43',)
        if getUser.get('seatNo43') == 1:
            data = data + ('seat44',)
        if getUser.get('seatNo44') == 1:
            data = data + ('seat45',)
        if getUser.get('seatNo45') == 1:
            data = data + ('seat46',)
        if getUser.get('seatNo46') == 1:
            data = data + ('seat47',)
        if getUser.get('seatNo47') == 1:
            data = data + ('seat48',)
        data1 = data1 + (
            (getUser.get('FlightSeatPrice'), getUser.get('DepartureDate'), getUser.get('ArrivalDate'), getUser.get('location'), getUser.get('destination')),)

  
    
    return render_template("purchaseRecord.html", data1=data1,  username=username, data=data)


@app.route("/profile", methods=["POST", "GET"])
def profile():
    # print(login_id)
    
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
    phone = getuserID.get('phone')
    email = getuserID.get('email')
   
    region = getuserID.get('region')
    address = getuserID.get('address')
    dateofbirth = getuserID.get('dateofbirth')
    nationality = getuserID.get('nationality')
    if request.method == "POST":
        User_name = request.form.get("User_name")
        getemail= request.form.get("inputemail")
        getphone= request.form.get("inputphone")
        getaddress= request.form.get("getaddress")
        getregion= request.form.get("inputregion")
        getnation= request.form.get("inputnationality")
        getbirth= request.form.get("inputbirth")
        if request.form['submit_button'] == 'test1':
           getuserID = db.collection('user').document(login_id).get()
           username = getuserID.get('name')
           phone = getuserID.get('phone')
           email = getuserID.get('email')       
           region = getuserID.get('region')
           address = getuserID.get('address')
           dateofbirth = getuserID.get('dateofbirth')
           nationality = getuserID.get('nationality')
   
           db.collection('user').document(login_id).update({
            "email":getemail,
            "phone":getphone,
            "region":getregion,
            "dateofbirth":getbirth,
            "nationality":getnation,
            "address":getaddress,
            })
           return render_template("profile.html", username=username, phone=phone, email=email, region=region, address=address,dateofbirth=dateofbirth, nationality=nationality)

        elif request.form['submit_button'] == 'test2':
            if User_name==facename:
                global photo_username
                photo_username = User_name
                db.collection('user').document(User_name).delete()
                cloud_path = "images/" + User_name + ".jpeg"
                local_path = "images/" + User_name + ".jpeg"
                bucket = admin_storage.bucket('fypars-660c5.appspot.com')
                blob = bucket.blob(cloud_path)
                blob.delete()
                return render_template("home.html",message='Directing to Reset Face')
            else:
                print("not logged in")
                return 'not logged in'
        elif request.form['submit_button'] == 'test3':
           
           return sendemail()
        elif request.form['submit_button'] == 'test4':
           checked = 'checkvalue' in request.form

           if checked==True:
                db.collection('user').document(login_id).update({
                    "alert":"On"
                })
                print("success")

           elif checked==False:
                db.collection('user').document(login_id).update({
                    "alert":"Off"
                })

           return render_template("profile.html", username=username, phone=phone, email=email, region=region, address=address,dateofbirth=dateofbirth, nationality=nationality)
    else: 
        return render_template("profile.html", username=username, phone=phone, email=email, region=region, address=address,dateofbirth=dateofbirth, nationality=nationality)

@app.route("/videoFeeder")
def gen():
    video = cv2.VideoCapture(0)
    flag = True
    db = firebase_config.firebase.database()
    users = db.child("users").get()
    for user in users.each():
        signedupUsers.append(user.key() + ".com")
    print("Sign up" + str(signedupUsers))
    sfr = SimpleFacerec()
    sfr.load_encoding_images("images")


    while True:
        success, image = video.read()
        face_locations, face_names = sfr.detect_known_faces(image)

        for face_loc, name in zip(face_locations, face_names):
            # print("got here")
            y1, x1, y2, x2 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            image = cv2.putText(image, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            image = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)

            if len(compareUsers) < 20:
                # print("got here")
                compareUsers.append(name)

        ret, jpeg = cv2.imencode('.jpg', image)
       
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        if cv2.waitKey(1) & 0xFF==ord('z'):
                break
     
    video.stop()
    video.release()
    print("got here")
    del cam
    del video
    del(camera)
    cv2.release()
    cv2.destroyAllWindows()

@app.route('/sendemail')
def sendemail():
    getuserEmail = db.collection('user').document(login_id).get()
    email= getuserEmail.get('email')
    subject="Reset FaceID Email Confirmation"
   

    token = s.dumps(email, salt='email-confirm')
    msg = Message(subject, recipients=[email])

    link = url_for('resetface', token=token, _external=True)
    msg.body = 'Your link is {}'.format(link)
    mail.send(msg)

    return redirect(url_for("profile"))

def sendalert():
    getuserEmail = db.collection('user').document(login_id).get()
    email= getuserEmail.get('email')
    subject="Reset FaceID Email Confirmation"
   

    token = s.dumps(email, salt='email-confirm')
    msg = Message(subject, recipients=[email])

    link = url_for('resetface', token=token, _external=True)
    msg.body = 'Your link is {}'.format(link)
    mail.send(msg)

    return redirect(url_for("profile"))


@app.route('/alert', methods=['GET', 'POST'])
def alert():
    getuser= db.collection('user').document(login_id).get()
    username = getuser.get('alert')
    print(username)
    if username=='On':
      print("success")

    else:
      print("Failed")
    # print(request.form.get('checkvalue'))
    if request.method == "POST":
        checked = 'checkvalue' in request.form

        if checked==True:
            db.collection('user').document(login_id).update({
                "alert":"On"
            })
            print("success")

        elif checked==False:
            db.collection('user').document(login_id).update({
                "alert":"Off"
            })

            print("Not Success")
       
      

    return render_template("alert.html")

@app.route('/resetface/<token>', methods=['GET', 'POST'])
def resetface(token):
  
    try:
        getuser= db.collection('user').document(login_id).get()
        username = getuser.get('name')
        email = s.loads(token, salt='email-confirm', max_age=3600)
        print(email)
        print(login_id)
        print("IM HERE EMAIL")

    except SignatureExpired:

         return '<h1>The token is expired!</h1>'

    if request.method == "POST":
            try:
                # gather all the data
                photo_register = request.form["source"]

                data_uri = photo_register
                # print(data_uri)



                with req.urlopen(data_uri) as response:
                    data = response.read()
                with open("images/" + login_id + ".jpeg", "wb") as f:
                    f.write(data)
                cloud_path = "images/" + login_id + ".jpeg"
                local_path = "images/" + login_id + ".jpeg"

                firebase_config.storage.child(cloud_path).put(local_path)
           

                print("Success?")      
                return redirect(url_for("home"))   
            except:
                print("Failedgg")
                return render_template("resetface.html",token=token)    

    return render_template("resetface.html",token=token, username=username)

@app.route('/video_feed')
def video_feed():
    global video
    # print("haha")
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
  
@app.route("/chatbot")
def chatbot():
    return render_template('chatbot.html')

@app.route("/explore")
def explore():
    return render_template('explore.html')

@app.route("/insert_schedule", methods=["POST", "GET"])
def insert_schedule():
    Name1 = ()
    country = ()
    airport_data = db.collection("FlightAirport").get()

    for FlightLocation in airport_data:
        country_list = FlightLocation.get('AirportLocation')
        country = country + (country_list,)

    getFlightselection= db.collection('Flight').get()

    for getFlightID in getFlightselection:
        flightID = getFlightID.get('FlightID')
        Name1 = Name1 + (flightID,)

    session.pop("user", None)
    if request.method == "POST":
        schedule_id = request.form['Schedule ID']
        flight_id = request.form['FlightID']
        from_location = request.form['FromLocation']
        destination = request.form['FlightDestination']
        arrival_time = request.form['FlightArrivalTime']
        departure_time = request.form['FlightDepartureTime']
        arrival_date = request.form['FlightArrivalDate']
        departure_date = request.form['FlightDepartureDate']
        price = request.form['FlightSeatPrice']

        exist_schedule = db.collection('FlightSchedule').document(schedule_id).get()
        if exist_schedule.exists:
            flash("Flight Schedule ID Duplicate , please try again", "info")

        else:
            Flight_ref.document(schedule_id).set({
                'ScheduleID': schedule_id,
                'FlightID': flight_id,
                'FromLocation': from_location,
                'FlightDestination': destination,
                'FlightArrivalDate': arrival_date,
                'FlightDepartureDate': departure_date,
                'FlightArrivalTime': arrival_time,
                'FlightDepartureTime': departure_time,
                'FlightSeatPrice': price,

            })
            flash("Successful insertion of new flights.", "info")

        return render_template('insert_schedule.html', country=country)
    else:
        return render_template('insert_schedule.html', country=country, Name1=Name1)

@app.route("/get")
def predict():
    user_text = request.args.get('msg')
    return make_responese(user_text)

@app.route("/time_table", methods=["POST", "GET"])
def time_table():
    country = ()
    data1 = (

    )

    flight_data = db.collection("FlightSchedule").get()
    airport_data = db.collection("FlightAirport").get()

    for Flight in airport_data:
        country_list = Flight.get('AirportLocation')

        country = country + (country_list,)

    for Flight in flight_data:

        data1 = data1 + ((
                             Flight.get('ScheduleID'), Flight.get('FlightID'), Flight.get('FlightArrivalDate'),
                             Flight.get('FlightArrivalTime'),
                             Flight.get('FlightDepartureDate'), Flight.get('FlightDepartureTime'),
                             Flight.get('FromLocation'), Flight.get('FlightDestination'),
                             Flight.get('FlightSeatPrice')),)

    return render_template("time_table.html", data1=data1, country=country)

@app.route("/test", methods=["POST", "GET"])
def test():
    getuserEmail = db.collection('user').document(login_id).get()
    email = getuserEmail.get('name')
    getFlight = db.collection('FlightSchedule').document(getid).get()
    destination = getFlight.get('FlightDestination')
    location = getFlight.get('FromLocation')
    ArrivalDate = getFlight.get('FlightArrivalDate')
    DepartureDate = getFlight.get('FlightDepartureDate')    
    return render_template('test.html', email=email, getid=getid, destination=destination, location=location, ArrivalDate=ArrivalDate, DepartureDate=DepartureDate)



@app.route('/getSeatid')
def getseatid():
    global getid
    getid = request.args.get('id')
    print(getid)
    return render_template("time_table.html")

@app.route("/flight_management")
def flight_management():
    data1 = (


    )
    flight_data = db.collection("FlightSchedule").get()

    for Flight in flight_data:
        data1 = data1 + ((
                             Flight.get('ScheduleID'), Flight.get('FlightID'), Flight.get('FlightArrivalDate'),
                             Flight.get('FlightArrivalTime'),
                             Flight.get('FlightDepartureDate'), Flight.get('FlightDepartureTime'),
                             Flight.get('FromLocation'), Flight.get('FlightDestination'),
                             Flight.get('FlightSeatPrice')),)

        print(data1)

    return render_template("flight_management.html", data1=data1)

@app.route('/getBook')
def getbook():
    global getbook
    getbook = request.args.get('id')
    getSeat = db.collection('FlightSeat').document(getbook).get()

    db.collection('FlightSeat').document()
    id = getSeat.get('id')
    email = getSeat.get('email')
    getbook = request.args.get('id')
    print(getbook)
    Seat_ref.document(getbook).set({
        'id': id,
        'email': email,
    })

    return render_template("flight_management.html")



@app.route('/submit-form', methods=['POST'])
def submitForm():

    select_value1 = request.form.get('select1')
    select_value2 = request.form.get('select2')
    select_value3 = request.form.get('select3')
    select_value4 = request.form.get('select4')

    data1 = (

    )

    if select_value1 != "" and select_value2 != "":
        fight_search = db.collection(u'FlightSchedule').where(u'FromLocation', u'==', select_value1) \
            .where(u'FlightDestination', u'==', select_value2).stream()
    elif select_value2 != "":
        fight_search = db.collection(u'FlightSchedule').where(u'FlightDestination', u'==', select_value2).stream()
    elif select_value1 != "":
        fight_search = db.collection(u'FlightSchedule').where(u'FromLocation', u'==', select_value1).stream()
    elif select_value2 != "" and select_value4 != "":
        fight_search = db.collection(u'FlightSchedule').where(u'FlightDestination', u'==', select_value2)\
            .where(u'FlightArrivalDate', u'==', select_value4).stream()
    else:
        fight_search = db.collection(u'FlightSchedule').where(u'FromLocation', u'==', select_value1) \
            .where(u'FlightDestination', u'==', select_value2).where(u'FlightDepartureDate', u'==', select_value3) \
            .where(u'FlightArrivalDate', u'==', select_value4).stream()

    for Flist in fight_search:
        data1 = data1 + ((
                             Flist.get('ScheduleID'), Flist.get('FlightID'), Flist.get('FlightArrivalDate'),
                             Flist.get('FlightArrivalTime'),
                             Flist.get('FlightDepartureDate'), Flist.get('FlightDepartureTime'),
                             Flist.get('FromLocation'), Flist.get('FlightDestination'),
                             Flist.get('FlightSeatPrice')),)

    return render_template("Flist.html", data1=data1, select_value2=select_value2, select_value1=select_value1,
                           select_value3=select_value3, select_value4=select_value4)


@app.route('/flight_edit', methods=["POST", "GET"])
def flight_edit():

    get_flight = db.collection('FlightSchedule').document(Tid).get()

    db.collection('FlightSchedule').document()

    flight_id = get_flight.get('FlightID')
    location = get_flight.get('FromLocation')
    destination = get_flight.get('FlightDestination')
    arrival_date = get_flight.get('FlightArrivalDate')
    arrival_time = get_flight.get('FlightArrivalTime')
    departure_date = get_flight.get('FlightDepartureDate')
    departure_time = get_flight.get('FlightDepartureTime')
    price = get_flight.get('FlightSeatPrice')

    if request.method == "POST":
        flight_id = request.form['FlightID']
        location = request.form['FromLocation']
        destination = request.form['FlightDestination']
        arrival_date = request.form['FlightArrivalDate']
        arrival_time = request.form['FlightArrivalTime']
        departure_date = request.form['FlightDepartureDate']
        departure_time = request.form['FlightDepartureTime']
        price = request.form['FlightSeatPrice']

        db.collection('FlightSchedule').document(Tid).update(
            {"flight_id": flight_id, "FromLocation": location, "FlightDestination": destination,
             "FlightArrivalDate": arrival_date, "FlightArrivalTime": arrival_time, "FlightDepartureDate": departure_date,
             "FlightDepartureTime": departure_time, "FlightSeatPrice": price})

    return render_template("flight_edit.html", flight_id=flight_id, location=location,
                           destination=destination, arrival_date=arrival_date, arrival_time=arrival_time,
                           departure_date=departure_date, departure_time=departure_time, price=price, )

@app.route('/home/<seatinfo>', methods=['POST'])
def getseat(seatinfo):
    seatinfo = json.load(seatinfo)
    return 'Info Received'

@app.route('/getTEdit')
def TgetEdit():
    global Tid
    Tid = request.args.get('id')

    return render_template("flight_edit.html.html")


@app.route("/getdelete")
def delete():
    user_text1 = request.args.get('id')

    db.collection('FlightSchedule').document(user_text1).delete()
    print(user_text1)

    return render_template("flight_management.html")

@app.route("/getTdelete")
def Tdelete():
    user_text1 = request.args.get('id')
    db.collection('FlightSchedule').document(user_text1).delete()
    db.collection('SeatList').document(user_text1).delete()

    print(user_text1)

    return render_template("flight_management.html")


@app.route("/addflight", methods=["POST", "GET"])
def addflight():
    if request.method == "POST":

        # gather all the data
        photo_register = request.files["flightphoto"]
        flightCapa = request.form.get("flightCapa")
        flightID = request.form.get("name_register")

        # print(data_uri)


        cloud_path = "flight/" + flightID + ".jpeg"
        local_path = "flight/" + flightID + ".jpeg"

        firebase_config.storage.child(cloud_path).put(photo_register)
        db1 = firebase_config.firebase.database()
        
        insertdata = {
        "FlightID": flightID,
        "FlightCapacity": flightCapa,

}
        db.collection("Flight").document().set(insertdata)

    
        return redirect(url_for("staffhome"))
    else:
        print("Failedgg")
        return render_template("addflight.html")



@app.route("/displayflight")
def displayflight():
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
    data1 = ()

    flightRecord = db.collection('Flight').get()
 
    for getFlight in flightRecord:
   
        data1 = data1 + (
            (getFlight.get('FlightID'), getFlight.get('FlightCapacity')),)

  
    
    return render_template("displayflight.html", data1=data1,  username=username)


@app.route("/deleteflight")
def deleteflight():
    getuserID = db.collection('user').document(login_id).get()
    username = getuserID.get('name')
   
    deleteid = request.args.get('id')
    print(deleteid)
    # flightRecord = db.collection('Flight').document(deleteid).delete()
    userRecord = db.collection(u'Flight').where(u'FlightID', u'==', deleteid).stream()
    for doc in userRecord:
        doc.reference.delete()




  
    
    return render_template("displayflight.html", username=username)



@app.route("/editflight", methods=["POST", "GET"])
def editflight():

    editid = request.args.get('id')
    getflight = db.collection('Flight').where(u'FlightID', u'==', editid).stream()
    for doc in getflight:
         global getflightid
         getflightid = doc.get('FlightID')  

    if request.method == "POST":
        updateFlightID= request.form.get("name_register")
        results= db.collection('Flight').where(u'FlightID', u'==', getflightid).get()
        for item in results:
                doc=db.collection('Flight').document(item.id)
                doc.update({
                    "FlightID":updateFlightID
                })
                return redirect(url_for("displayflight"))
       

    return render_template("editflight.html", flightID=getflightid)

@app.route("/buy_ticket", methods=["POST", "GET"])
def buy_ticket():
    getuserEmail = db.collection('user').document(login_id).get()
    gemail = getuserEmail.get('name')
    getFlight = db.collection('FlightSchedule').document(getid).get()
    destination = getFlight.get('FlightDestination')
    location = getFlight.get('FromLocation')
    FlightID = getFlight.get('FlightID')
    ArrivalDate = getFlight.get('FlightArrivalDate')
    DepartureDate = getFlight.get('FlightDepartureDate')
    price = getFlight.get('FlightSeatPrice')

    if request.method == "POST":
        seat = request.form['pn']

        Seat_ref2.set({
            'FlightSeatPrice': price,
            'seat': seat,
            'email': gemail,

        })

    return render_template('buy_ticket.html', email=gemail, getid=getid, destination=destination,
                           location=location, FlightID=FlightID, ArrivalDate=ArrivalDate, DepartureDate=DepartureDate,
                           price=price)


if __name__ == "__main__":
    app.debug = True


    app.run()

  
