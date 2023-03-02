from flask import Flask

app = Flask(__name__)

@app.route('/')
def connect_to_db():
    a=3
    b=5
    c=a+b
    return "Hi"






