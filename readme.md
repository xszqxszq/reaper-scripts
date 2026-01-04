# Reaper-Scripts

一些在音MAD制作中利用 Reaper 工程文件进行自动化处理的脚本。

## 素材相关

### count-sources-total.py

估算 Reaper 工程中使用到的素材文件的总体积。

### extract-sources.py

裁切 Reaper 工程中使用到的视频片段，并渲染到指定目录中以便打包分发。

### extract-sources-specify-manually.py

基本同 `extract-sources.py`，但对于导入的提取了干声的音频，支持手动指定路径来替换为视频文件。

此脚本在制作[最终鬼畜全明星•BILIBILI【东方新春宴'24单品】](https://www.bilibili.com/video/BV17z421d7mj)这一作时编写而成，便于打包素材分发给各视频作者来协同制作，避免了传输上百 GB 的完整素材。

## Mashup/比较

### generate_mashup_exo.py

根据 Mashup 的 RPP 工程，按照网格一键摆放好各作品坐标位置，生成可以导入 AviUtl 1.16d 的 exo 文件。导入之后直接在 AviUtl 中渲染即可。

如果 Mashup 的视频数量过多，渲染将极其缓慢，更快的方案请参考 `generate_mashup_obs.py`。

### generate_mashup_exo_quick.py

与 `generate_mashup_exo.py` 功能相同，但会对比较视频进行预处理转码及拉伸分辨率，避免在 AviUtl 中出现大量视频物件使用缩放率导致的渲染缓慢。

事实上相较于上一脚本并不能加速多少，更快的方案请参考 `generate_mashup_obs.py`。

### generate_mashup_obs.py

根据 Mashup 的 RPP 工程，按照网格一键摆放好各作品坐标位置，生成可以导入 OBS Studio 的场景文件。导入后使用 OBS 录制一遍即可。

OBS 直接录制完全不会卡顿，所以为最佳方案。