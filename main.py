import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PDF Engine is running perfectly!"}

@app.get("/download-pdf")
async def download_pdf(url: str = Query(..., description="Target web page URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    async with async_playwright() as p:
        # ব্যাকগ্রাউন্ডে হেডলেস ক্রোম ব্রাউজার রান
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # পেজটি ওপেন হওয়া এবং নেটওয়ার্ক শান্ত হওয়া পর্যন্ত অপেক্ষা
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # আসল ভেক্টর কোয়ালিটি A4 সাইজ PDF প্রিন্ট
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
            )
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

        await browser.close()

        # সরাসরি ব্রাউজারে বা মোবাইলে ডাউনলোড করানোর রেসপন্স
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="bulletin.pdf"'}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)