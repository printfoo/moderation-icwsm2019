#!/usr/local/bin/python3

import requests
import os, sys, json, random, time
import pandas as pd
import multiprocessing as mp

# youtube crawler
class youtubeCrawler:
    
    # initialization
    def __init__(self, keys, id, save_path):
        self.keys = keys
        self.id = id
        self.save_path = save_path
        self.key_update()
        self.save_file = open(os.path.join(self.save_path, str(self.id)), "w")
        self.params = {"id": self.id, "key": self.key, "part": "snippet,statistics"}
        self.base = "https://www.googleapis.com/youtube/v3/videos"
    
    # save json to file
    def save(self):
        self.js["videoId"] = self.id
        self.save_file.write(json.dumps(self.js) + "\n")
    
    # get next key
    def key_update(self):
        try:
            self.key = self.keys[0]
        except IndexError:
            print("No usable keys left.")
            sys.exit()

    # get a response
    def get(self):
        self.res = requests.get(self.base, params = self.params)
        while self.res.status_code == 400: # 400 is an incidental error, try again until good
            time.sleep(1) # be gentle
            self.res = requests.get(self.base, params = self.params)
        if self.res.status_code > 400:
            print(self.res.content)
        self.js = json.loads(self.res.content)
        self.save()
        self.save_file.close()

# get youtube video ids from factcheck data
def get_ids(id_path):
    factcheck = pd.read_csv(id_path)
    factcheck = factcheck[factcheck["site"] == "youtube"]
    return list(factcheck["social_id"].drop_duplicates().values)

# get usable youtube keys
def get_keys(key_path):
    with open(key_path, "r") as key_file:
        keys = key_file.read().strip("\n").split("\n")
    return keys

# create youtube crawler class and start crawling
def create_youtube_crawler(keys, id, save_path):
    youtube = youtubeCrawler(keys, id, save_path)
    youtube.get()

if __name__ == "__main__":
    
    # get path
    sys_path = sys.path[0]
    sep = sys_path.find("src")
    file_path = sys_path[0:sep]
    
    # get all video ids to crawl
    id_path = os.path.join(file_path, "data", "2nd_crawl", "factcheck.csv")
    ids = get_ids(id_path)
    ids = [id for id in ids if id]

    # get all usable keys
    key_path = os.path.join(file_path, "resources", "youtube.keys")
    keys = get_keys(key_path)

    # intilize save path
    save_path = os.path.join(file_path, "data", "youtube_info", "youtube_name_id_raw")
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    # crawler initilization
    for id in ids:
        p = mp.Process(target = create_youtube_crawler, args = (keys, id, save_path))
        p.start()
