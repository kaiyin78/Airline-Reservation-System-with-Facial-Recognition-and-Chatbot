import pyrebase


firebaseConfig = {
  'apiKey': "AIzaSyAbBYgZUyVfdw-9Jyx7IREo1Wv82em_Hu4",
  'authDomain': "fypars-660c5.firebaseapp.com",
  'projectId': "fypars-660c5",
  'storageBucket': "fypars-660c5.appspot.com",
  'messagingSenderId': "810959590520",
  'appId': "1:810959590520:web:0dbad49b86bf784e3d898d",
  'databaseURL': "https://fypars-660c5-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()



