import uuid
import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from pyppeteer import launch
import validators

base_url = os.environ.get('BASEURL')
app = FastAPI()
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshot")

@app.get("/")
async def screenshoot_api(url: str, width: int = 1920, height: int = 1080):
    if not validators.url(url):
        raise HTTPException(detail='invalid url', status_code=400)

    unique_id = uuid.uuid4()
    image_path = f'screenshots/{unique_id}.png'

    browser = await launch(options={'args': ['--no-sandbox'],'autoClose': False, 'headless': True, 'executablePath': '/usr/bin/google-chrome'})
    page = await browser.newPage()
    await page.setViewport(viewport={
        'width': width,
        'height': height
    })
    await page.goto(url)
    await page.screenshot({'path': image_path})
    await browser.close()
    return {"image": f"{base_url if base_url else ''}/{image_path}"}

