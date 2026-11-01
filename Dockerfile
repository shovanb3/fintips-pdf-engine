FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# লাইব্রেরি ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# কোড কপি
COPY . .

# Render এর পোর্ট কনফিগারেশন
ENV PORT=8000
EXPOSE 8000

# সার্ভার চালু করার কমান্ড
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
