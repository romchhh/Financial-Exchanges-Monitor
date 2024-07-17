import cloudscraper

scraper = cloudscraper.create_scraper()
url = "https://dexscreener.com/?rankBy=volume&order=desc&maxAge=24"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://dexscreener.com/",
}

response = scraper.get(url, headers=headers)

print(response.status_code)
print(response.text[:100000])  
