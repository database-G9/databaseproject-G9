import random

import pymysql
import numpy as np
import pandas as pd

def get_book(cursor, book_id):
    cursor.execute('''
                    SELECT * FROM novel
                    WHERE nIndex = %s
                   ''', (book_id,))
    return cursor.fetchone()



def recommend(user: str, top_n: int = 10):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1107',
        database='mojoin',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mojoin.read;")
        records = cursor.fetchall()
        df = pd.DataFrame(records)

        user_book_matrix = df.pivot_table(index='Account', columns='nIndex', values='History', fill_value=0)

        if user not in user_book_matrix.index:
            print(f"⚠️ 找不到使用者：{user}")
            return []

        # 計算餘弦相似度
        dot_product_matrix = np.dot(user_book_matrix.values, user_book_matrix.values.T)
        norms = np.linalg.norm(user_book_matrix.values, axis=1)
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
            left = top_n - len(top_books)
            read_books = set(user_history[user_history > 0].index)
            excluded_ids = read_books | top_books

            if excluded_ids:
                placeholders = ','.join(['%s'] * len(excluded_ids))
                query = f"""
                    SELECT nIndex FROM novel
                    WHERE nIndex NOT IN ({placeholders})
                    ORDER BY RAND() LIMIT %s
                """
                params = list(excluded_ids) + [left * 5]
            else:
                query = "SELECT nIndex FROM novel ORDER BY RAND() LIMIT %s"
                params = [left * 5]

            cursor.execute(query, params)
            random_rows = cursor.fetchall()
            for row in random_rows:
                top_books.add(row['nIndex'])
                if len(top_books) >= top_n:
                    break

        top_books = list(top_books)[:top_n]

        # 顯示推薦結果
        print(f"📄 使用者「{user}」對未看過書籍的預測分數:")
        for book_id, score in sorted_books:
            if book_id in top_books:
                print(f"書籍 {book_id}：預測分數 {score:.2f}")
        print()

        return [get_book(cursor, book_id) for book_id in top_books]

    finally:
        conn.close()



if __name__ == "__main__":
    print(f"📚books: {recommend('U002')}")
