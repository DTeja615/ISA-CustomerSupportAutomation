# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:59:28 2020

@author: Lakshmi Subramanian
"""


from __future__ import print_function
from flask import Flask, request, make_response, jsonify
from requests import Session
from google.cloud import vision
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import requests
import pandas as pd
import os
import io
from google.cloud import vision
from google.cloud.vision import types
import tagui as t

client = vision.ImageAnnotatorClient.from_service_account_json("lak_cred.json")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

app = Flask(__name__)

# **********************
# UTIL FUNCTIONS : START
# **********************

def gdriveValues():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(q="name contains 'Please upload image here' and mimeType = 'application/vnd.google-apps.folder'",
        pageSize=10, fields="nextPageToken, files(id, name, modifiedTime)").execute()
    items = results.get('files', [])
    
    fileresults = service.files().list(q="'" + results['files'][0]['id'] + "' in parents",
        pageSize=10, fields="nextPageToken, files(id, name, modifiedTime)").execute()
    
    df = pd.DataFrame(fileresults['files']).sort_values(by=['modifiedTime'], ascending=False)
    
    return df.head(1)['id'].values[0],df.head(1)['name'].values[0]
    


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


def text_detection(image):
    """Detects text in the file."""
    from google.cloud import vision

    with io.open(image, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    finImage = ""
    nameImage = ""
    dobImage = ""
    if format(response).startswith("error") == False:
        texts = response.text_annotations
        ocrOut = format(texts[0].description)
        
        for i in range(len(ocrOut.split("\n"))):
            if ocrOut.split("\n")[i].startswith("FIN"):
                if len(ocrOut.split("\n")[i])<4:
                    finImage = ocrOut.split("\n")[i+1]
                else:
                    finImage = ocrOut.split("\n")[i].split(" ")[1]
        print(finImage)
        
        for i in range(len(ocrOut.split("\n"))):
            if ocrOut.split("\n")[i].startswith("Name"):
               nameImage = ocrOut.split("\n")[i+1]
        print(nameImage)
        
        for i in range(len(ocrOut.split("\n"))):
            if ocrOut.split("\n")[i].startswith("Sex"):
               dobImage = ocrOut.split("\n")[i+1]
        print(dobImage)

    return finImage,nameImage,dobImage


def verificationFromDB(accNum):
    pcodeActual = ""
    finActual = ""
    try:
        t.init()
        t.url('http://localhost:5050/index.html')
        #t.url('file:///D:/Intelligent%20Systems/Intelligent%20Software%20Agents/Project/Project%203A/accountnumber.html')
        t.type('//*[@id="accnum"]', accNum)
        t.click('//*[@id="btnSubmit"]')
        selector1 = """//*[@id="fourdigits"]"""
        pcodeActual = t.read(selector1)
        selector2 = """//*[@id="finnum"]"""
        finActual = t.read(selector2)
        t.close()
    finally:
        t.close()
    return pcodeActual,finActual

def updateDB(accNum,updateField,updateValue):
    try:
        print("update process initiated")
        t.init()
        t.url('http://localhost:5050/index.html')
        t.type('//*[@id="accnum"]', accNum)
        t.click('//*[@id="btnSubmit"]')
        value = "[clear]"+updateValue
        if updateField == "fname":
            t.type('//*[@id="fname"]',value)
        elif updateField == "add":
            t.type('//*[@id="add"]',value)
        elif updateField == "phn":
            t.type('//*[@id="phn"]',value)
        else:
            resp = "Nothing to update"      
        print("update done")
        t.click('//*[@id="btnsubmit"]')
        t.close()
        resp = "Updated Successfully"
    finally:
        t.close()
        
    return resp

# **********************
# UTIL FUNCTIONS : END
# **********************

# *****************************
# Intent Handlers funcs : START
# *****************************

def getLastIntentHandler(wparams):
    
    print("intent handling started")
    print(wparams)
    accNum = wparams['accNum']
    updateField = wparams['updatefield']
    updateValue = wparams['updateValue']
    pcode = wparams['pcode']
    

    file_id,destination = gdriveValues()
    download_file_from_google_drive(file_id, destination)
    print("file downloaded to local")
    finImage,nameImage,dobImage = text_detection(destination)
    print("text detection on image handled")

    pcodeActual,finActual = verificationFromDB(accNum)
    print("verification started")
    print( finActual,finImage,pcodeActual,pcode)
    if finActual == finImage  and pcodeActual == pcode:
        if updateField in ['address']:
            resp = updateDB(accNum,'add',updateValue)
        elif updateField in ['dob']:
            resp = updateDB(accNum,'dob',updateValue)
        elif updateField in ['phone number']:
            resp = updateDB(accNum,'phn',updateValue)        
        elif updateField in ['name']:
            resp = updateDB(accNum,'phn',updateValue)
        else:
            resp = "Sorry couldn't update"
            print(resp)
    else:
         resp = "Sorry couldn't update! Records don't match"
         print(resp)
    return resp


# ***************************
# Intent Handlers funcs : END
# ***************************


# *****************************
# WEBHOOK MAIN ENDPOINT : START
# *****************************
@app.route('/', methods=['POST'])
def main():
    req = request.get_json(silent=True, force=True)
    intent_name = req["queryResult"]["intent"]["displayName"]
    print(intent_name)
    if intent_name == "getImage":
        wparams = req["queryResult"]["outputContexts"][len(req["queryResult"]["outputContexts"])-2]["parameters"]
        resp_text = getLastIntentHandler(wparams)
    else:
        resp_text = "Unable to find a matching intent. Try again."

    resp = {
        "fulfillmentText": resp_text
    }
    return make_response(jsonify(resp))


# ***************************
# WEBHOOK MAIN ENDPOINT : END
# ***************************

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
