# Base Image
FROM python:3.11-slim

# منع Python من كتابة ملفات .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# مجلد الشغل جوا الـ Container
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها الأول (أسرع في الـ rebuild)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# إنشاء مجلد tmp
RUN mkdir -p tmp

# تشغيل البوت
CMD ["python", "main.py"]