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
                "--hide-scrollbars"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = await context.new_page()

        try:
            # পেজ লোড হওয়া
            await page.goto(url, wait_until="networkidle", timeout=90000)

            # অপ্রয়োজনীয় হেডার বাটন ও বর্ডার বাদ দেওয়া
            css_styles = """
                body, html { box-shadow: none !important; margin: 0 !important; padding: 0 !important; background: #fff !important; }
                header, nav, .no-print, [class*="header"], [class*="navbar"] { display: none !important; }
                * { -webkit-print-color-adjust: exact !important; }
            """
            await page.add_style_tag(content=css_styles)

            # সহজ ও এরর-মুক্ত অটো-স্ক্রল (যাতে সব ৬০-৬৫ পেজ লোড হয়)
            for _ in range(15):
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(0.5)

            # স্ক্রল শেষে পেজ ঠিক হতে ১ সেকেন্ড অপেক্ষা
            await asyncio.sleep(1)

            # মিনিমাম ৩ মিমি (3mm) মার্জিন সহ ল্যান্ডস্কেপ PDF তৈরি
            pdf_bytes = await page.pdf(
                format="A4",
                landscape=True,
                print_background=True,
                prefer_css_page_size=False,
                margin={"top": "3mm", "bottom": "3mm", "left": "3mm", "right": "3mm"}
            )
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

        await browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{final_filename}"'}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
