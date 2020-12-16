# flask
from flask import Flask
from flask import render_template
from flask import request

# sqlite
import sqlite3 as DB

#定義資料庫位置
sqlite_path = 'D:\ptt.db'


def queryData(sqlite_path,webName):
    [conndb,curr] = get_DB(sqlite_path)
    try:
        results = curr.execute("SELECT * FROM {} ORDER BY Date DESC;".format(webName))
    except DB.OperationalError:
        return 'No Such Table'
    return results

def queryBoardName(sqlite_path):
    [conndb,curr] = get_DB(sqlite_path)
    boardList = []
    try:
        results = curr.execute("SELECT name FROM sqlite_master")
        for row in results:
            boardList.append(row[0])
    except DB.OperationalError:
        return 'No Tables'
    return boardList

#定義資料庫位置
def get_DB(DB_path):
    conndb = DB.connect(DB_path) # 若有則讀取，沒有則建立
    curr = conndb.cursor()  
    return [conndb,curr]


app = Flask(__name__)

# 一定要有GET
@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'GET':
        boardName = queryBoardName(sqlite_path)
        return render_template('view.html', boardName=boardName)

    elif request.method == 'POST':
        webName = request.form.get('webName')
        boardName = queryBoardName(sqlite_path)
        datas = queryData(sqlite_path,webName)
        if datas != 'No Such Table':
            return render_template('view.html', datas=datas, webName=webName, boardName=boardName)
        # else:
        #     datas = []
        #     return render_template('view.html', datas=datas, webName='No Such Table')
        

# 一定要有GET
# @app.route('/queryResults',methods=['GET','POST'])
# def data():



# 運行flask

# <code>$ set FLASK_APP=main.py
# $ flask run --reload --debugger --host 0.0.0.0 --port 8080

# <li>–reload # 修改 py 檔後，Flask server 會自動 reload
# <li>–debugger # 如果有錯誤，會在頁面上顯示是哪一行錯誤
# <li>–host # 可以指定允許訪問的主機IP，0.0.0.0 為所有主機的意思
# <li>–port # 自訂網路埠號的參數

# css reload problems -> 在chrome上 按下 ctrl + shift + R






