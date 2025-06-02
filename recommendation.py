import random

import pymysql
import numpy as np
import pandas as pd

def get_book(cursor, book_id):
    #執行SQL查詢，根據書籍編號取得對應資料
    cursor.execute('''
                    SELECT * FROM novel
                    WHERE nIndex = %s
                   ''', (book_id,))
    return cursor.fetchone()#回傳搜尋結果



def recommend(user: str, top_n: int = 10):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mojoin.read;") # 讀取使用者閱讀紀錄
        records = cursor.fetchall()# 全部取出來
        df = pd.DataFrame(records)# 轉成 pandas 資料框

        user_book_matrix = df.pivot_table(index='Account', columns='nIndex', values='History', fill_value=0)
        #建立 使用者-書籍 矩陣 沒資料就填0
        #先查詢使用者存不存在
        if user not in user_book_matrix.index:
            print(f"⚠️ 找不到使用者：{user}")
            return []

        # 計算餘弦相似度
            # 向量內積
        dot_product_matrix = np.dot(user_book_matrix.values, user_book_matrix.values.T)
        norms = np.linalg.norm(user_book_matrix.values, axis=1) # 每個使用者向量的長度
        norm_matrix = np.outer(norms, norms)
        cosine_similarity_matrix = np.divide(
            dot_product_matrix,
            norm_matrix,
            out=np.zeros_like(dot_product_matrix),
            where=norm_matrix != 0
        )
        cosine_similarity_df = pd.DataFrame(
            cosine_similarity_matrix,
            index=user_book_matrix.index,
            columns=user_book_matrix.index
        )
        #計算推薦分數
        similarities = cosine_similarity_df.loc[user]
        other_users = user_book_matrix.index.difference([user])
        user_history = user_book_matrix.loc[user]
        unread_books = user_history[user_history == 0].index

        predicted_scores = {}
        for book in unread_books:
            if book not in user_book_matrix.columns:
                continue
            scores = user_book_matrix.loc[other_users, book]
            sim_scores = similarities[other_users]
            mask = sim_scores > 0
            if mask.sum() > 0:
                weighted_sum = np.dot(scores[mask], sim_scores[mask])
                if weighted_sum > 0:
                    predicted_scores[book] = weighted_sum

        # 排序預測分數
        sorted_books = sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)
        top_books = set(id for id, _ in sorted_books[:top_n - random.randint(0, 5)])

        # ➕ 補推薦（若不足 top_n）
        if len(top_books) < top_n:
            left = top_n - len(top_books) # 還缺幾本
            read_books = set(user_history[user_history > 0].index) # 已讀書籍
            excluded_ids = read_books | top_books# 排除這些書

            if excluded_ids:
                placeholders = ','.join(['%s'] * len(excluded_ids))
                query = f"""
                    SELECT nIndex FROM novel
                    WHERE nIndex NOT IN ({placeholders})
                    ORDER BY RAND() LIMIT %s
                """
                params = list(excluded_ids) + [left * 5]# 倍數增加以保險有書可選
            else:
                query = "SELECT nIndex FROM novel ORDER BY RAND() LIMIT %s"
                params = [left * 5]

            cursor.execute(query, params)
            random_rows = cursor.fetchall()
            for row in random_rows:
                top_books.add(row['nIndex'])
                if len(top_books) >= top_n:
                    break
    
    
        # 顯示推薦分數
        top_books = list(top_books)[:top_n]
        
        print(f"📄 使用者「{user}」對未看過書籍的預測分數:")
        for book_id, score in sorted_books:
            if book_id in top_books:
                print(f"書籍 {book_id}：預測分數 {score:.2f}")
        print()
        #回傳推薦的書籍資訊
        return [get_book(cursor, book_id) for book_id in top_books]

    finally:
        conn.close()


#若直接執行此檔案，則推薦一次
#if __name__ == "__main__":
    #print(f"📚books: {recommend('U002')}")
    

def tagrecommend(user: str, top_n: int = 10):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        cursor = conn.cursor()

        # 1. 找出使用者已讀書籍 ID
        cursor.execute("""
            SELECT DISTINCT Account,nIndex FROM mojoin.read
            WHERE Account = %s AND History > 0
        """, (user,))
        records = cursor.fetchall()
        read_books = set(row['nIndex'] for row in records)
        if not read_books:
            print(f"⚠️ 使用者「{user}」沒有閱讀紀錄，隨機推薦 {top_n} 本書籍。")
            cursor.execute("SELECT nIndex FROM novel ORDER BY RAND() LIMIT %s", (top_n,))
            random_books = [row['nIndex'] for row in cursor.fetchall()]
            return [get_book(cursor, book_id) for book_id in random_books]
        
        # 2. 找出這些書的 tag
        placeholders = ','.join(['%s'] * len(read_books))
        cursor.execute(f"""
            SELECT tIndex FROM noveltag
            WHERE nIndex IN ({placeholders})
        """, list(read_books))
        tags = [row['tIndex'] for row in cursor.fetchall()]
        if not tags:
            print(f"⚠️ 沒有找到使用者讀過書籍的 tag，隨機推薦 {top_n} 本書籍。")
            cursor.execute("SELECT nIndex FROM novel ORDER BY RAND() LIMIT %s", (top_n,))
            random_books = [row['nIndex'] for row in cursor.fetchall()]
            return [get_book(cursor, book_id) for book_id in random_books]

        # 3. 統計 tag 頻率（建立使用者的 tag 偏好分數）
        tag_scores = pd.Series(tags).value_counts().to_dict()

        # 4. 找出所有包含這些 tag 的書，排除已讀書籍
        cursor.execute("""
            SELECT nIndex, tindex FROM noveltag
        """)
        all_tag_data = cursor.fetchall()

        tag_to_books = {}
        for row in all_tag_data:
            tag_to_books.setdefault(row['nIndex'], set()).add(row['tindex'])

        predicted_scores = {}
        for book_id, tag_set in tag_to_books.items():
            if book_id in read_books:
                continue
            score = sum(tag_scores.get(tag, 0) for tag in tag_set)
            if score > 0:
                predicted_scores[book_id] = score

        # 5. 排序推薦書籍
        sorted_books = sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)
        top_books = [book_id for book_id, _ in sorted_books[:top_n]]

        # 7. 若推薦書不足，補上隨機書
        if len(top_books) < top_n:
            needed = top_n - len(top_books)
            excluded_books = read_books.union(set(top_books))
            placeholders = ','.join(['%s'] * len(excluded_books)) if excluded_books else 'NULL'
            query = f"""
                SELECT nIndex FROM novel
                WHERE nIndex NOT IN ({placeholders})
                ORDER BY RAND() LIMIT %s
            """
            params = list(excluded_books) + [needed] if excluded_books else [needed]
            cursor.execute(query, params)
            random_extra = [row['nIndex'] for row in cursor.fetchall()]
            top_books.extend(random_extra)
            
        # 顯示推薦結果
        print(f"📘 使用者「{user}」根據偏好 tag 推薦：")
        for book_id, score in sorted_books[:top_n]:
            print(f"書籍 {book_id}（分數：{score}）")

        # 回傳書籍詳細資料
        return [get_book(cursor, book_id) for book_id in top_books]

    finally:
        conn.close()
        
def bookrecommend(book_id: int, top_n: int = 10):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='05101107',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        cursor = conn.cursor()

        # 1. 查出書的 Series 與 SeriesN
        cursor.execute("""
            SELECT Series, SeriesN FROM novel WHERE nIndex = %s
        """, (book_id,))
        series_info = cursor.fetchone()
        if not series_info:
            print(f"⚠️ 找不到書籍 {book_id}。")
            return []

        series_id = series_info['Series']
        series_n = series_info['SeriesN']

        # 2. 查找續集（SeriesN > 現在的）
        next_book_id = None
        if series_id and series_id > 0:
            cursor.execute("""
                SELECT nIndex FROM novel
                WHERE Series = %s AND SeriesN > %s
                ORDER BY SeriesN ASC LIMIT 1
            """, (series_id, series_n))
            row = cursor.fetchone()
            if row:
                next_book_id = row['nIndex']

        # 3. 查找前一集（SeriesN < 現在的）
        prev_book_id = None
        if series_id and series_id > 0:
            cursor.execute("""
                SELECT nIndex FROM novel
                WHERE Series = %s AND SeriesN < %s
                ORDER BY SeriesN DESC LIMIT 1
            """, (series_id, series_n))
            row = cursor.fetchone()
            if row:
                prev_book_id = row['nIndex']

        related_books = []
        if next_book_id:
            related_books.append(next_book_id)
        if prev_book_id:
            related_books.append(prev_book_id)

        # 4. 查 tag
        cursor.execute("""
            SELECT tIndex FROM noveltag WHERE nIndex = %s
        """, (book_id,))
        tags = [row['tIndex'] for row in cursor.fetchall()]
        if not tags:
            print(f"⚠️ 書籍 {book_id} 沒有 tag 資料。")
            return [get_book(cursor, bid) for bid in related_books]

        # 5. 所有書 tag 資料
        cursor.execute("SELECT nIndex, tIndex FROM noveltag")
        all_tag_data = cursor.fetchall()

        tag_to_books = {}
        for row in all_tag_data:
            if int(row['nIndex']) == int(book_id):
                continue
            tag_to_books.setdefault(row['nIndex'], set()).add(row['tIndex'])

        # 移除本書，避免推薦自己
        tag_to_books.pop(book_id, None)

        # 6. tag 相似度分數
        predicted_scores = {}
        for other_book_id, tag_set in tag_to_books.items():
            if int(other_book_id) == int(book_id) or other_book_id in related_books:
                continue
            overlap = len(set(tags) & tag_set)
            if overlap > 0:
                predicted_scores[other_book_id] = overlap
        # 移除本書，避免推薦自己
        predicted_scores.pop(book_id, None)
        
        sorted_books = sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)
        top_books = []
        for bid, _ in sorted_books:
            if bid != book_id and bid not in top_books and bid not in related_books:
                top_books.append(bid)
            if len(top_books) >= (top_n - len(related_books)):
                break

        # 7. 補齊推薦（隨機）
        if len(top_books) + len(related_books) < top_n:
            needed = top_n - len(top_books) - len(related_books)
            excluded = top_books + related_books + [book_id]
            placeholders = ','.join(['%s'] * len(excluded))
            query = f"""
                SELECT nIndex FROM novel
                WHERE nIndex NOT IN ({placeholders})
                ORDER BY RAND() LIMIT %s
            """
            params = excluded + [needed * 3]
            cursor.execute(query, params)
            for row in cursor.fetchall():
                bid = row['nIndex']
                if bid != book_id and bid not in top_books and bid not in related_books:
                    top_books.append(bid)
                if len(top_books) + len(related_books) >= top_n:
                    break

        final_books = [bid for bid in (related_books + top_books) if bid != book_id]

    
        print("❗目前 book_id:", book_id)
        print("✅ related_books:", related_books)
        print("✅ predicted_scores.keys():", list(predicted_scores.keys()))
        print("✅ top_books:", top_books)
        print("✅ final_books:", final_books)
        # 8. 顯示推薦結果
        print(f"📘 書籍 {book_id} 的推薦：")
        for i, bid in enumerate(final_books):
            label = "續集" if bid == next_book_id else "前一集" if bid == prev_book_id else predicted_scores.get(bid, 0)
            print(f"{i+1}. 書籍 {bid}（{label}）")

        return [get_book(cursor, bid) for bid in final_books]

    finally:
        conn.close()



if __name__ == "__main__":
    print(f"📚books: {bookrecommend('76')}")
