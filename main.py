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

    today_date = datetime.now().strftime("%d-%m-%Y")
    final_filename = f"WB_Live_Tender_Bulletin_{today_date}.pdf"

    async with async_playwright() as p:
        # সুপার শার্প ফন্ট ইঞ্জিন এনাবল করা
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--font-render-hinting=medium",       # ফন্টের এজ স্পষ্ট করবে
                "--enable-font-antialiasing",
                "--force-color-profile=srgb",
                "--hide-scrollbars"
            ]
        )
        
        # A4 ল্যান্ডস্কেপের নিখুঁত আসপেক্ট রেশিও এবং স্কেলিং
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},   # A4 ল্যান্ডস্কেপের সাথে পারফেক্ট ম্যাচ
            device_scale_factor=1                      # স্কেলিং ডিসটরশন বন্ধ
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=90000)

            # ফন্টকে ক্রিস্টাল ক্লিয়ার, গাঢ় ও শার্প করার বিশেষ CSS
            css_styles = """
                body, html { 
                    box-shadow: none !important; 
                    margin: 0 !important; 
                    padding: 0 !important; 
                    background: #fff !important; 
                    -webkit-font-smoothing: antialiased !important;
                    -moz-osx-font-smoothing: grayscale !important;
                    text-rendering: optimizeLegibility !important;
                }
                header, nav, .no-print, [class*="header"], [class*="navbar"] { 
                    display: none !important; 
                }
                * { 
                    -webkit-print-color-adjust: exact !important;
                    color-adjust: exact !important;
                }
                /* টেবিল ও ফন্ট যেন হালকা না হয়ে স্পষ্ট কালো থাকে */
                table, th, td, p, span, div {
                    text-shadow: none !important;
                }
            """
            await page.add_style_tag(content=css_styles)

            # সম্পূর্ণ পেজ লোড নিশ্চিত করতে অটো-স্ক্রল
            for _ in range(15):
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(0.5)

            await asyncio.sleep(1)

            # আসল ভেক্টর প্রিন্ট
            pdf_bytes = await page.pdf(
                format="A4",
                landscape=True,
                print_background=True,
                prefer_css_page_size=False,
                scale=1.0,                               # জোর করে ছোট হওয়া বন্ধ করবে (ঝাপসা দূর হবে)
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
