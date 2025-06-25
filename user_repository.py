import os
import psycopg2
from psycopg2.extras import RealDictCursor

class UserRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )
        self.conn.autocommit = True

    def get_content(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users ORDER BY id;")
            return cur.fetchall()

    def find(self, id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (id,))
            return cur.fetchone()

    def save(self, user_data):
        with self.conn.cursor() as cur:
            # Обновление
            if 'id' in user_data:
                cur.execute("""
                    UPDATE users SET name = %s, email = %s WHERE id = %s;
                """, (user_data['name'], user_data['email'], user_data['id']))
                return user_data['id']
            else:
                # Вставка нового пользователя
                cur.execute("""
                    INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;
                """, (user_data['name'], user_data['email']))
                new_id = cur.fetchone()['id']
                return str(new_id)

    def destroy(self, id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s;", (id,))
            return cur.rowcount > 0