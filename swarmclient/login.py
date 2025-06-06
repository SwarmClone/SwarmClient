import asyncio
import json
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,

    QFormLayout,

    QLineEdit,
    QLabel,
    QPushButton
)

class LoginWindow(QMainWindow):
    def __init__(self, result: list[tuple[asyncio.StreamReader, asyncio.StreamWriter]]):
        super().__init__()
        self.result = result

        self.setWindowTitle("登录 - 蜂群克隆计划")
        widget = QWidget()
        self.setCentralWidget(widget)

        # 创建表单
        form = QFormLayout(widget)

        # IP 地址输入框
        ip_label = QLabel("IP 地址")
        self.ip_input = QLineEdit()
        self.ip_input.setText("127.0.0.1")
        form.addRow(ip_label, self.ip_input)

        # 端口输入框
        port_label = QLabel("端口")
        self.port_input = QLineEdit()
        self.port_input.setText("8004")
        form.addRow(port_label, self.port_input)

        # 用户名输入框
        username_label = QLabel("用户名")
        self.username_input = QLineEdit()
        form.addRow(username_label, self.username_input)

        # 密码输入框
        password_label = QLabel("密码")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow(password_label, self.password_input)

        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(lambda: asyncio.ensure_future(self.login()))
        form.addRow(self.login_button)
    
    async def login(self):
        self.login_button.setEnabled(False)
        self.login_button.setText("正在登录……")

        ip = self.ip_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        password = self.password_input.text()
        login_msg = json.dumps({
            "name": username,
            "passwd": password
        })

        try:
            reader, writer = await asyncio.open_connection(ip, port)
        except ConnectionRefusedError:
            msg_box = QMessageBox()
            msg_box.setText("无法连接，请检查IP和端口号")
            msg_box.exec()
            self.login_button.setEnabled(True)
            self.login_button.setText("登录")
            return
        
        writer.write(login_msg.encode())
        await writer.drain()
        response = (await reader.readline()).decode().strip()
        match response:
            case "OK":
                self.result.append((reader, writer))
                self.close()
            case "WRUSR":
                msg_box = QMessageBox()
                msg_box.setText("用户名不存在")
                msg_box.exec()
                self.login_button.setEnabled(True)
                self.login_button.setText("登录")
            case "WRPWD":
                msg_box = QMessageBox()
                msg_box.setText("密码错误")
                msg_box.exec()
                self.login_button.setEnabled(True)
                self.login_button.setText("登录")
            case _:
                msg_box = QMessageBox()
                msg_box.setText("对方不是正确的服务器，请检查IP和端口号")
                msg_box.exec()
                self.login_button.setEnabled(True)
                self.login_button.setText("登录")
