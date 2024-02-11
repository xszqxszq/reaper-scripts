import rpp
import cv2
import os
import tqdm
from rpp import Element
from moviepy.editor import *
from pathlib import Path

filename = r'F:\音MAD\工程\RPP工程\合作\2024新春宴\新春宴-最终鬼畜妹+UN.rpp'

r = rpp.load(open(filename, 'r', encoding='UTF-8'))

bay = set()

tracks = [i for i in r.children if isinstance(i, Element) and i.tag == 'TRACK']
for track in tqdm.tqdm(tracks):
	items = [i for i in track.children if isinstance(i, Element) and i.tag == 'ITEM']
	for item in items:
		path = [i for i in item.children if isinstance(i, Element) and i.tag == 'SOURCE'][0].children[0][1]
		bay.add(path)

size = 0

for file in tqdm.tqdm(bay):
	if os.path.exists(file):
		size += os.stat(file).st_size

print('总共 {} GB'.format(size / (1024 * 1024 * 1024)))