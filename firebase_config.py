import pyrebase


firebaseConfig = {
  'apiKey': "*",
  'authDomain': "*",
  'projectId': "*",
  'storageBucket': "*",
  'messagingSenderId': "*",
  'appId': "*",
  'databaseURL': "*"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()



