import sys
import asyncio
from qasync import QEventLoop, QApplication
from .login import LoginWindow
from .main import MainWindow

def main(argv: list[str]):
    """登录"""
    app = QApplication(argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    login_event = asyncio.Event()
    result: list[tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []
    login_window = LoginWindow(result)
    login_window.closeEvent = lambda event: login_event.set()
    login_window.show()
    loop.run_until_complete(login_event.wait())
    if len(result) != 1:
        return 0
    
    """主循环"""
    main_window = MainWindow(*result[0])
    main_window.show()
    with loop:
        loop.create_task(main_window.listen())
        loop.create_task(main_window.record())
        loop.run_forever()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
