from flask import Flask, request, render_template, redirect, session, url_for
from recommendation import recommend
import pymysql

app = Flask(__name__)
app.secret_key = 'KDDRYDRLFYKD4ENE5M'  
@app.route('/')
def index():
    
    category = request.args.get('category')
    #用來取得網址中的查詢參數

    # !!! 4個密碼要改 !!!
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
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
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            WHERE novel.Category = %s
        """, (category,))
    else:
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName
            FROM novel
            LEFT JOIN author ON novel.aIndex = author.aIndex
        """)

    novel = cursor.fetchall()
    username = session.get('username')
    conn.close()
    return render_template("index.html", novel=novel, category=category, categories=categories, username=username)


# 註冊register 登入login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='12345678',
            database='mojoin',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE Account=%s AND Password=%s", (username, password))
        user = cursor.fetchone() #取出一筆資料
        conn.close()
        
        if user:
            #print('username=', username , 'password=', password , 'user=', user)
            #return render_template("login.html", error="登入成功")
            session['username'] = username
            return redirect(url_for('index'))
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
            password='12345678',
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

@app.route('/profile')
def profile():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    cursor.execute("SELECT LoveRecord FROM userlove WHERE Account = %s", (username,))
    loverecords = cursor.fetchall()

    if not loverecords:
        return render_template('profile.html', username=username, novels=[])

    record_ids = tuple(record['LoveRecord'] for record in loverecords)

    if len(record_ids) == 1:
        query = """
            SELECT novel.*, author.Name AS AuthorName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            WHERE nIndex = %s
        """
        cursor.execute(query, (record_ids[0],))
    else:
        placeholders = ', '.join(['%s'] * len(record_ids))
        query = f"""
            SELECT novel.*, author.Name AS AuthorName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            WHERE nIndex IN ({placeholders})
        """
        cursor.execute(query, record_ids)

    novels = cursor.fetchall()
    recommended_titles = recommend(username)

    cursor.close()
    conn.close()

    return render_template('profile.html', username=username, novels=novels, recommended=recommended_titles)


@app.route('/logout')
def logout():
    session.pop('username', None)  # 清空 session 中的 username
    return redirect(url_for('index'))  # 回到首頁

@app.route('/novel')
def novel():
    nIndex = request.args.get('nIndex')
    if not nIndex:
        return "", 400

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    query = """
        SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
        FROM novel
        JOIN author ON novel.aIndex = author.aIndex
        JOIN publish ON novel.pIndex = publish.pIndex
        WHERE nIndex = %s
    """
    cursor.execute(query, (nIndex,))
    novel = cursor.fetchone()

    cursor.close()
    conn.close()

    if not novel:
        return "找不到這本小說", 404

    return render_template('novel.html', novel=novel)

@app.route('/author')
def author():
    session.pop('username', None)  # 清空 session 中的 username
    return redirect(url_for('index'))  # 回到首頁

if __name__ == '__main__':
    app.run(debug=True)