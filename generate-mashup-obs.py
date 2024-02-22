import audiofile
import rpp
import tqdm
import ffmpeg
from rpp import Element
import uuid
import os
import json
import threading

mashup_audio = r'D:\Temp\mashup.flac'
mashup_project = r'D:\Temp\mashup.rpp'

video_w = 2560
video_h = 1440
fps = 60
w = 8
h = 8
item_w, item_h = video_w // w, video_h // h

r = rpp.load(open(mashup_project, 'r', encoding='UTF-8'))

source_items = []
sources = []

now_id = 90

commands = []

tracks = [i for i in r.children if isinstance(i, Element) and i.tag == 'TRACK']
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

		x = ((index - 1) % w) * item_w
		y = ((index - 1) // w) * item_h
		now_uuid = str(uuid.uuid4())
		now_id += 1
		commands.append('ffmpeg -hwaccel cuda -i "{0}" -filter_complex "color=c=black:s={1}x{2}:r={3}:d={4},scale={1}:{2},setsar=16/9,setdar=16/9[black];[0:v]scale={1}:{2},setsar=16/9,setdar=16/9,trim=start={6}:end={7},setpts={8}*PTS[v0];[black][v0]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v h264_nvenc temp/{5}.mp4'.format(path, item_w, item_h, now_fps, pos, now_uuid, start, start + length, speed))
		source_items.append({
		    "name": "媒体源",
		    "source_uuid": now_uuid,
		    "visible": True,
		    "locked": False,
		    "rot": 0.0,
		    "pos": {
		        "x": x,
		        "y": y
		    },
		    "scale": {
		        "x": 1.0,
		        "y": 1.0
		    },
		    "align": 5,
		    "bounds_type": 0,
		    "bounds_align": 0,
		    "bounds": {
		        "x": 1.0,
		        "y": 1.0
		    },
		    "crop_left": 0,
		    "crop_top": 0,
		    "crop_right": 0,
		    "crop_bottom": 0,
		    "id": now_id,
		    "group_item_backup": False,
		    "scale_filter": "disable",
		    "blend_method": "default",
		    "blend_type": "normal",
		    "show_transition": {
		        "duration": 0
		    },
		    "hide_transition": {
		        "duration": 0
		    },
		    "private_settings": {}
		})
		sources.append({
            "prev_ver": 486604803,
            "name": "媒体源",
            "uuid": now_uuid,
            "id": "ffmpeg_source",
            "versioned_id": "ffmpeg_source",
            "settings": {
                "local_file": os.path.join(os.getcwd(), 'temp/{}.mp4'.format(now_uuid))
            },
            "mixers": 255,
            "sync": 0,
            "flags": 0,
            "volume": 0.0,
            "balance": 0.5,
            "enabled": True,
            "muted": False,
            "push-to-mute": False,
            "push-to-mute-delay": 0,
            "push-to-talk": False,
            "push-to-talk-delay": 0,
            "hotkeys": {
                "libobs.mute": [],
                "libobs.unmute": [],
                "libobs.push-to-mute": [],
                "libobs.push-to-talk": [],
                "MediaSource.Restart": [],
                "MediaSource.Play": [],
                "MediaSource.Pause": [],
                "MediaSource.Stop": []
            },
            "deinterlace_mode": 0,
            "deinterlace_field_order": 0,
            "monitoring_type": 0,
            "private_settings": {}
        })



sources = [{
    "prev_ver": 486604803,
    "name": "场景",
    "uuid": str(uuid.uuid4()),
    "id": "scene",
    "versioned_id": "scene",
    "settings": {
        "custom_size": False,
        "id_counter": now_id,
        "items": source_items
    },
    "mixers": 0,
    "sync": 0,
    "flags": 0,
    "volume": 1.0,
    "balance": 0.5,
    "enabled": True,
    "muted": False,
    "push-to-mute": False,
    "push-to-mute-delay": 0,
    "push-to-talk": False,
    "push-to-talk-delay": 0,
    "hotkeys": {
        "OBSBasic.SelectScene": [],
    },
    "deinterlace_mode": 0,
    "deinterlace_field_order": 0,
    "monitoring_type": 0,
    "private_settings": {}
}] + sources
open('result.json', 'w', encoding='UTF-8').write(json.dumps(sources, indent=4))


max_threads = 3
sema = threading.Semaphore(max_threads)
def do_ffmpeg(command):
	sema.acquire()
	os.system(command)
	sema.release()

for i in commands:
	threading.Thread(target=do_ffmpeg, args=(i,)).start()