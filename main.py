from email import message
from typing import Any
from unicodedata import name
import uuid
import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, AnyUrl

from pyppeteer import launch
import validators

base_url = (
    os.environ.get("BASEURL") if "BASEURL" in os.environ else "http://localhost:8000"
)
app = FastAPI(title="Screenshot API")
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshot")


class ScreenshotResponse(BaseModel):
    image: AnyUrl
    url: AnyUrl
    width: int
    height: int
    message: str


@app.get("/")
async def index():
    return {"name": "Screenshot API", "status": "running", "docs": f"{base_url}/docs"}


@app.get("/ss", response_model=ScreenshotResponse)
async def screenshoot_api(url: str, width: int = 1920, height: int = 1080):
    if not validators.url(url):
        raise HTTPException(detail="invalid url", status_code=400)

    unique_id = uuid.uuid4()
    image_path = f"screenshots/{unique_id}.png"

    browser = await launch(
        options={
            "args": ["--no-sandbox"],
            "autoClose": False,
            "headless": True,
            "executablePath": "/usr/bin/google-chrome",
        }
    )
    page = await browser.newPage()
    await page.setViewport(viewport={"width": width, "height": height})
    await page.goto(url)
    await page.screenshot({"path": image_path})
    await browser.close()
    return ScreenshotResponse(
        image=f"{base_url if base_url else ''}/{image_path}",
        url=url,
        width=width,
        height=height,
        message="this api deployed to serverless service, image only last for few minutes, before deleted",
    )
