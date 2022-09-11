import requests
import os
from dotenv import load_dotenv

class ShortUrl:
    def __init__(self, url: str):
        self.shortened_url = self.get_short_url(url)
    
    def get_short_url(self, url: str):
        load_dotenv()
        api_key = os.getenv("CUTTLY_API_KEY")
        api_url = f"https://cutt.ly/api/api.php?key={api_key}&short={url}"
        data = requests.get(api_url).json()["url"]
        if data["status"] == 7:
            shortened_url = data["shortLink"]
            return shortened_url
        else:
            print("[!] Error Shortening URL:", data)
            
    def __str__(self):
        return self.shortened_url