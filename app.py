from flask import Flask, request, render_template, redirect, session
import pymysql

app = Flask(__name__)

@app.route('/')
def index():
    
    category = request.args.get('category')
    #用來取得網址中的查詢參數

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='J19940214k?',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = conn.cursor()  # 讓資料是 dict 格式
    #cursor.execute("SELECT * FROM novel")  # 讀取表單所有資料

    # 取得所有不同的分類
    cursor.execute("SELECT DISTINCT Category FROM novel")
    categories = [row['Category'] for row in cursor.fetchall()]

    # 依據分類撈資料
    if category:
        cursor.execute("SELECT * FROM novel WHERE Category = %s", (category,))
    else:
        cursor.execute("SELECT * FROM novel")

    novel = cursor.fetchall()
    conn.close()
    return render_template("index.html", novel=novel, category=category, categories=categories)


# 註冊register 登入login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='J19940214k?',
            database='mojoin',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE Account=%s AND Password=%s", (username, password))
        user = cursor.fetchone() #取出一筆資料
        conn.close()
        
        if user:
            #print('username=', username , 'password=', password , 'user=', user)
            return render_template("login.html", error="登入成功")
        else:
            #print('username=', username , 'password=', password , 'user=', user)
            return render_template("login.html", error="帳號或密碼錯誤")
    
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 確認密碼一致
        if password != confirm_password:
            message = "密碼與確認密碼不一致，請重新輸入。"
            return render_template("register.html", message=message)

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='J19940214k?',
            database='mojoin',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        # 檢查帳號是否已存在
        cursor.execute("SELECT * FROM user WHERE Account = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            message = "帳號已存在，請使用其他帳號。"
        else:
            # 寫入資料庫
            cursor.execute("INSERT INTO user (Account, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            message = "註冊成功！"

        conn.close()

    return render_template("register.html", message=message)

if __name__ == '__main__':
    app.run(debug=True)