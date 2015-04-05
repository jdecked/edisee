import requests, json
import numpy as np
import cv2
from pprint import pprint
from nltk.corpus import wordnet as wn
import mraa

class WatsonConnect:
    "Read Watson API account data from JSON."
    creds = None

    # type service
    services = ["visual_recognition", "concept_expansion", "speech_to_text"]

    #   __init__ : (Service, ?servPath) -> ()
    def __init__(self, service, servPath=''):
        if self.creds == None:
            try:
                with open(servPath) as j:
                    self.creds = json.load(j)
            except:
                print "Did not provide a valid JSON credentials file on init"
                raise

        assert(service in self.services)
        c = self.creds[service][0]['credentials']
        self.service = service
        self.url     = c["url"]
        self.auth    = (c["username"], c["password"])

class VisualRecog:
    "Wrapper around the Watson visual-recognition service"
    def __init__(self):
        self.vr = WatsonConnect('visual_recognition')

    #   recognize : imgPath -> Maybe [(String, Float)]
    def recognize(self, imgPath):
        res = requests.post(url=self.vr.url + '/v1/tag/recognize',
                             auth=self.vr.auth,
                             files={'img_File': open(imgPath, 'rb')},
                             stream=True).json()
        if 'labels' in res['images'] and res['images']['labels'] != []:
            return map(lambda x: (x['label_name'], float(x['label_score'])),
                        res['images']['labels'])
        else: return None


# c = VisualRecog()
# pprint(c.recognize('food.jpg'))
# ===>
# {u'images': [{u'image_id': u'0',
#               u'image_name': u'food.jpg',
#               u'labels': [{u'label_name': u'Graphics',
#                            u'label_score': u'0.584123'}]}]}

# Find related words. Only nouns by default.
#   related_words : (word, ?WordTypes) -> [word]
def related_words(word, typeof=['n']):
    return list(set([s.name().split('.')[0] for s in wn.synsets(word)
                     if len(wn.synsets(word)) > 0
                     and s.name.split('.')[1] in typeof]))

# Is the current image a match according to Watson?
#   is_match_watson : (word, Maybe [(String,Float)], ?conf_lvl) -> Bool
def is_match_watson(word, labels, conf_lvl=0.5):
    if labels == None: return False
    rels = related_words(word)
    intersect = set(rels) & set(map(lambda x: x[0],labels))
    if len(intersect) > 0 and \
        len(filter (lambda x: x[0] in intersect and \
                    x[1] >= conf_lvl, labels)) > 0:
        return True
    else: return False

#
