import urllib
import requests
import re
import time
import os
import logging
import random

text_class_div = r'<div class=\"text\">((?:(?!<\/div>)[\s\S])*)<\/div>'
p_regex = r'<p>((?:(?!<\/p>)[\s\S])*)<\/p>'
url_regex = '[0-9a-zA-Z_\-\/\.]+'
imag_class_div_regex = r'<a\s+href=\"(' + url_regex + r')\".*>*.<\/a>'
number_regex = r'<a\s+href=\".*\">([0-9]*)<\/a>'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3)'
    + ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

JIANDAN="jiandan"
logger = None

def init():
    print("creating data folder:" + JIANDAN)
    if not os.path.exists(JIANDAN):
        os.mkdir(JIANDAN)
        
    global logger
    if logger is None:
        logfilename = JIANDAN + "/log.txt"
        print("creating log file:" + logfilename)
        logging.basicConfig(filename=logfilename,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger('jiandan')


class Post:
    def __init__(self, number, urls):
        self.number = number
        self.urls = urls
        
    def __repr__(self):
        return str((self.number, self.urls))
        
def get_divs(pic_html):
    divs = re.findall(text_class_div, pic_html)
    return divs
    
    
def get_urls(pic_html):
    posts = []
    divs = get_divs(pic_html)
    for div in divs:      
        
        numbers = re.findall(number_regex, div)
        numbers = [int(n) for n in numbers]
        number = numbers[0] if len(numbers) > 0 else None
        
        imag_urls = None
        ps = re.findall(p_regex, div)
        for p in ps:
            imag_urls = re.findall(imag_class_div_regex, p)  
            
        if number is not None:
            posts.append(Post(number, imag_urls))    
    return posts
                
    
def get_file_name(url):
    return os.path.basename(url)

def refine_url(url):
    if url.startswith("//"):
        return "https:" + url
    
def save_pictures_html(pic_html, pic_folder):
        
        
    n_download = 0
    pic = JIANDAN + "/" + pic_folder
    if not os.path.exists(pic):
        logger.info("pic not exists")
        os.mkdir(pic)
    else:
        logger.info("pic exists")
        
    
    posts = get_urls(pic_html)
    for post in posts:        
        number, urls = post.number, post.urls
        path = pic + "/" + str(number)
        if not os.path.exists(path):
            logger.info("number %d not exists"%number)
            os.mkdir("" + path)
        else:
            logger.info("number %d exists"%number)
            
        with open(path + "/" + "meta.txt", "at") as meta:
            localtime = time.asctime( time.localtime(time.time()) )
            meta.write("update time:" + str(localtime) + "\n")
                        
        for url in urls:
            pic_path = path + "/" + get_file_name(url)
            if not os.path.exists("./" + pic_path):
                logger.info("file %s not exists"%pic_path)
                
                refined_url = refine_url(url)
                with requests.get(refined_url, headers=headers) as response:
                    data = response.content
                    with open(pic_path, "wb") as f:
                        f.write(response.content)
                        n_download += 1
            else:
                logger.info("file %s exists"%pic_path)
    return n_download
                
def save_pictures_url(url, pic_folder):
    
    with requests.get(url, headers=headers) as response:
        data = response.content
        pic_html = data.decode("utf-8")
        return save_pictures_html(pic_html, pic_folder)
    
      
def pull_pictures():
    init()
    while True:
        print("pull picutres...")
        try:
            n_download = save_pictures_url("http://jandan.net/ooxx", "ooxx")
            print("%d pictures for %s, sleeping..."%(n_download, "ooxx"))
            time.sleep(100 + random.randint(0, 100))
            n_download = save_pictures_url("http://jandan.net/zoo", "zoo")
            print("%d pictures for %s, sleeping..."%(n_download, "zoo"))
            time.sleep(100 + random.randint(0, 100))
            n_download = save_pictures_url("http://jandan.net/girl", "girl")
            print("%d pictures for %s, sleeping..."%(n_download, "girl"))
            time.sleep(100 + random.randint(0, 100))
            n_download = save_pictures_url("http://jandan.net/pic", "pic")
            print("%d pictures for %s, sleeping..."%(n_download, "pic"))
            time.sleep(100 + random.randint(0, 100))
        except KeyboardInterrupt as e:
            logger.error(str(e))
            print(str(e))
            break
        except ConnectionError as e:
            logger.error(str(e))
            time.sleep(200)
            print(str(e))
        except Exception as e:
            logger.error(str(e))
            time.sleep(200)
            print(str(e))

pull_pictures()
