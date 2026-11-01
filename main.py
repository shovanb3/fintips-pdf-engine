# main.py - High-Definition Retina Vector PDF Engine
import os
import urllib.parse
from fastapi import FastAPI, Response, HTTPException
from playwright.async_api import async_playwright

app = FastAPI(title="FinTips High-Definition PDF Engine")

@app.get("/")
def home():
    return {"status": "active", "service": "FinTips Retina Chrome PDF Generator"}

@app.get("/download-pdf")
async def generate_pdf(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is missing")
    
    decoded_url = urllib.parse.unquote(url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--font-render-hinting=medium",
                "--enable-font-antialiasing"
            ]
        )
        
        # ১. রেটিনা ২এক্স হাই-রেজোলিউশন ভিউপোর্ট (ফন্ট একদম ক্রিস্টাল শার্প করার জন্য)
        page = await browser.new_page(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2
        )
        
        # প্রিন্ট মোড সক্রিয় করা
        await page.emulate_media(media="print")
        
        # পেজ লোড হওয়া
        await page.goto(decoded_url, wait_until="networkidle", timeout=45000)
        
        # ২. গুগল ফন্ট (Hind Siliguri) ১০০% লোড হওয়া নিশ্চিত করার নির্দেশ
        await page.evaluate("document.fonts.ready")
        
        # ফন্ট রেন্ডারিং সেটেল হওয়ার জন্য ৪০০ মিলি-সেকেন্ড অপেক্ষা
        await page.wait_for_timeout(400)
        
        # ৩. নিখুঁত A4 Landscape ভেক্টর PDF জেনারেট (কোনো লেখা স্ট্রেচ হবে না)
        pdf_bytes = await page.pdf(
            format="A4",
            landscape=True,
            print_background=True,
            prefer_css_page_size=True
        )
        await browser.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=WB_Tender_Bulletin.pdf",
                "Cache-Control": "no-cache"
            }
        )


# main.py - Ultra-Fast Persistent Chromium PDF Engine
import os
import urllib.parse
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from playwright.async_api import async_playwright

browser_instance = None
playwright_manager = None

# সার্ভার চালু হওয়ার সময় একবারই ক্রোম অন হবে (প্রতি রিকোয়েস্টে নতুন করে অন হবে না)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser_instance, playwright_manager
    playwright_manager = await async_playwright().start()
    browser_instance = await playwright_manager.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--font-render-hinting=medium",
            "--enable-font-antialiasing"
        ]
    )
    yield
    if browser_instance:
        await browser_instance.close()
    if playwright_manager:
        await playwright_manager.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"status": "active", "service": "FinTips Turbo PDF Generator"}

@app.get("/download-pdf")
async def generate_pdf(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL is missing")
    
    decoded_url = urllib.parse.unquote(url)
    
    # ব্যাকগ্রাউন্ডে চালু থাকা ক্রোম ব্রাউজারে নিমেষে একটি নতুন ট্যাব খোলা
    context = await browser_instance.new_context(
        viewport={"width": 1600, "height": 1000},
        device_scale_factor=2
    )
    page = await context.new_page()
    await page.emulate_media(media="print")
    
    try:
        # অযথা দেরি না করে domcontentloaded এ দ্রুত পেজ নেওয়া
        await page.goto(decoded_url, wait_until="domcontentloaded", timeout=30000)
        
        # ফন্ট লোড নিশ্চিত করা
        await page.evaluate("document.fonts.ready")
        
        # দ্রুত ভেক্টর PDF জেনারেট
        pdf_bytes = await page.pdf(
            format="A4",
            landscape=True,
            print_background=True,
            prefer_css_page_size=True
        )
    finally:
        await context.close() # শুধু ট্যাবটি বন্ধ হবে, ক্রোম চালু থাকবে
        
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=WB_Tender_Bulletin.pdf",
            "Cache-Control": "no-cache"
        }
    )
