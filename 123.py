import pymysql
import traceback
#import charts

print("📡 正在嘗試連線資料庫...")

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='12345678',
        database='mojoin',
       # port='3306',
    )


    print("✅ 成功連線")
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    for t in cursor:
        print("📚 找到資料表：", t)
    conn.close()
except Exception as e:
    print("❌ 發生錯誤：")
    print(traceback.format_exc())
