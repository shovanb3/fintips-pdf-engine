FROM python:3.10-slim

# প্রয়োজনীয় লিনাক্স ও ক্রোম ডিপেনডেন্সি ইন্সটল
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ফাইল কপি
COPY requirements.txt .

# পাইথন লাইব্রেরি এবং প্লে-রাইটের ক্রোম ব্রাউজার ডাউনলোড
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Render ডিফল্ট পোর্ট 10000 ব্যবহার করে
ENV PORT=10000
EXPOSE 10000

CMD ["python", "main.py"]