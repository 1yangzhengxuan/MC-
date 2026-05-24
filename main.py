import sys
import os
import zipfile

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QFileDialog,
)

from PyQt6.QtGui import (
    QFont,
    QDragEnterEvent,
    QDropEvent,
)

from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # =========================
        # 基础窗口
        # =========================

        self.setAcceptDrops(True)

        self.resize(980, 640)

        self.setMinimumSize(860, 560)
        self.setMaximumSize(1200, 800)

        self.setWindowTitle("MC Crash Helper")

        QApplication.setFont(
            QFont("Microsoft YaHei UI", 10)
        )

        # =========================
        # 配色
        # =========================

        BG = "#f5f7fb"
        CARD = "#ffffff"
        PRIMARY = "#4285F4"

        TEXT = "#202124"
        SUBTEXT = "#5f6368"

        BORDER = "#dadce0"

        # =========================
        # 主容器
        # =========================

        central = QWidget()
        self.setCentralWidget(central)

        central.setStyleSheet(f"""
            background:{BG};
        """)

        root = QVBoxLayout(central)

        root.setContentsMargins(
            28,
            22,
            28,
            22
        )

        root.setSpacing(22)

        # =========================
        # 顶部
        # =========================

        topLayout = QHBoxLayout()

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(4)

        self.titleLabel = QLabel()

        self.titleLabel.setStyleSheet(f"""
            font-size:38px;
            font-weight:700;
            color:{TEXT};
        """)

        self.subtitleLabel = QLabel()

        self.subtitleLabel.setStyleSheet(f"""
            font-size:18px;
            color:{SUBTEXT};
        """)

        titleLayout.addWidget(self.titleLabel)
        titleLayout.addWidget(self.subtitleLabel)

        topLayout.addLayout(titleLayout)

        topLayout.addStretch()

        # =========================
        # 语言切换
        # =========================

        self.languageBox = QComboBox()

        self.languageBox.addItems([
            "简体中文",
            "English"
        ])

        self.languageBox.setFixedSize(150, 42)

        self.languageBox.setStyleSheet(f"""
QComboBox{{
    background:white;
    border:1px solid {BORDER};
    border-radius:21px;

    padding-left:16px;

    font-size:15px;
    color:{TEXT};
}}

QComboBox:hover{{
    border:1px solid {PRIMARY};
}}

QComboBox::drop-down{{
    border:none;
    width:28px;
}}

QComboBox::down-arrow{{
    image:none;
}}

QComboBox QAbstractItemView{{
    background:white;

    border:1px solid {BORDER};

    border-radius:12px;

    padding:6px;

    selection-background-color:#e8f0fe;

    outline:none;
}}
""")

        topLayout.addWidget(self.languageBox)

        root.addLayout(topLayout)

        # =========================
        # 卡片区域
        # =========================

        card = QWidget()

        card.setStyleSheet(f"""
            background:{CARD};
            border-radius:28px;
        """)

        cardLayout = QVBoxLayout(card)

        cardLayout.setContentsMargins(
            28,
            28,
            28,
            28
        )

        cardLayout.setSpacing(18)

        # =========================
        # 按钮
        # =========================

        self.selectButton = QPushButton()

        self.selectButton.setMinimumHeight(62)

        self.selectButton.setStyleSheet(f"""
QPushButton{{
    background:{PRIMARY};

    color:white;

    border:none;

    border-radius:20px;

    font-size:18px;
    font-weight:600;
}}

QPushButton:hover{{
    background:#5a95f5;
}}

QPushButton:pressed{{
    background:#3b78e0;
}}
""")

        cardLayout.addWidget(self.selectButton)

        # =========================
        # 拖拽提示
        # =========================

        self.dragLabel = QLabel()

        self.dragLabel.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.dragLabel.setStyleSheet(f"""
            font-size:15px;
            color:{SUBTEXT};
        """)

        cardLayout.addWidget(self.dragLabel)

        # =========================
        # 输出框
        # =========================

        self.resultBox = QTextEdit()

        self.resultBox.setReadOnly(True)

        self.resultBox.setStyleSheet(f"""
QTextEdit{{
    background:#f8f9fa;

    border:none;

    border-radius:20px;

    padding:18px;

    font-size:15px;

    color:{TEXT};
}}
""")

        cardLayout.addWidget(self.resultBox)

        root.addWidget(card)

        # =========================
        # 信号绑定
        # =========================

        self.selectButton.clicked.connect(
            self.selectLogFile
        )

        self.languageBox.currentTextChanged.connect(
            self.updateLanguage
        )

        # =========================
        # 默认语言
        # =========================

        self.currentLanguage = "zh"

        self.updateLanguage()

    # =========================================================
    # 多语言
    # =========================================================

    def updateLanguage(self):

        if self.languageBox.currentText() == "English":

            self.currentLanguage = "en"

            self.titleLabel.setText(
                "MC Crash Helper"
            )

            self.subtitleLabel.setText(
                "Make Minecraft crashes understandable"
            )

            self.selectButton.setText(
                "Select Log File"
            )

            self.dragLabel.setText(
                "You can drag log or ZIP files here"
            )

            self.resultBox.setPlaceholderText(
                "Waiting for log analysis..."
            )

        else:

            self.currentLanguage = "zh"

            self.titleLabel.setText(
                "MC崩溃助手"
            )

            self.subtitleLabel.setText(
                "让MC报错不再像天书"
            )

            self.selectButton.setText(
                "选择日志文件"
            )

            self.dragLabel.setText(
                "也可以直接拖拽日志或ZIP压缩包到窗口"
            )

            self.resultBox.setPlaceholderText(
                "等待分析日志..."
            )

    # =========================================================
    # 选择文件
    # =========================================================

    def selectLogFile(self):

        path, _ = QFileDialog.getOpenFileName(
            self,

            "选择日志",

            "",

            "日志文件 (*.log *.txt *.zip)"
        )

        if not path:
            return

        self.analyzeLog(path)

    # =========================================================
    # ZIP / LOG读取
    # =========================================================

    def readLogFile(self, path):

        # ZIP
        if path.lower().endswith(".zip"):

            try:

                with zipfile.ZipFile(path, "r") as zipf:

                    file_list = zipf.namelist()

                    priority = [
                        "crash",
                        "latest.log",
                        "debug.log",
                        "hs_err",
                        ".log",
                        ".txt"
                    ]

                    selected = None

                    for key in priority:

                        for file in file_list:

                            lower = file.lower()

                            if key in lower:

                                selected = file

                                break

                        if selected:
                            break

                    if not selected:
                        return ""

                    with zipf.open(selected) as f:

                        return f.read().decode(
                            "utf-8",
                            errors="ignore"
                        )

            except Exception as e:

                print(e)

                return ""

        # 普通文件
        else:

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    return f.read()

            except:
                return ""

    # =========================================================
    # 日志分析
    # =========================================================

    def analyzeLog(self, path):

        log = self.readLogFile(path)

        if not log:

            if self.currentLanguage == "zh":

                self.resultBox.setText(
                    "无法读取日志文件"
                )

            else:

                self.resultBox.setText(
                    "Unable to read log file"
                )

            return

        issues = []

        lower = log.lower()

        # =====================================================
        # 内存不足
        # =====================================================

        if (
            "outofmemoryerror" in lower
            or "java heap space" in lower
        ):

            if self.currentLanguage == "zh":

                issues.append(
                    "【检测到】内存不足\n\n"
                    "可能原因：\n"
                    "- 分配给Minecraft的内存太小\n"
                    "- Mod数量过多\n"
                    "- 光影占用过高\n\n"
                    "建议解决方案：\n"
                    "1. 提高JVM内存\n"
                    "2. 删除大型Mod\n"
                    "3. 关闭高强度光影"
                )

            else:

                issues.append(
                    "[Detected] Out Of Memory\n\n"
                    "Possible Causes:\n"
                    "- Too little RAM allocated\n"
                    "- Too many mods\n"
                    "- Heavy shaders\n\n"
                    "Suggested Solutions:\n"
                    "1. Increase JVM RAM\n"
                    "2. Remove heavy mods\n"
                    "3. Disable shaders"
                )

        # =====================================================
        # Mod前置缺失
        # =====================================================

        if (
            "noclassdeffounderror" in lower
            or "classnotfoundexception" in lower
        ):

            if self.currentLanguage == "zh":

                issues.append(
                    "【检测到】Mod缺少前置\n\n"
                    "可能原因：\n"
                    "- 缺少依赖Mod\n"
                    "- Mod版本错误\n"
                    "- Forge/Fabric版本不匹配"
                )

            else:

                issues.append(
                    "[Detected] Missing Dependency Mod\n\n"
                    "Possible Causes:\n"
                    "- Missing dependency\n"
                    "- Wrong mod version\n"
                    "- Loader version mismatch"
                )

        # =====================================================
        # Mod冲突
        # =====================================================

        if (
            "mixin" in lower
            or "failed loading" in lower
            or "exception loading" in lower
        ):

            if self.currentLanguage == "zh":

                issues.append(
                    "【检测到】Mod冲突\n\n"
                    "可能原因：\n"
                    "- 两个Mod功能冲突\n"
                    "- Mod版本不兼容\n"
                    "- Fabric/Forge API问题"
                )

            else:

                issues.append(
                    "[Detected] Mod Conflict\n\n"
                    "Possible Causes:\n"
                    "- Mod conflicts\n"
                    "- Incompatible versions\n"
                    "- Loader API issues"
                )

        # =====================================================
        # Java版本错误
        # =====================================================

        if (
            "unsupportedclassversionerror" in lower
        ):

            if self.currentLanguage == "zh":

                issues.append(
                    "【检测到】Java版本错误\n\n"
                    "可能原因：\n"
                    "- Java版本过低\n"
                    "- Java版本过高"
                )

            else:

                issues.append(
                    "[Detected] Wrong Java Version\n\n"
                    "Possible Causes:\n"
                    "- Java version too low\n"
                    "- Java version too high"
                )

        # =====================================================
        # 未识别
        # =====================================================

        if not issues:

            if self.currentLanguage == "zh":

                issues.append(
                    "未识别具体错误\n\n"
                    "后续版本可接入AI分析。"
                )

            else:

                issues.append(
                    "Unknown error\n\n"
                    "AI analysis can be added later."
                )

        # =====================================================
        # 输出
        # =====================================================

        self.resultBox.setText(
            "\n\n====================\n\n".join(issues)
        )

    # =========================================================
    # 拖拽
    # =========================================================

    def dragEnterEvent(
        self,
        event: QDragEnterEvent
    ):

        if event.mimeData().hasUrls():

            event.acceptProposedAction()

    def dropEvent(
        self,
        event: QDropEvent
    ):

        urls = event.mimeData().urls()

        if not urls:
            return

        path = urls[0].toLocalFile()

        self.analyzeLog(path)

        event.acceptProposedAction()


# =============================================================
# 启动
# =============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())