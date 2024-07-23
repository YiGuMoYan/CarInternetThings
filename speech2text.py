import json
from queue import Queue
from threading import Thread

import pyaudio
import pyttsx3
import webrtcvad
from vosk import Model, KaldiRecognizer

from utils import jaccard_similarity

vad = webrtcvad.Vad()
vad.set_mode(2)  # 设置VAD模式，0为最不敏感，3为最敏感


def is_speech(data, sample_rate):
    return vad.is_speech(data, sample_rate)


class Speech2Text:
    CHANNELS = 1
    FRAME_RATE = 16000
    AUDIO_FORMAT = pyaudio.paInt16
    SAMPLE_SIZE = 2

    def __init__(self, call_name):
        # 音频数据流
        self.p = pyaudio.PyAudio()
        # 消息队列
        self.messages = Queue()
        # 文本生成队列
        self.recordings = Queue()
        # 唤醒词
        self.call_name = call_name
        # False 关闭状态，需要使用唤醒词唤醒 / True 开启状态，不需要使用唤醒词
        self.call_mode = False

        self.model = Model(model_path="./vosk-model-cn-0.22")
        self.rec = KaldiRecognizer(self.model, self.FRAME_RATE)
        self.rec.SetWords(True)

        self.chunk_duration_ms = 30
        self.chunk_size = int(self.FRAME_RATE * self.chunk_duration_ms / 1000)  # 以帧为单位的块大小

        self.start_recording()

    def record_microphone(self):
        stream = self.p.open(format=self.AUDIO_FORMAT,
                             channels=self.CHANNELS,
                             rate=self.FRAME_RATE,
                             input=True,
                             input_device_index=0,  # 这是麦克风的索引id
                             frames_per_buffer=self.chunk_size)

        frames = []
        silence_duration = 0
        silence_threshold = 1  # 停止录音的静音阈值（秒）

        while not self.messages.empty():
            data = stream.read(self.chunk_size)
            frames.append(data)

            if is_speech(data, self.FRAME_RATE):
                silence_duration = 0
            else:
                silence_duration += self.chunk_duration_ms / 1000

            if silence_duration > silence_threshold:
                break

        stream.stop_stream()
        stream.close()

        if frames:
            self.recordings.put(frames.copy())

    def start_recording(self):
        # 清空消息队列，确保每次重新启动录音和识别时都能添加新的消息
        while not self.messages.empty():
            self.messages.get()

        self.messages.put(True)  # 放入新的消息

        record = Thread(target=self.record_microphone)
        record.start()
        transcribe = Thread(target=self.speech_recognition)
        transcribe.start()

    def speech_recognition(self):
        while not self.messages.empty():
            frames = self.recordings.get()

            text = ""

            try:
                self.rec.AcceptWaveform(b''.join(frames))
                result = self.rec.Result()
                text = json.loads(result)["text"].replace(" ", "")

                if text == "" or text == " " or text is None:
                    self.start_recording()
                    continue

                jaccard = jaccard_similarity(text, self.call_name)

                print(type(text))
                print(text, jaccard)

            except Exception as e:
                print(e)
                self.start_recording()

            if jaccard > 0.5:
                pyttsx3.speak("我在")
                print("123")
                self.call_mode = True
                print("识别的文字", text)
                self.messages.put(True)  # 重新启动录音和识别
            elif self.call_mode and text != "" and text != " " and text is not None:
                print("识别的文字", text)
                pyttsx3.speak(text)
                self.call_mode = False
                self.messages.put(True)  # 重新启动录音和识别

            # 重新启动录音和识别
            self.start_recording()


speech_2_text = Speech2Text(call_name="小巴同学")
