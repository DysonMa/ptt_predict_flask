# flask
from flask import Flask
from flask import request, render_template, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user




# sqlite
import sqlite3 as DB

#定義資料庫位置
sqlite_path = 'ptt.db'


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

# 設定密碼
import os
secret_key = os.urandom(16).hex()

app = Flask(__name__)
app.secret_key = secret_key

#初始化Flask-Login
login_manager = LoginManager()

#將flask與flask-login綁定
login_manager.init_app(app)

#預設是'basic'，這行可寫可不寫
# login_manager.session_protection = "strong"

#當未登入的使用者請求了一個需要權限的網頁時，就將他送到代表login()的位址去，login()是函式
login_manager.login_view = 'login'

#當未登入的使用者被送到login_view所指定的位址時，會一併跳出的訊息
login_manager.login_message = '請輸入帳號密碼已登入'

#繼承Flask-login裏頭的UserMixin
class User(UserMixin):
    pass

#驗證使用者是否存在在合法清單內
@login_manager.user_loader
def user_loader(loginUser):
    if loginUser not in users:
        return

    user = User()
    user.id = loginUser
    return user

#驗證使用者的密碼是否正確
@login_manager.request_loader
def request_loader(request):
    loginUser = request.form.get('user_id')
    if loginUser not in users:
        return

    user = User()
    user.id = loginUser

    # user.is_authenticated = (request.form['password'] == users[loginUser]['password'])

    return user

#建立一個使用者清單
users = {'Madi': {'password': '0914'}}


# 一定要有GET
@app.route('/',methods=['GET','POST'])
@login_required #指定該頁面一定要登入才能查看
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
        
#登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    loginUser = request.form['user_id']
    if (loginUser in users) and (request.form['password'] == users[loginUser]['password']):
        user = User()
        user.id = loginUser
        login_user(user)
        flash(f'{loginUser}！歡迎登入！')
        return redirect(url_for('home'))

    flash('登入失敗了...')
    return render_template('login.html')

#登出
@app.route('/logout')
def logout():
    loginUser = current_user.get_id()
    logout_user()
    flash(f'{loginUser}！歡迎下次再來！')
    return render_template('login.html')


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






