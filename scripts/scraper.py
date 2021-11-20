import requests
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

def get_rinkworks_names():
    url = "http://rinkworks.com/namegen/fnames.cgi?d=1&f=0"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    names = soup.select_one('.fnames_results').select("td")
    names = [name.string for name in names]
    return names

def get_reedsy_names(char_type):
    url = f"http://webcache.googleusercontent.com/search?q=cache:https://blog.reedsy.com/character-name-generator/fantasy/{char_type}/"
    r = requests.get(url, fake_header)
    # save_html(r.content, 'names.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    names = soup.find(id="names-container").select("h3")
    names = [name.string for name in names]
    return names

def get_names():
    names = []
    names.extend(get_reedsy_names("human"))
    names.extend(get_reedsy_names("elf"))
    names.extend(get_rinkworks_names())
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
        if i % 10 == 0:
            print(i)
        try:
            f.write('\n'.join(func()))
        except:
            print("failure")

if __name__ == '__main__':
    all_names = set()
    with open("names.txt") as f:
        for line in f:
            all_names.add(line.strip())
    with open("new_names.txt", "w") as f:
        f.write('\n'.join(all_names))