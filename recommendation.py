import pymysql
import numpy as np
import pandas as pd

def get_book(cursor, book_id):
    cursor.execute('''
                    SELECT * FROM novel
                    WHERE nIndex = %s
                   ''', (book_id,))
    return cursor.fetchone()


def recommend(user : str, top_n : int = 10):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='412410291',
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

        dot_product_matrix = np.dot(user_book_matrix.values, user_book_matrix.values.T)
        norms = np.linalg.norm(user_book_matrix.values, axis=1)
        norm_matrix = np.outer(norms, norms)
        cosine_similarity_matrix = np.divide(
            dot_product_matrix,
            norm_matrix,
            out=np.zeros_like(dot_product_matrix),
            where=norm_matrix != 0
        )
        cosine_similarity_df = pd.DataFrame(cosine_similarity_matrix, index=user_book_matrix.index, columns=user_book_matrix.index)

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

        sorted_books = sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)
        top_books = sorted_books[:top_n]

        # TODO: top_n推薦數量不足，補上熱門書籍+續集(可能有)

        print(f"使用者「{user}」的紀錄: \n{user_history}\n")
        print(f"📄 使用者「{user}」對未看過書籍的喜好程度:")
        for book_id, score in predicted_scores.items():
            print(f"書籍 {book_id}：預測分數 {score:.2f}")
        print()
        print(f"📄 所有使用者的紀錄: \n{df}\n")
        print(f"📈 餘弦相似度矩陣:\n{cosine_similarity_df}\n")
        print(f"📚 推薦給使用者「{user}」的書籍：")
        for book_id, score in top_books:
            print(f"書籍 {book_id}：預測分數 {score:.2f}")

        return [get_book(cursor, book_id) for book_id, _ in top_books]

    finally:
        conn.close()



if __name__ == "__main__":
    print(f"📚books: {recommend('aaa')}")
