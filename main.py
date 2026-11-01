import os
import urllib.parse
from fastapi import FastAPI, Response, HTTPException
from playwright.async_api import async_playwright

app = FastAPI(title="FinTips Vector PDF Engine")

@app.get("/")
def home():
    return {"status": "active", "service": "FinTips Headless Chrome PDF Generator"}

@app.get("/download-pdf")
async def generate_pdf(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is missing")
    
    decoded_url = urllib.parse.unquote(url)
    
    async with async_playwright() as p:
        # ব্যাকগ্রাউন্ডে আসল ক্রোম চালু করা
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        # মোবাইল বা ডেস্কটপ ভিউপোর্ট সেট করা
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        # পেজ সম্পূর্ণ লোড হওয়া ও নেটওয়ার্ক শান্ত হওয়া পর্যন্ত অপেক্ষা
        await page.goto(decoded_url, wait_until="networkidle", timeout=45000)
        
        # ১০০% ক্রিস্টাল ক্লিয়ার A4 Landscape ভেক্টর প্রিন্ট তৈরি
        pdf_bytes = await page.pdf(
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top": "4mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
        )
        await browser.close()
        
        # সরাসরি ক্যান্ডিডেটের ফোনে ফাইল ডাউনলোড পুশ
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=WB_Tender_Bulletin.pdf",
                "Cache-Control": "no-cache"
            }
        )