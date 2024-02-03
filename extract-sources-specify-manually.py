import rpp
import cv2
import os
import tqdm
from rpp import Element
from moviepy.editor import *
from pathlib import Path

if not os.path.exists('result'):
	os.mkdir('result')

filename = 'D:/Temp/test.rpp'

r = rpp.load(open(filename, 'r', encoding='UTF-8'))

bay = {}

tracks = [i for i in r.children if isinstance(i, Element) and i.tag == 'TRACK']
for track in tqdm.tqdm(tracks):
	items = [i for i in track.children if isinstance(i, Element) and i.tag == 'ITEM']
	for item in items:
		path = [i for i in item.children if isinstance(i, Element) and i.tag == 'SOURCE'][0].children[0][1]
		start = float([i for i in item.children if isinstance(i, list) and i[0] == 'SOFFS'][0][1])
		length = float([i for i in item.children if isinstance(i, list) and i[0] == 'LENGTH'][0][1])
		speed = float([i for i in item.children if isinstance(i, list) and i[0] == 'PLAYRATE'][0][1])
		end = start + length / speed
		if path not in bay:
			bay[path] = [start, end]
		bay[path][0] = min(bay[path][0], start)
		bay[path][1] = max(bay[path][1], end)

clips = {}
left = []

for video in tqdm.tqdm(bay):
	if video.split('.')[-1].lower() in ['mp4', 'mkv']:
		continue

	now = None
	filename = Path(video).stem.replace('_(Vocals)', '')
	if filename.startswith('1_'):
		videoPath = str(Path(video).parent / (filename[2:] + '.mp4'))
		if os.path.exists(videoPath):
			now = videoPath
		else:
			videoPath = str(Path(video).parent / (filename[2:] + '.mkv'))
			if os.path.exists(videoPath):
				now = videoPath
	if not now:
		print(video)
		now = input('请输入欲替换的素材路径：').replace('"', '')
	if now.strip() == '':
		left.append(video)
		continue

	clip = VideoFileClip(now)
	duration = clip.duration
	start = max(0, bay[video][0] - 5)
	end = min(duration, bay[video][1] + 5)

	clips[video] = clip.subclip(start, end)

for video in clips:
	filename = Path(video).stem
	clips[video].write_videofile('result/{}.mp4'.format(filename))

print('剩余以下素材未裁剪：')
print('\n'.join(left))