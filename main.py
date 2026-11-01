import os
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

    # আজকের তারিখ তৈরি করা (দিন-মাস-বছর ফরম্যাটে, যেমন: 01-11-2024)
    today_date = datetime.now().strftime("%d-%m-%Y")
    
    # ফাইলের নামের সাথে ডেট যোগ করা
    final_filename = f"WB Live Tender Finder Bulletin_{today_date}.pdf"

    async with async_playwright() as p:
        # ১. টেক্সট ও ফন্ট শার্প করার সেটিংস
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--font-render-hinting=none",
                "--force-color-profile=srgb"
            ]
        )
        
        # ২. ল্যান্ডস্কেপ ভিউপোর্ট এবং রেটিনা স্কেলিং
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, # ল্যান্ডস্কেপ ভিউ
            device_scale_factor=2
        )
        page = await context.new_page()

        try:
            await page.emulate_media(media="screen")
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # পারফেক্ট ল্যান্ডস্কেপ (Landscape) PDF প্রিন্ট
            pdf_bytes = await page.pdf(
                format="A4",
                landscape=True,                          # <-- এটি PDF-কে Landscape (আড়াআড়ি) করবে
                print_background=True,
                prefer_css_page_size=False,             # ফিক্সড ল্যান্ডস্কেপ বাধ্য করার জন্য False
                margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
            )
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

        await browser.close()

        # ডায়নামিক নাম এবং ল্যান্ডস্কেপ ফাইল রিটার্ন
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{final_filename}"'}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
