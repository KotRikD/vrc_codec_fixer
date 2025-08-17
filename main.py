from PySide6 import QtCore, QtWidgets
import sys
import subprocess
import os

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.font_normal = self.font()
        self.font_normal.setPointSize(18)

        self.font_bold = self.font()
        self.font_bold.setPointSize(18)
        self.font_bold.setBold(True)

        self.window().setFont(self.font_normal)
        
        self.av1 = QtWidgets.QLabel("AV1", alignment=QtCore.Qt.AlignLeft)
        self.av1_status = QtWidgets.QLabel("No", alignment=QtCore.Qt.AlignRight)
        self.av1_status.setFont(self.font_bold)
        self.av1_status.setStyleSheet('color: red')

        self.vp9 = QtWidgets.QLabel("VP9", alignment=QtCore.Qt.AlignLeft)
        self.vp9_status = QtWidgets.QLabel("No", alignment=QtCore.Qt.AlignRight)
        self.vp9_status.setFont(self.font_bold)
        self.vp9_status.setStyleSheet('color: red')

        self.dolby = QtWidgets.QLabel("Dolby", alignment=QtCore.Qt.AlignLeft)
        self.dolby_status = QtWidgets.QLabel("No", alignment=QtCore.Qt.AlignRight)
        self.dolby_status.setFont(self.font_bold)
        self.dolby_status.setStyleSheet('color: red')

        self.hevc = QtWidgets.QLabel("HEVC", alignment=QtCore.Qt.AlignLeft)
        self.hevc_status = QtWidgets.QLabel("No", alignment=QtCore.Qt.AlignRight)
        self.hevc_status.setFont(self.font_bold)
        self.hevc_status.setStyleSheet('color: red')

        self.button = QtWidgets.QPushButton("Install codecs")
        self.button.clicked.connect(self.install_codecs)

        # Добавляем текстовое поле для логов
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)

        self.av1_layout = QtWidgets.QHBoxLayout()
        self.av1_layout.addWidget(self.av1)
        self.av1_layout.addWidget(self.av1_status)

        self.vp9_layout = QtWidgets.QHBoxLayout()
        self.vp9_layout.addWidget(self.vp9)
        self.vp9_layout.addWidget(self.vp9_status)

        self.dolby_layout = QtWidgets.QHBoxLayout()
        self.dolby_layout.addWidget(self.dolby)
        self.dolby_layout.addWidget(self.dolby_status)

        self.hevc_layout = QtWidgets.QHBoxLayout()
        self.hevc_layout.addWidget(self.hevc)
        self.hevc_layout.addWidget(self.hevc_status)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(self.av1_layout)
        mainLayout.addLayout(self.vp9_layout)
        mainLayout.addLayout(self.dolby_layout)
        mainLayout.addLayout(self.hevc_layout)

        mainLayout.addWidget(self.button)
        mainLayout.addWidget(self.log_text)

        self.setLayout(mainLayout)
        
        # Проверяем кодеки при запуске
        self.check_codecs()

    def log_message(self, message):
        self.log_text.setStyleSheet("font-size: 14px")
        self.log_text.append(f"[{QtCore.QTime.currentTime().toString('HH:mm:ss')}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def check_winget_available(self):
        try:
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def install_via_winget(self):
        packages = [
            "9n4d0msmp0pt", # VP9
            "9mvzqvxjbq9v", # AV1
            "9nvjqjbdkn97", # Dolby
        ]
        
        for package in packages:
            try:
                self.log_message(f"Устанавливаю пакет {package} через winget...")
                result = subprocess.run(['winget', 'install', package, '--accept-source-agreements', '--accept-package-agreements'], 
                                      capture_output=True, text=True, timeout=300, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    self.log_message(f"Пакет {package} успешно установлен")
                    continue

                if result.returncode == 2316632107:
                    self.log_message(f"Пакет {package} уже установлен")
                    continue

                self.log_message(f"Ошибка установки пакета {package}: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.log_message(f"Таймаут при установке пакета {package}")
            except Exception as e:
                self.log_message(f"Ошибка при установке пакета {package}: {e}")

    def install_via_powershell(self, script: str):
        try:
            script_path = get_resource_path(f'cmd/{script}')            
            cmd_dir = get_resource_path('cmd')

            self.log_message(script_path)
            self.log_message(cmd_dir)

            result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path], 
                                  cwd=cmd_dir, capture_output=True, text=True, timeout=300, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                self.log_message(f"PowerShell скрипт успешно выполнен: {result.stdout}")
                return

            self.log_message(f"Ошибка выполнения PowerShell скрипта: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.log_message("Таймаут при выполнении PowerShell скрипта")
        except Exception as e:
            self.log_message(f"Ошибка при запуске PowerShell скрипта: {e}")

    def install_codecs(self):
        self.button.setEnabled(False)
        self.button.setText("Installing...")
        self.log_text.clear()

        try:
            if self.check_winget_available():
                self.log_message("winget.exe доступен, устанавливаю через него...")
                self.install_via_winget()
                self.install_via_powershell('InstallHevc.ps1')
            else:
                self.log_message("winget.exe недоступен, запускаю PowerShell скрипт...")
                self.install_via_powershell('InstallCodecs.ps1')
        finally:
            self.button.setEnabled(True)
            self.button.setText("Install codecs")
            
        # Проверяем кодеки после установки
        self.log_message("Проверяю кодеки после установки...")
        self.check_codecs()

    def check_codecs(self):
        self.log_message("Проверяю наличие кодеков...")

        # Проверяем AV1
        av1_installed = self.check_codec_template("AV1", "av1", "9n4d0msmp0pt")
        self.update_codec_status(self.av1_status, av1_installed, "AV1")

        # Проверяем VP9
        vp9_installed = self.check_codec_template("VP9", "vp9", "9mvzqvxjbq9v")
        self.update_codec_status(self.vp9_status, vp9_installed, "VP9")

        # Проверяем Dolby
        dolby_installed = self.check_codec_template("Dolby", "dolby", "9nvjqjbdkn97")
        self.update_codec_status(self.dolby_status, dolby_installed, "Dolby")

        # Проверяем HEVC
        hevc_installed = self.check_codec_template("HEVC", "hevc", "9n4wgh0z6vhq")
        self.update_codec_status(self.hevc_status, hevc_installed, "HEVC")

        self.log_message("Проверка кодеков завершена")

    def check_codec_template(self, codec_name, codec_lower, winget_id):
        try:
            try:
                result = subprocess.run(['winget', 'list', winget_id], 
                                      capture_output=True, text=True, timeout=5, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0 and winget_id in result.stdout.lower():
                    return True
            except Exception:
                pass

            try:
                result = subprocess.run(['powershell', '-Command', f'Get-AppxPackage | Where-Object {{$_.Name -like "*{codec_lower}*" -or $_.PackageFullName -like "*{codec_lower}*"}}'], 
                                      capture_output=True, text=True, timeout=10, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except Exception:
                pass
        except Exception as e:
            self.log_message(f"Ошибка при проверке {codec_name}: {e}")

        return False

    def check_av1_codec(self):
        return self.check_codec_template("AV1", "av1", "9n4d0msmp0pt")

    def check_vp9_codec(self):
        return self.check_codec_template("VP9", "vp9", "9mvzqvxjbq9v")

    def check_dolby_codec(self):
        return self.check_codec_template("Dolby", "dolby", "9nvjqjbdkn97")

    def check_hevc_codec(self):
        return self.check_codec_template("HEVC", "hevc", "9nvjqjbdkn97")

    def update_codec_status(self, status_label, is_installed, codec_name):
        if is_installed:
            status_label.setText("Yes")
            status_label.setStyleSheet('color: green')
            self.log_message(f"Кодек {codec_name} найден в системе")
            return

        status_label.setText("No")
        status_label.setStyleSheet('color: red')
        self.log_message(f"Кодек {codec_name} не найден в системе")

def main():
    # Prints the Qt version used to compile PySide6
    print(QtCore.__version__)

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.setWindowTitle("VRChat Codec Fixer")
    widget.setFixedSize(QtCore.QSize(500, 350))
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
