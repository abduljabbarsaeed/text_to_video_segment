
import speech_recognition as sr
import moviepy.editor as mp
import math
from pydub import AudioSegment
from pydub.silence import split_on_silence
import sys
import os

# check commandline arguments.
if(len(sys.argv) < 3):
    print("usage: python comment_segment.py <video file path> <text/comment to match in the video>")
    quit()

# get video file path from command line.
video_filepath = sys.argv[1]

# read video in memory by moviepy module
clip = mp.VideoFileClip(r""+video_filepath+"") 

# save the audio of a video in separate file 
clip.audio.write_audiofile(r""+video_filepath+".wav")

#reading from audio wav file
sound = AudioSegment.from_mp3(video_filepath+".wav")

# spliting audio files by silence
audio_chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-40 )

# loop through the audio_chunks list and save audio chunks as separate files.
list_of_files = []
for i, chunk in enumerate(audio_chunks):
   output_file = "chunk{0}.wav".format(i)
   list_of_files.append(output_file)
   chunk.export(output_file, format="wav")

#loop through each audio chunk file, recognize words and set time info.

start=0
end=0
list_of_chunk_results = []
for file in list_of_files:

    print(file)
    r=sr.Recognizer()
    r.energy_threshold = 300
    chunk_info={}
    audio = sr.AudioFile(file)
    with audio as source:

        lower_bound_duration = math.floor(source.DURATION)
        actual_duration = source.DURATION 
        set_duration = 0

        if (lower_bound_duration+0.5) <= actual_duration:
            set_duration = math.ceil(actual_duration)
        else:
            set_duration = lower_bound_duration

        if end == 0:
            end = set_duration
        else:
            start = end
            end = start + set_duration

        chunk_info["file_path"] = file
        chunk_info["start"] = start
        chunk_info["end"] = end
        chunk_info["duration"] = end - start
 
        r.adjust_for_ambient_noise(source,duration = 1)
        audio_file = r.record(source)
        result = r.recognize_google(audio_file,show_all=True,language="zh-CN")
        print(result)
        if len(result) == 0:
            chunk_info["words"] = [""]
        else:
            chunk_info["words"] = list(u""+result["alternative"][0]["transcript"]+"")
    
        list_of_chunk_results.append(chunk_info)
print(list_of_chunk_results)
# match words in input comment with audio chunks words recognized and saved in list.

input_words = list(u""+sys.argv[2]+"")
list_match_counts = []
for chunk  in list_of_chunk_results:
    count = 0
    for i in range(len(input_words)):
        for j in range(len(chunk["words"])):
            if input_words[i] == chunk["words"][j]:
                count += 1
                break
    list_match_counts.append(count)

print(list_match_counts)
# get the index of chunk having max word count matched.
max_count_index = list_match_counts.index(max(list_match_counts))
print(max_count_index)

# get that chunk from the list 
max_chunk = list_of_chunk_results[max_count_index]

# fet the video segment start time info in seconds.
segment_start = max_chunk["start"]
segment_end = max_chunk["end"]
print("ss= ",segment_start,"es= ",segment_end)
# currently segment is select from start till the end of complete video.
# in case if just need that specific segment to play then uncomment
# the set segment_end = max_chunk["end"] and pass it as a second parameter
# in this next instruction statement.

segment = clip.subclip(segment_start, segment_end)

# Finally show and play the segment.
segment.preview(fps = 20)

# Remove all audio files
for file in list_of_files:
    os.remove(file)
os.remove(video_filepath+".wav")
