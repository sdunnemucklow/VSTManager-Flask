# Original work Copyright (c) 2017 Samuel Dunne-Mucklow

from flask import Flask, redirect, render_template, request, g
from multiprocessing import Queue
import jinja2.ext
import os, shutil, zipfile, urllib.request, csv, io
import MyCSV
app = Flask(__name__)

@app.before_first_request
def before_first_request():
    Initialize()

def _urlExists(url):
    req = urllib.request.Request(url, method='HEAD')
    try:
        urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError:
        return False
                           
@app.route('/')
def _index():
    return redirect('/local', code=302)
                           
@app.route('/local', methods=['GET','POST'])
def _local():
    global LocalPath

    if request.method == 'POST':
        LocalPath = request.form["locationTextBox"]
        if LocalPath.endswith(os.path.sep):
            LocalPath = LocalPath[:-1]
        MyCSV.AddRow("locations.csv", [LocalPath])
    
        # if path is new, create folder
        if not os.path.exists(LocalPath):
            os.mkdir(LocalPath)

    localVstList = []
    if LocalPath:
        localCsvPath = os.path.join(LocalPath,"local.csv")
        if os.path.exists(localCsvPath):
            localVstList = MyCSV.ReadToList(localCsvPath)
        else:
            file = open(localCsvPath, 'w')
            file.close()
        
    return render_template('local.html',
                           localPath=LocalPath,
                           vstList=localVstList)
                           
@app.route('/local/install/<index>')
def _localInstall(index):
    global LocalPath
    if not LocalPath:
        print("Please select an install path first!")
        return redirect('/local', code=302)
    index = int(index)
    localVstList = MyCSV.ReadToList(os.path.join(LocalPath,"local.csv"))
    result = DownloadAndExtract(localVstList[index][2], localVstList[index][3])
    MyCSV.AddRow(os.path.join(LocalPath,"local.csv"), localVstList[index]) # note row will normally already exist
    return redirect('/local', code=302)

@app.route('/local/uninstall/<index>')
def _localUninstall(index):
    global LocalPath
    if not LocalPath:
        print("Please select an install path first!")
        return redirect('/local', code=302)
    index = int(index)
    localVstList = MyCSV.ReadToList(os.path.join(LocalPath,"local.csv"))
    shutil.rmtree(os.path.join(LocalPath,localVstList[index][2]))
    MyCSV.DeleteRow(os.path.join(LocalPath,"local.csv"), localVstList[index])
    return redirect('/local', code=302)
    
@app.route('/store', methods=['GET','POST'])
def _store():
    global StoreUrl
    storeVstList = []
    if StoreUrl:
        storeVstList = MyCSV.ReadToList('store.csv')[1:]    # ignore header row
        
    # if post request or store already selected, populate vstList
    if request.method == 'POST':
        StoreUrl = request.form["storeTextBox"]
        
        if len(StoreUrl) < 7 or StoreUrl[:4] != "http":
            StoreUrl = "http://" + StoreUrl
        if not StoreUrl.endswith("/"):
            StoreUrl = StoreUrl + "/"
    
        if os.path.exists("store.csv"):
            os.remove("store.csv")
    
        try:
            data = urllib.request.urlretrieve(StoreUrl + "store.csv", "store.csv")
            storeVstList = MyCSV.ReadToList('store.csv')[1:]    # ignore header row
        except:
            print(StoreUrl + " is not a valid store.")
        
        MyCSV.AddRow("past_stores.csv", [StoreUrl])

    return render_template('store.html',
                           storeUrl=StoreUrl,
                           vstList=storeVstList)
                           
@app.route('/store/install/<index>')
def _storeInstall(index):
    global LocalPath
    if not LocalPath:
        print("Please select an install path first!")
        return redirect('/store', code=302)
    storeVstList = MyCSV.ReadToList('store.csv')[1:]    # ignore header row
    index = int(index)
    success = DownloadAndExtract(storeVstList[index][2], storeVstList[index][3])
    MyCSV.AddRow(os.path.join(LocalPath,"local.csv"), storeVstList[index])
    return redirect('/store', code=302)

def Initialize():
    # initialize the app
    if not os.path.exists("past_stores.csv"):
        file = open("past_stores.csv", 'w')
        file.close()
    if not os.path.exists("locations.csv"):
        file = open("locations.csv", 'w')
        file.close()
        
    storesList = MyCSV.ReadToList("past_stores.csv")
    # populate the web page stores list using storesList
    locationList = MyCSV.ReadToList("locations.csv")
    # populate the web page locations list using locationList
    
    for s in locationList:
        if not os.path.exists(os.path.join(s[0],"local.csv")):
            file = open(os.path.join(s[0],"local.csv"), 'w')
            file.close()
    
    # global variables
    global StoreUrl
    StoreUrl = ''
    global LocalPath
    LocalPath = None
                           
def DownloadAndExtract(fileName, downloadUrl):
    global LocalPath
    success = True

    if os.path.exists(os.path.join(LocalPath,fileName + ".zip")):
        os.remove(os.path.join(LocalPath,fileName + ".zip"))
    
    try:
        data = urllib.request.urlretrieve(downloadUrl, os.path.join(LocalPath,fileName + ".zip"))
    except:
        return False
        
    if os.path.exists(os.path.join(LocalPath,fileName)):
        os.rename(os.path.join(LocalPath,fileName), os.path.join(LocalPath,fileName + "_old"))
    
    try:
        zipFile = zipfile.ZipFile(os.path.join(LocalPath,fileName + ".zip"))
        zipFile.extractall(path=LocalPath)
        zipFile.close()
    except:
        success = False
        
    if os.path.exists(os.path.join(LocalPath,fileName + ".zip")):
        os.remove(os.path.join(LocalPath,fileName + ".zip"))
    if os.path.exists(os.path.join(LocalPath,fileName + "_old")):
        shutil.rmtree(os.path.join(LocalPath,fileName + "_old"))

    return success
    
if __name__ == "__main__":
    app.run(debug=True)
