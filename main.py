import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PDF Engine is running perfectly!"}

@app.get("/download-pdf")
async def download_pdf(
    url: str = Query(..., description="Target web page URL"),
    filename: str = Query("Tender_Bulletin.pdf", description="Custom name for PDF file")  # ডিফল্ট নাম
):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # নামের শেষে .pdf না থাকলে স্বয়ংক্রিয়ভাবে যোগ হবে
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    async with async_playwright() as p:
        # ফন্ট ঝকঝকে ও শার্প করার জন্য সেটিংস
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--font-render-hinting=none",
                "--force-color-profile=srgb"
            ]
        )
        
        # রেটিনা হাই-রেজোলিউশন মোড (ঝাপসা দূর করার জন্য)
        context = await browser.new_context(
            device_scale_factor=2
        )
        page = await context.new_page()

        try:
            await page.emulate_media(media="screen")
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # পারফেক্ট ক্রিস্টাল-ক্লিয়ার ভেক্টর PDF তৈরি
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
            )
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

        await browser.close()

        # ডায়নামিক ফাইলের নাম দিয়ে ডাউনলোড করানো
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
