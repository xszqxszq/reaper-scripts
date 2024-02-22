import audiofile
import rpp
import tqdm
import ffmpeg
from rpp import Element
import uuid
import os
import threading

mashup_audio = r'D:\Temp\mashup.flac'
mashup_project = r'D:\Temp\mashup.rpp'

video_w = 1920
video_h = 1080
fps = 60
w = 8
h = 8
item_w, item_h = video_w // w, video_h // h
x1 = -w // 2 * item_w + ((item_w / 2) if w % 2 == 0 else 0)
y1 = -h // 2 * item_h + ((item_h / 2) if h % 2 == 0 else 0)

exo = '''[exedit]
width={}
height={}
rate={}
scale=1
length={}
audio_rate=48000
audio_ch=2'''.format(video_w, video_h, fps, int(fps * audiofile.duration(mashup_audio)))

video = '''
[{0}]
start={1}
end={2}
layer={9}
group={9}
overlay=1
camera=0
[{0}.0]
_name=视频文件
播放位置={3}
播放速度={4:.2f}
循环播放=0
读取Alpha通道=0
file={5}
[{0}.1]
_name=标准属性
X={6:.1f}
Y={7:.1f}
Z=0.0
缩放率={8:.2f}
透明度=0.0
旋转=0.00
blend=0'''

r = rpp.load(open(mashup_project, 'r', encoding='UTF-8'))

tracks = [i for i in r.children if isinstance(i, Element) and i.tag == 'TRACK']

now_id = 0

commands = []

for index, track in tqdm.tqdm(enumerate(tracks)):
	items = [i for i in track.children if isinstance(i, Element) and i.tag == 'ITEM']
	for item in items:
		path = [i for i in item.children if isinstance(i, Element) and i.tag == 'SOURCE'][0].children[0][1]
		info = [stream for stream in ffmpeg.probe(path)['streams'] if stream['codec_type'] == 'video'][0]
		width, height, now_fps = info['width'], info['height'], int(info['r_frame_rate'].split('/')[0]) / int(info['r_frame_rate'].split('/')[1])
		pos = float([i for i in item.children if isinstance(i, list) and i[0] == 'POSITION'][0][1])
		start = float([i for i in item.children if isinstance(i, list) and i[0] == 'SOFFS'][0][1])
		length = float([i for i in item.children if isinstance(i, list) and i[0] == 'LENGTH'][0][1])
		speed = 1 / float([i for i in item.children if isinstance(i, list) and i[0] == 'PLAYRATE'][0][1])

		x = (now_id % w) * item_w
		y = (now_id // w) * item_h
		now_uuid = str(uuid.uuid4())
		commands.append('ffmpeg -hwaccel cuda -i "{0}" -filter_complex "color=c=black:s={1}x{2}:r={3}:d={4},scale={1}:{2},setsar=16/9,setdar=16/9[black];[0:v]scale={1}:{2},setsar=16/9,setdar=16/9,trim=start={6}:end={7},setpts={8}*PTS[v0];[black][v0]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v h264_nvenc temp/{5}.mp4'.format(path, item_w, item_h, now_fps, pos, now_uuid, start, start + length, speed))

		x = x1 + (now_id % w) * item_w
		y = y1 + (now_id // w) * item_h
		exo += video.format(now_id, 0, int(fps * audiofile.duration(mashup_audio)), 0, 100.0, os.path.join(os.getcwd(), 'temp/{}.mp4'.format(now_uuid)), x, y, 100.0, now_id + 1)
		now_id += 1

open('result.exo', 'w', encoding='gbk').write(exo)

max_threads = 4
sema = threading.Semaphore(max_threads)
def do_ffmpeg(command):
	sema.acquire()
	os.system(command)
	sema.release()

for i in commands:
	threading.Thread(target=do_ffmpeg, args=(i,)).start()