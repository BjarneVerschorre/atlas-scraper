import os
import httpx
import asyncio
import threading
from bs4 import BeautifulSoup as bs

def get_page(url) -> bs:
    res = httpx.get(url, timeout=30)
    soup = bs(res.text, "html.parser")
    return soup

def get_images(soup: bs) -> list[str]:
    images = []
    for img in soup.find_all("li", {"class": "flexListItem"}):
        images.append(img.find('a')['href'])
        
    return images

def save_image(image_data: bytes, file_name: str):
    with open(f"images/{file_name}", "wb") as f:
        f.write(image_data)

    print(f"Downloaded \"{file_name}\"")

async def download_image(client: httpx.AsyncClient, image_url:str):
    res = await client.get(f"https://www.memeatlas.com/{image_url}")

    if res.status_code != 200:
        print(f"Failed to download \"{image_url}\"")
        return
    
    file_name = image_url.split("/")[-1]
    threading.Thread(target=save_image, args=(res.content, file_name)).start()


def get_existent_images() -> list[str]:
    existent_images = []
    for file in os.listdir("images"):
        existent_images.append(file)

    return existent_images


async def main():

    url = input("https://www.memeatlas.com/")
    url = url if url.startswith("https://www.memeatlas.com/") else f"https://www.memeatlas.com/{url}"

    soup = get_page(url)
    images = get_images(soup)

    print(f"Found {len(images)} images")
    
    os.makedirs("images", exist_ok=True)

    # Remove existent images from list
    existent_images = get_existent_images()
    images = [image for image in images if image.split("/")[-1] not in existent_images]
    
    print(f"Downloading {len(images)} images")

    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        tasks = [download_image(client, image) for image in images]
        await asyncio.gather(*tasks)

    print("Done")


if __name__ == "__main__":
    asyncio.run(main())