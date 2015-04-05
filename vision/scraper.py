#from skimage import data, io, filters
from PIL import Image
from cStringIO import StringIO
# import matplotlib
import numpy as np
# import opencv
import re
import json
import urllib2
import os
import cv2
from subprocess import call

TMPD = os.getcwd()

class ImageScraper:
    "Scrape google images"
    def __init__(self,):
        self.fetcher = urllib2.build_opener()
        self.urls = []
        self.term = ""

    # build_url :: (String, Int) -> String
    # return links from page `idx` of google images
    def build_url(self, term, idx):
        term1 = re.sub('\s', '+', term).lower()
        return "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" \
            + term1 + "&start=" + str(idx)

    # search :: (String, Int) -> [URL]
    def search(self, term, pages=10):
        self.term = term
        for idx in range(0,pages):
            f = self.fetcher.open(self.build_url(term,idx))
            goog_json = json.load(f)
            goog_json = goog_json['responseData']['results']
            self.urls += map(lambda x: x['unescapedUrl'], goog_json)

    # downloads the list of image urls to disk
    # download :: (Int) -> IO ()
    def download(self):
        # assert(items <= len(self.urls) and items > -1)
        tdir = TMPD+'/'+self.term
        os.mkdir(tdir)

        # download1 :: (Int, URL) -> IO ()
        def download1(id_url):
            id  = id_url[0]
            url = id_url[1]

            name    = url.split('/')[-1].split('.')
            name[0] = self.term+str(id)
            name[1] = name[1][:3]
            name    = '.'.join(name)

            f = urllib2.urlopen(url)

            output = open(tdir+'/'+name,'wb')
            output.write(f.read())
            output.close()

        if self.term != "":
            map(download1, zip(range(len(self.urls)), self.urls))

    def clear(self):
        self.urls = []
        self.term = ""



s = ImageScraper()
s.search('apple')

def openImage(url):
    return Image.open(StringIO(urllib2.urlopen(url).read()))

imgs = map(openImage, s.urls)
for i in imgs:
    print i
