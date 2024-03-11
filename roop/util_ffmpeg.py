
import os
import subprocess
import roop.globals
import roop.utilities as util

from typing import List, Any

def run_ffmpeg(args: List[str]) -> bool:
    commands = ['ffmpeg', '-hide_banner', '-hwaccel', 'auto', '-y', '-loglevel', roop.globals.log_level]
    commands.extend(args)
    print (" ".join(commands))
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except Exception as e:
        print(e)
    return False



def cut_video(original_video: str, cut_video: str, start_frame: int, end_frame: int):
    fps = util.detect_fps(original_video)
    start_time = start_frame / fps
    num_frames = end_frame - start_frame

    run_ffmpeg(['-ss',  str(start_time), '-i', original_video, '-c:v', roop.globals.video_encoder, '-c:a', 'aac', '-frames:v', str(num_frames), cut_video])

def join_videos(videos: List[str], dest_filename: str, simple: bool):
    if simple:
        txtfilename = util.resolve_relative_path('../temp')
        txtfilename = os.path.join(txtfilename, 'joinvids.txt')
        with open(txtfilename, "w", encoding="utf-8") as f:
            for v in videos:
                 v = v.replace('\\', '/')
                 f.write(f"file {v}\n")
        commands = ['-f', 'concat', '-safe', '0', '-i', f'{txtfilename}', '-vcodec', 'copy', f'{dest_filename}']
        run_ffmpeg(commands)

    else:
        inputs = []
        filter = ''
        for i,v in enumerate(videos):
            inputs.append('-i')
            inputs.append(v)
            filter += f'[{i}:v:0][{i}:a:0]'
        run_ffmpeg([" ".join(inputs), '-filter_complex', f'"{filter}concat=n={len(videos)}:v=1:a=1[outv][outa]"', '-map', '"[outv]"', '-map', '"[outa]"', dest_filename])    



def extract_frames(target_path : str, trim_frame_start, trim_frame_end, fps : float) -> bool:
    util.create_temp(target_path)
    temp_directory_path = util.get_temp_directory_path(target_path)
    commands = ['-i', target_path, '-q:v', '1', '-pix_fmt', 'rgb24', ]
    if trim_frame_start is not None and trim_frame_end is not None:
        commands.extend([ '-vf', 'trim=start_frame=' + str(trim_frame_start) + ':end_frame=' + str(trim_frame_end) + ',fps=' + str(fps) ])
    commands.extend(['-vsync', '0', os.path.join(temp_directory_path, '%06d.' + roop.globals.CFG.output_image_format)])
    return run_ffmpeg(commands)


def create_video(target_path: str, dest_filename: str, fps: float = 24.0, temp_directory_path: str = None) -> None:
    if temp_directory_path is None:
        temp_directory_path = util.get_temp_directory_path(target_path)
    run_ffmpeg(['-r', str(fps), '-i', os.path.join(temp_directory_path, f'%06d.{roop.globals.CFG.output_image_format}'), '-c:v', roop.globals.video_encoder, '-crf', str(roop.globals.video_quality), '-pix_fmt', 'yuv420p', '-vf', 'colorspace=bt709:iall=bt601-6-625:fast=1', '-y', dest_filename])
    return dest_filename


def create_gif_from_video(video_path: str, gif_path):
    from roop.capturer import get_video_frame

    fps = util.detect_fps(video_path)
    frame = get_video_frame(video_path)

    run_ffmpeg(['-i', video_path, '-vf', f'fps={fps},scale={frame.shape[0]}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse', '-loop', '0', gif_path])


def restore_audio(intermediate_video: str, original_video: str, trim_frame_start, trim_frame_end, final_video : str) -> None:
	fps = util.detect_fps(original_video)
	commands = [ '-i', intermediate_video ]
	if trim_frame_start is None and trim_frame_end is None:
		commands.extend([ '-c:a', 'copy' ])
	else:
		# if trim_frame_start is not None:
		# 	start_time = trim_frame_start / fps
		# 	commands.extend([ '-ss', format(start_time, ".2f")])
		# else:
		# 	commands.extend([ '-ss', '0' ])
		# if trim_frame_end is not None:
		# 	end_time = trim_frame_end / fps
		# 	commands.extend([ '-to', format(end_time, ".2f")])
		# commands.extend([ '-c:a', 'aac' ])
		if trim_frame_start is not None:
			start_time = trim_frame_start / fps
			commands.extend([ '-ss', format(start_time, ".2f")])
		else:
			commands.extend([ '-ss', '0' ])
		if trim_frame_end is not None:
			end_time = trim_frame_end / fps
			commands.extend([ '-to', format(end_time, ".2f")])
		commands.extend([ '-i', original_video, "-c",  "copy" ])

	commands.extend([ '-map', '0:v:0', '-map', '1:a:0?', '-shortest', final_video ])
	run_ffmpeg(commands)
