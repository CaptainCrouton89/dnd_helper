import random
import requests
import time
from bs4 import BeautifulSoup

fake_header = {
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {}, 
  "headers": {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en-US,en;q=0.9", 
    "Host": "httpbin.org", 
    "Referer": "https://www.codementor.io/@scrapingdog/10-tips-to-avoid-getting-blocked-while-scraping-websites-16papipe62", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15", 
    "X-Amzn-Trace-Id": "Root=1-6196bf67-31303fd84ce334a44718e3da"
  }, 
  "method": "GET", 
  "origin": "104.28.97.69", 
  "url": "https://httpbin.org/anything"
}


name_gen_urls = {
    "rinkworks": "http://rinkworks.com/namegen/fnames.cgi?d=1&f=0",
}
def save_html(html, path):
    with open(path, 'wb') as f:
        f.write(html)

def open_html(path):
    with open(path, 'rb') as f:
        return f.read()

def get_ss_items():
    url = "https://www.seventhsanctum.com/generate.php?Genname=magicitem"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    names = soup.find_all("div", {"class": "GeneratorResultPrimeBG"})
    names.extend(soup.find_all("div", {"class": "GeneratorResultSecondaryBG"}))
    names = [name.text for name in names]
    return names

# Doesn't work—they've shielded the names from scraping
def get_fantasygen_names(char_type):
    char_type = "human"
    url = f"http://webcache.googleusercontent.com/search?q=cache:https://www.fantasynamegenerators.com/dnd-human-names.php"
    r = requests.get(url, fake_header)
    # save_html(r.content, 'names.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    names = soup.select("genSection")
    print(names)
    return names

def scrape(func, count, output):
    f = open(output, "a")
    for i in range(count):
        time.sleep(random.random())
        if i % 10 == 0:
            print(i)
        try:
            f.write('\n'.join(func()))
        except:
            print("failure")
    f.close()

if __name__ == '__main__':
    all_names = set()
    scrape(get_ss_items, 4000, "fantasyItems.txt")