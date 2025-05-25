import pymysql
from collections import Counter
from difflib import get_close_matches
import heapq

# 可自定義分類的 tags
SCI_FI_TAGS = ["奇幻", "科幻"]
ROMANCE_TAGS = ["愛情", "戀愛"]

def classify_genre(tag_list):
    score = {"sci-fi": 0, "romance": 0}
    for tag in tag_list:
        if tag in SCI_FI_TAGS:
            score["sci-fi"] += 1
        if tag in ROMANCE_TAGS:
            score["romance"] += 1
    if score["sci-fi"] > score["romance"]:
        return "sci-fi"
    elif score["romance"] > score["sci-fi"]:
        return "romance"
    else:
        return "romance"  # 平手時預設為 romance（可改）

def analyze_user_preference(tags):
    # `tags` 是一個 list，裡面每個元素是 tag list，例如 [['科幻', '機器人'], ['戀愛'], ['太空', '純愛']]
    genres = [classify_genre(tag_list) for tag_list in tags]
    genre_count = Counter(genres)
    total = sum(genre_count.values())
    sci_fi_count = round(10 * (genre_count["sci-fi"] / total)) if total else 3
    romance_count = 10 - sci_fi_count
    return {"sci-fi": sci_fi_count, "romance": romance_count}

def recommend(user):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT Account, GROUP_CONCAT(LoveRecord) AS LoveRecords
                       FROM userlove
                       WHERE Account = %s
                       GROUP BY Account
                       """, (user,))

        records = cursor.fetchone()
        if not records or not records['LoveRecords']:
            print('⚠️找不到使用者紀錄')
            return

        novel_ids = [int(i.strip()) for i in records['LoveRecords'].split(',')]

        tags = []
        for id in novel_ids:
            cursor.execute("""
                           SELECT NT.nIndex, GROUP_CONCAT(T.Tag ORDER BY T.Tag SEPARATOR ', ') AS tags
                           FROM noveltag NT,
                                tag T
                           WHERE NT.nIndex = %s
                             AND T.tIndex = NT.tIndex
                           GROUP BY NT.nIndex
                           """, (id,))
            result = cursor.fetchall()
            #novel_and_tags.append({result[0]['nIndex'] : result[0]['tags'].split(',')})
            tags.append(result[0]['tags'].split(','))

        analyze_result = analyze_user_preference(tags)

        cursor.execute("""
                       SELECT N.nIndex,
                              N.aIndex,
                              N.Title,
                              GROUP_CONCAT(T.Tag ORDER BY T.Tag SEPARATOR ', ') AS tags
                       FROM novel N
                                JOIN noveltag NT ON N.nIndex = NT.nIndex
                                JOIN tag T ON NT.tIndex = T.tIndex
                       GROUP BY N.nIndex
                       HAVING FIND_IN_SET('奇幻', tags)
                           OR FIND_IN_SET('科幻', tags)
                       ORDER BY RAND() LIMIT 100
                       """)
        sci_fi_books = cursor.fetchall()

        cursor.execute("""
                       SELECT N.nIndex,
                              N.aIndex,
                              N.Title,
                              GROUP_CONCAT(T.Tag ORDER BY T.Tag SEPARATOR ', ') AS tags
                       FROM novel N
                                JOIN noveltag NT ON N.nIndex = NT.nIndex
                                JOIN tag T ON NT.tIndex = T.tIndex
                       WHERE N.Category = '愛情'
                       GROUP BY N.nIndex
                       ORDER BY RAND() LIMIT 100
                       """)
        romance_books = cursor.fetchall()

        print('tags', tags)
        print('analyze', analyze_result)
        print('sci_fi_books', sci_fi_books[0 : analyze_result['sci-fi']])
        print('romance_books', romance_books[0 : analyze_result['romance']])
        return (
            [row['Title'] for row in sci_fi_books[:analyze_result['sci-fi']]] +
            [row['Title'] for row in romance_books[:analyze_result['romance']]]
        )

    finally:
        conn.close()


if __name__ == "__main__":
    recommend('aaa')
