#!/usr/bin/env bash
# ডিপ্লয়ের সময় স্বয়ংক্রিয়ভাবে ক্রোম ও ডিপেন্ডেন্সি ইনস্টল করার স্ক্রিপ্ট
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium