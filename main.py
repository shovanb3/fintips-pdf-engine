import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PDF Engine is running perfectly!"}

@app.get("/download-pdf")
async def download_pdf(
    url: str = Query(..., description="Target web page URL")
):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # আজকের তারিখ দিয়ে নাম তৈরি
    today_date = datetime.now().strftime("%d-%m-%Y")
    final_filename = f"Download_PDM_Bulletin_for_WB_Live_Tender_Bulletin_{today_date}.pdf"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--font-render-hinting=none",
                "--force-color-profile=srgb",
                "--hide-scrollbars"             # ব্রাউজারের স্ক্রলবারের দাগ দূর করবে
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = await context.new_page()

        try:
            # পেজে যাওয়া এবং লোড হওয়া
            await page.goto(url, wait_until="networkidle", timeout=90000)

            # সাইডের অতিরিক্ত ছায়া ও মার্জিন রিমুভ এবং ওপরের বোতাম বার মুছে ফেলা
            await page.add_style_tag(content="""
                body, html { 
                    box-shadow: none !important; 
                    margin: 0 !important; 
                    padding: 0 !important; 
                    background: #ffffff !important;
                }
                header, nav, .no-print, [class*="header"], [class*="navbar"] { 
                    display: none !important; 
                }
                * { 
                    -webkit-print-color-adjust: exact !important; 
                }
            """)

            # সম্পূর্ণ ৬০-৬৫টি পেজের সব টেন্ডার লোড করার জন্য অটো-স্ক্রল
            await page.evaluate("""async () => {
                await new Promise((resolve) => {
                    var totalHeight = 0;
                    var distance = 800;
                    var timer = setInterval(() => {
                        var sc
