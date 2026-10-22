import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """بتفتح connection جديد مع PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "data_bot"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def init_db():
    """
    بتنشئ الجداول لو مش موجودة
    بتتشغل مرة واحدة لما البوت يبدأ
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          SERIAL PRIMARY KEY,
            user_id     BIGINT NOT NULL,
            username    VARCHAR(100),
            file_name   VARCHAR(255),
            rows        INTEGER,
            columns     INTEGER,
            chart_type  VARCHAR(50),
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized.")


def save_analysis(
    user_id: int,
    username: str,
    file_name: str,
    rows: int,
    columns: int,
    chart_type: str,
):
    """بتحفظ كل تحليل في قاعدة البيانات"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO analyses (user_id, username, file_name, rows, columns, chart_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, username, file_name, rows, columns, chart_type))

    conn.commit()
    cur.close()
    conn.close()


def get_user_history(user_id: int) -> list:
    """بترجع آخر 5 تحليلات للمستخدم"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT file_name, rows, columns, chart_type, created_at
        FROM analyses
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_admin_stats() -> dict:
    """بترجع إحصائيات للـ Admin"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT COUNT(DISTINCT user_id) AS total_users FROM analyses;")
    total_users = cur.fetchone()["total_users"]

    cur.execute("SELECT COUNT(*) AS total_analyses FROM analyses;")
    total_analyses = cur.fetchone()["total_analyses"]

    cur.execute("""
        SELECT chart_type, COUNT(*) AS count
        FROM analyses
        GROUP BY chart_type
        ORDER BY count DESC;
    """)
    chart_stats = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total_users":    total_users,
        "total_analyses": total_analyses,
        "chart_stats":    chart_stats,
    }