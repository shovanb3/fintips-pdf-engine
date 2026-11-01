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
    final_filename = f"Download_PDM_Bulletin_for_WB_Live_Tender_Bulletin_{today_date}.pdf"

    async with async_playwright() as p:
        # মেমোরি হালকা রাখার এবং শার্প ফন্টের ফ্ল্যাগ
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",        # 502 এরর এবং ক্র্যাশ পুরোপুরি বন্ধ করবে
                "--disable-gpu",
                "--font-render-hinting=medium",
                "--hide-scrollbars"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1.5              # ক্রিস্টাল ক্লিয়ার টেক্সট কিন্তু মেমোরি ফ্রেন্ডলি
        )
        page = await context.new_page()

        try:
            # পেজে লোড হওয়া
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # ফন্ট শার্প ও ডার্ক করার জন্য CSS
            css_styles = """
                body, html { 
                    box-shadow: none !important; 
                    margin: 0 !important; 
                    padding: 0 !important; 
                    background: #fff !important; 
                    text-rendering: geometricPrecision !important;
                }
                header, nav, .no-print, [class*="header"], [class*="navbar"] { 
                    display: none !important; 
                }
                * { 
                    -webkit-print-color-adjust: exact !important;
                }
                table {
                    border-collapse: collapse !important;
                }
            """
            await page.add_style_tag(content=css_styles)

            # মেমোরি নষ্ট না করে লাইটওয়েট স্ক্রল (৬০-৬৫ পেজ লোড নিশ্চিত করতে)
            await page.evaluate("""() => {
                window.scrollTo(0, document.body.scrollHeight);
            }""")
            await asyncio.sleep(2)

            # পারফেক্ট ল্যান্ডস্কেপ ভেক্টর PDF প্রিন্ট
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
