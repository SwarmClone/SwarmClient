import asyncio
import sounddevice as sd
from librosa import resample
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,

    QVBoxLayout,

    QLabel,
    QPushButton
)

class MainWindow(QMainWindow):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        super().__init__()
        self.reader = reader
        self.writer = writer
        self.recording = False

        self.setWindowTitle("蜂群克隆计划")
        widget = QWidget()
        self.setCentralWidget(widget)

        # 上下排列
        layout = QVBoxLayout(widget)

        # 显示语音识别的文字
        self.text_label = QLabel("")
        layout.addWidget(self.text_label)

        # 录音按钮
        self.record_button = QPushButton("录音已停止")
        self.record_button.clicked.connect(lambda: asyncio.ensure_future(self.start_recording()))
        layout.addWidget(self.record_button)
    
    async def stop_recording(self):
        self.recording = False
        self.record_button.setText("录音已停止")
        self.record_button.clicked.disconnect()
        self.record_button.clicked.connect(lambda: asyncio.ensure_future(self.start_recording()))
    
    async def start_recording(self):
        self.recording = True
        self.record_button.setText("正在录音")
        self.record_button.clicked.disconnect()
        self.record_button.clicked.connect(lambda: asyncio.ensure_future(self.stop_recording()))

    async def record(self):
        SAMPLE_RATE = 44100 # 采样率44.1k，因为一些设备不支持16k采样率
        SAMPLE_TIME = 0.1 # 0.1s读一次
        with sd.InputStream(channels=1, dtype="float32", samplerate=SAMPLE_RATE) as s:
            while True:
                samples, _ = await asyncio.to_thread(s.read, int(SAMPLE_RATE * SAMPLE_TIME))
                audio = resample(samples.reshape(-1), orig_sr=SAMPLE_RATE, target_sr=16000)
                if not self.recording:
                    audio *= 0 # 没开麦 = 静音
                self.writer.write(audio.tobytes())
                await self.writer.drain()
    
    async def listen(self):
        while True:
            text = await self.reader.read(1024)
            self.text_label.setText(text.decode().strip())
