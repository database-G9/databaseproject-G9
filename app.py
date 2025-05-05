from flask import Flask, request, render_template
import pymysql

app = Flask(__name__)

@app.route('/')
def index():
    
    category = request.args.get('category')
    #用來取得網址中的查詢參數

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
        cursor.execute("SELECT * FROM novel WHERE Category = %s", (category,))
    else:
        cursor.execute("SELECT * FROM novel")

    novel = cursor.fetchall()
    conn.close()
    return render_template("index.html", novel=novel, category=category, categories=categories)


if __name__ == '__main__':
    app.run(debug=True)