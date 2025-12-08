import sys
import os
import tempfile
import time
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QListWidget, QListWidgetItem, 
                             QFileDialog, QMessageBox, QProgressBar, QLabel, QScrollArea, 
                             QFrame, QSizePolicy, QDialog, QTextBrowser)
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QPixmap, QImage

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed


def process_single_image(image_params):
    """
    处理单个图像的函数，用于多进程处理
    返回处理后的图像信息
    """
    image_path, temp_dir = image_params
    try:
        # 打开并分析图像
        img = Image.open(image_path)
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        
        # 如果是横图，则使用 landscape 页面方向
        if aspect_ratio > 1:
            # 横向页面
            pdf_img = img.rotate(90, expand=True)
            img_width, img_height = img_height, img_width
            is_landscape = True
        else:
            # 纵向页面
            pdf_img = img
            is_landscape = False
            
        # 为了更好地利用内存和CPU，预处理图像到适合PDF的尺寸
        target_size = (1200, 1200)  # 设置一个合适的最大尺寸
        pdf_img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # 创建临时文件保存处理后的图像
        temp_filename = os.path.join(temp_dir, os.path.basename(image_path) + "_processed.png")
        pdf_img.save(temp_filename, "PNG", optimize=True)
        
        return {
            'original_path': image_path,
            'processed_path': temp_filename,
            'width': pdf_img.width,
            'height': pdf_img.height,
            'is_landscape': is_landscape,
            'aspect_ratio': aspect_ratio if not is_landscape else 1/aspect_ratio
        }
    except Exception as e:
        return {'error': str(e), 'original_path': image_path}


class ImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("图片预览")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 文件名标签
        filename_label = QLabel(Path(self.image_path).name)
        filename_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(filename_label)
        
        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.pixmap = QPixmap(self.image_path)
        self.update_image()
        layout.addWidget(self.image_label)
        
        self.setLayout(layout)
        
    def update_image(self):
        if not self.pixmap.isNull():
            # 缩放图片以适应窗口，同时保持纵横比
            scaled_pixmap = self.pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()


class ImageListItem(QListWidgetItem):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setSizeHint(QSize(120, 150))
        
        
class DraggableListWidget(QListWidget):
    item_dropped = pyqtSignal()
    item_clicked = pyqtSignal(str)  # 发送图片路径信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setMovement(QListWidget.Snap)
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.Adjust)
        
    def dropEvent(self, event):
        super().dropEvent(event)
        self.item_dropped.emit()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item and isinstance(item, ImageListItem):
            self.item_clicked.emit(item.image_path)


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    finished_signal = pyqtSignal(str)  # result filename
    error_signal = pyqtSignal(str)     # error message
    
    def __init__(self, images, temp_dir):
        super().__init__()
        self.images = images
        self.temp_dir = temp_dir
        
    def run(self):
        try:
            self.generate_pdf()
        except Exception as e:
            self.error_signal.emit(str(e))
            
    def generate_pdf(self):
        # 获取保存路径
        filename, _ = QFileDialog.getSaveFileName(None, "保存PDF文件", "", "PDF Files (*.pdf)")
        if not filename:
            return
            
        if not filename.endswith('.pdf'):
            filename += '.pdf'
            
        # 记录开始时间
        start_time = time.time()
        
        # 使用多进程处理所有图像
        worker_count = min(multiprocessing.cpu_count() + 2, len(self.images))
        
        # 更新进度条
        self.progress_updated.emit(0, len(self.images), "正在处理图片...")
        
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            # 准备任务数据
            tasks = [(image_path, self.temp_dir) for image_path in self.images]
            
            # 提交所有任务
            future_to_image = {executor.submit(process_single_image, task): i for i, task in enumerate(tasks)}
            
            completed = 0
            # 收集结果
            all_results = []
            for future in as_completed(future_to_image):
                result = future.result()
                all_results.append(result)
                completed += 1
                self.progress_updated.emit(completed, len(self.images), f"已处理 {completed}/{len(self.images)} 张图片")
        
        # 按原始顺序排序处理后的图像
        processed_images = sorted(all_results, key=lambda x: self.images.index(x['original_path']) if 'original_path' in x else float('inf'))
        
        # 更新进度
        self.progress_updated.emit(0, 0, "正在创建PDF...")
        
        # 创建PDF
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            for i, img_info in enumerate(processed_images):
                if 'error' in img_info:
                    print(f"处理图片出错 {img_info.get('original_path', 'unknown')}: {img_info['error']}")
                    continue
                    
                if img_info.get('is_landscape'):
                    page_size = (height, width)  # 横向页面
                else:
                    page_size = letter  # 纵向页面
                    
                c.setPageSize(page_size)
                pdf_width, pdf_height = page_size

                img_width = img_info['width']
                img_height = img_info['height']

                scale = min(pdf_width / img_width, pdf_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale

                x = (pdf_width - new_width) / 2
                y = (pdf_height - new_height) / 2

                c.drawImage(img_info['processed_path'], x, y, new_width, new_height)
                c.showPage()
                
                # 更新进度
                self.progress_updated.emit(i+1, len(processed_images), f"正在添加第 {i+1}/{len(processed_images)} 张图片到PDF")

            c.save()
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            self.finished_signal.emit(f"{filename}\n耗时: {elapsed_time:.2f} 秒")
        except Exception as e:
            self.error_signal.emit(str(e))


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("PDF图片生成器")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # 信息文本
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        about_text = """
        <h2>PDF图片生成器</h2>
        <p><b>版本:</b> 1.0</p>
        <p><b>描述:</b> 这是一个免费开源的PDF生成工具，可以将多张图片合并为一个PDF文件。</p>
        
        <p><b>许可证:</b> MIT License</p>
        <p>版权所有 (c) 2025 JollSnow</p>
        
        <p><b>作者:</b> JollSnow</p>
        <p><b>AI协助:</b> 由通义千问（Qwen）AI模型协助编写</p>
        
        <p><b>开源声明:</b> 本软件是免费开源软件，遵循MIT许可证发布。</p>
        
        <p><b>免责声明:</b> 本软件按"现状"提供，不提供任何形式的担保。作者不对因使用本软件而产生的任何直接或间接损害负责。</p>
        
        <p>更多信息请访问项目地址。</p>
        """
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)


class PDFGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF生成器")
        self.setGeometry(100, 100, 900, 700)
        
        self.images = []
        self.temp_dir = tempfile.mkdtemp()
        
        self.init_ui()
        
    def init_ui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("选择图片生成PDF")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加图片")
        self.add_button.clicked.connect(self.add_images)
        
        self.clear_button = QPushButton("清空图片")
        self.clear_button.clicked.connect(self.clear_images)
        
        self.generate_button = QPushButton("生成PDF")
        self.generate_button.clicked.connect(self.generate_pdf)
        
        self.about_button = QPushButton("关于")
        self.about_button.clicked.connect(self.show_about)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.about_button)
        
        main_layout.addLayout(button_layout)
        
        # 图片列表
        self.image_list = DraggableListWidget()
        self.image_list.item_dropped.connect(self.update_image_order)
        self.image_list.item_clicked.connect(self.show_image)
        self.image_list.setSpacing(10)
        self.image_list.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        main_layout.addWidget(QLabel("图片预览 (可拖拽排序，点击图片可放大查看):"))
        main_layout.addWidget(self.image_list)
        
        # 进度条
        self.progress_widget = QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_widget)
        
        self.progress_label = QLabel("正在处理...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QLabel()
        self.progress_text.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_text)
        
        main_layout.addWidget(self.progress_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def add_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        for file_path in file_paths:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.images.append(file_path)
                self.add_image_item(file_path)
                
        self.statusBar().showMessage(f"已添加 {len(self.images)} 张图片")
        
    def add_image_item(self, image_path):
        item = ImageListItem(image_path)
        self.image_list.addItem(item)
        
        # 创建自定义的widget用于显示图片和文件名
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 图片预览
        label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 文件名
        name_label = QLabel(Path(image_path).name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setToolTip(image_path)
        name_label.setStyleSheet("font-size: 10px;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 删除按钮
        delete_button = QPushButton("删除")
        delete_button.clicked.connect(lambda _, i=len(self.images)-1: self.remove_image(i))
        layout.addWidget(delete_button)
        
        self.image_list.setItemWidget(item, widget)
        
    def remove_image(self, index):
        if 0 <= index < len(self.images):
            del self.images[index]
            item = self.image_list.takeItem(index)
            del item
            self.statusBar().showMessage(f"已删除图片，剩余 {len(self.images)} 张")
            
    def clear_images(self):
        self.images.clear()
        self.image_list.clear()
        self.statusBar().showMessage("已清空所有图片")
        
    def update_image_order(self):
        # 更新图片顺序
        new_order = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if isinstance(item, ImageListItem):
                new_order.append(item.image_path)
        self.images = new_order
        self.statusBar().showMessage(f"已更新图片顺序，共 {len(self.images)} 张图片")
        
    def show_image(self, image_path):
        viewer = ImageViewer(image_path, self)
        viewer.show()
        
    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def generate_pdf(self):
        if not self.images:
            QMessageBox.warning(self, "警告", "请先添加图片!")
            return
            
        self.progress_widget.setVisible(True)
        self.add_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.generate_button.setEnabled(False)
        
        # 启动工作线程
        self.worker_thread = WorkerThread(self.images, self.temp_dir)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.on_generation_finished)
        self.worker_thread.error_signal.connect(self.on_generation_error)
        self.worker_thread.start()
        
    def update_progress(self, current, total, text):
        self.progress_text.setText(text)
        if total > 0:
            progress_percent = (current / total) * 100
            self.progress_bar.setValue(int(progress_percent))
        else:
            self.progress_bar.setValue(0)
            
    def on_generation_finished(self, message):
        self.progress_widget.setVisible(False)
        self.add_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.generate_button.setEnabled(True)
        
        filename_info = message.split('\n')[0]
        QMessageBox.information(self, "成功", f"PDF创建成功\n保存至: {filename_info}")
        self.statusBar().showMessage("PDF生成完成")
        
    def on_generation_error(self, error_message):
        self.progress_widget.setVisible(False)
        self.add_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.generate_button.setEnabled(True)
        
        QMessageBox.critical(self, "错误", f"生成PDF失败:\n{error_message}")
        self.statusBar().showMessage("PDF生成失败")
        
    def closeEvent(self, event):
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        event.accept()


def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = PDFGeneratorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
