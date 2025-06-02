from flask import Flask, request, render_template, redirect, session, url_for
from recommendation import recommend, bookrecommend
import pymysql

app = Flask(__name__)
app.secret_key = 'KDDRYDRLFYKD4ENE5M'  
@app.route('/')
def index():
    
    category = request.args.get('category')
    author = request.args.get('author')
    publisher = request.args.get('publisher')
    state = request.args.get('state')
    tag = request.args.get('tag')
    #用來取得網址中的查詢參數
    q = request.args.get('q')  # 新增搜尋參數
    

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
    keyword = None

    # 依據分類撈資料+撈書籍資料需要的表單
    if q:
    #上方搜尋欄
        keyword = f"%{q}%"
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE novel.Title LIKE %s OR author.Name LIKE %s OR publish.Name LIKE %s
        """, (keyword, keyword, keyword))
        keyword = f"{q}"
    elif author:
    #搜尋同作者
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE author.Name = %s
        """, (author,))
    elif category:
    #搜尋同分類
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE novel.Category = %s
        """, (category,))
    elif publisher:
    #搜尋同出版社
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE publish.Name = %s
        """, (publisher,))
    elif state:
    #搜尋同狀態
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE State = %s
        """, (state,))
    elif tag:
    #搜尋同狀態
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            JOIN noveltag nt ON nt.nIndex = novel.nIndex
            JOIN tag t ON t.tIndex = nt.tIndex
            JOIN author ON novel.aIndex = author.aIndex
            JOIN publish ON novel.pIndex = publish.pIndex
            WHERE t.tIndex = nt.tIndex AND nt.nIndex = novel.nIndex AND t.Tag = %s
        """, (tag,))
    else:
    #顯示全部
        cursor.execute("""
            SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
            FROM novel
            LEFT JOIN author ON novel.aIndex = author.aIndex
            LEFT JOIN publish ON novel.pIndex = publish.pIndex
        """)

    novel = cursor.fetchall()

    username = session.get('username')
    is_loved = set()
    if username:
        cursor.execute("SELECT LoveRecord FROM userlove WHERE Account = %s", (username,))
        is_loved = {row['LoveRecord'] for row in cursor.fetchall()}
    
    conn.close()
    return render_template("index.html", novel=novel, category=category, categories=categories, author=author, publisher=publisher, username=username, is_loved=is_loved, keyword=keyword, state=state, tag=tag)

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
        #搜尋是否有和使用者輸入之相同的帳密
        cursor.execute("SELECT * FROM user WHERE Account=%s AND Password=%s", (username, password))
        user = cursor.fetchone() #取出一筆資料
        conn.close()
        
        if user:
            #print('username=', username , 'password=', password , 'user=', user)
            #return render_template("login.html", error="登入成功")
            #已登入 儲存使用者名稱 返回index
            session['username'] = username
            return redirect(url_for('index'))
        else:
            #print('username=', username , 'password=', password , 'user=', user)
            #登入失敗 顯示錯誤訊息
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
            # 將新的使用者帳密寫入資料庫
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
    
    
    #根據使用者名稱搜尋使用者蒐藏之書籍
    cursor.execute("SELECT LoveRecord FROM userlove WHERE Account = %s", (username,))
    loverecords = cursor.fetchall()

    if not loverecords:
        return render_template('profile.html', username=username, novels=[])

    record_ids = tuple(record['LoveRecord'] for record in loverecords)

    #根據使用者收藏書籍 搜書籍資料
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

    #根據演算法 獲得推薦書籍資料
    recommended_titles = recommend(username)

    is_loved = set()
    if username:
        #搜使用者是否蒐藏該書籍(愛心之顯示)
        cursor.execute("SELECT LoveRecord FROM userlove WHERE Account = %s", (username,))
        is_loved = {row['LoveRecord'] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return render_template('profile.html', username=username, novels=novels, recommended=recommended_titles, is_loved=is_loved)

@app.route('/logout')
def logout():
    #清空儲存的使用者名稱=登出
    session.pop('username', None)  # 清空 session 中的 username
    return redirect(url_for('index'))  # 回到首頁

@app.route('/novel')
def novel():
    username = session.get('username')
    
    #獲取點擊的書之nIndex
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

    #根據nIndex搜該書的書籍資訊(不含tags)
    query = """
        SELECT novel.*, author.Name AS AuthorName, publish.Name AS PublishName
        FROM novel
        JOIN author ON novel.aIndex = author.aIndex
        JOIN publish ON novel.pIndex = publish.pIndex
        WHERE nIndex = %s
    """
    cursor.execute(query, (nIndex,))
    novel = cursor.fetchone()
    if novel and 'Introduction' in novel:
        novel['Introduction'] = novel['Introduction'].replace('\r\n', '\n').replace('\r', '\n')

    #根據nIndex搜該書的書籍資訊(tags)
    query2 = """ 
        SELECT t.Tag
        FROM noveltag nt
        JOIN tag t ON nt.tIndex = t.tIndex
        WHERE nt.nIndex = %s AND nt.tIndex < 500
        ORDER BY t.tIndex;
    """
    cursor.execute(query2, (nIndex,))
    tags = cursor.fetchall()

    recommended_titles = recommend(username)
    

    #搜使用者是否蒐藏該書籍(愛心之顯示)
    is_loved = set()
    if username:
        #搜使用者是否蒐藏該書籍(愛心之顯示)
        cursor.execute("SELECT LoveRecord FROM userlove WHERE Account = %s", (username,))
        is_loved = {row['LoveRecord'] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    if not novel:
        return "找不到這本小說", 404

    return render_template('novel.html', novel=novel, username=username , is_loved=is_loved, tags=tags, recommended=recommended_titles)

@app.route('/addlove/<int:nIndex>')
def addlove(nIndex):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin'
    )
    cursor = conn.cursor()

    #搜使用者是否蒐藏該書籍(愛心之顯示)
    cursor.execute("SELECT * FROM userlove WHERE Account = %s AND LoveRecord = %s", (username, nIndex))
    exists = cursor.fetchone()

    if exists:
        # 如果已經收藏 -> 取消收藏
        cursor.execute("DELETE FROM userlove WHERE Account = %s AND LoveRecord = %s", (username, nIndex))
    else:
        # 沒有收藏 -> 加入收藏
        cursor.execute("INSERT INTO userlove (Account, LoveRecord) VALUES (%s, %s)", (username, nIndex))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(request.referrer or url_for('index'))

@app.route('/read/<int:nid>')
def read_book(nid):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # 未登入導向登入頁

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # 先檢查是否有這筆資料，沒有就插入
    cursor.execute("""
        SELECT * FROM `read` WHERE Account = %s AND nIndex = %s
    """, (username, nid))
    row = cursor.fetchone()

    if row:
        # 若有紀錄則更新 History + 1
        cursor.execute("""
            UPDATE `read` SET History = History + 1 WHERE Account = %s AND nIndex = %s
        """, (username, nid))
    else:
        # 若無則插入新的資料
        cursor.execute("""
            INSERT INTO `read` (Account, nIndex, History) VALUES (%s, %s, 1)
        """, (username, nid))

    conn.commit()
    conn.close()

    # 取得該小說的真正閱讀連結 (例如 novel.Link)
    next_url = request.args.get('next')
    return redirect(next_url)


if __name__ == '__main__':
    app.run(debug=True)