import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import pillow_heif
from pathlib import Path
import threading

class HEICToJPGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HEIC 转 JPG 批量转换工具")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # 初始化变量
        self.source_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.is_converting = False
        self.converted_count = 0
        self.total_files = 0
        
        # 创建主界面
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = ttk.Label(
            self.root, 
            text="HEIC 转 JPG 批量转换工具", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # 主容器 - 使用Canvas确保所有内容可见
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 源目录选择
        source_frame = ttk.LabelFrame(scrollable_frame, text="源目录（包含HEIC文件）", padding="10")
        source_frame.pack(fill=tk.X, padx=20, pady=5)
        
        source_entry = ttk.Entry(source_frame, textvariable=self.source_dir, width=50)
        source_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        source_btn = ttk.Button(
            source_frame, 
            text="浏览...", 
            command=self.select_source_dir
        )
        source_btn.pack(side=tk.LEFT, padx=5)
        
        # 输出目录选择
        output_frame = ttk.LabelFrame(scrollable_frame, text="输出目录（JPG保存位置）", padding="10")
        output_frame.pack(fill=tk.X, padx=20, pady=5)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        output_btn = ttk.Button(
            output_frame, 
            text="浏览...", 
            command=self.select_output_dir
        )
        output_btn.pack(side=tk.LEFT, padx=5)
        
        # 选项框架
        options_frame = ttk.LabelFrame(scrollable_frame, text="转换选项", padding="10")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 质量设置
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="JPG质量：").pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(
            quality_frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.pack(side=tk.LEFT, padx=5)
        
        self.quality_label = ttk.Label(quality_frame, text="95")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        # 保持原文件名
        self.keep_name_var = tk.BooleanVar(value=True)
        keep_name_check = ttk.Checkbutton(
            options_frame,
            text="保持原文件名",
            variable=self.keep_name_var
        )
        keep_name_check.pack(anchor=tk.W, pady=5, padx=5)
        
        # 删除原文件选项
        self.delete_original_var = tk.BooleanVar(value=False)
        delete_check = ttk.Checkbutton(
            options_frame,
            text="转换后删除原HEIC文件",
            variable=self.delete_original_var
        )
        delete_check.pack(anchor=tk.W, pady=5, padx=5)
        
        # 进度条框架
        progress_frame = ttk.LabelFrame(scrollable_frame, text="转换进度", padding="10")
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500
        )
        self.progress_bar.pack(pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="准备就绪")
        self.status_label.pack()
        
        # 按钮框架 - 修复按钮显示问题
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 创建按钮容器
        button_container = ttk.Frame(button_frame)
        button_container.pack()
        
        self.convert_btn = ttk.Button(
            button_container,
            text="开始转换",
            command=self.start_conversion,
            width=15
        )
        self.convert_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = ttk.Button(
            button_container,
            text="取消",
            command=self.cancel_conversion,
            state=tk.DISABLED,
            width=15
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加底部填充
        bottom_padding = ttk.Frame(scrollable_frame, height=20)
        bottom_padding.pack()
        
        # 布置Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
        
    def select_source_dir(self):
        directory = filedialog.askdirectory(title="选择包含HEIC文件的目录")
        if directory:
            self.source_dir.set(directory)
            # 如果输出目录未设置，默认使用源目录
            if not self.output_dir.get():
                self.output_dir.set(directory)
                
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="选择JPG输出目录")
        if directory:
            self.output_dir.set(directory)
            
    def find_heic_files(self, directory):
        """查找目录下所有的HEIC文件"""
        heic_files = []
        extensions = ('.heic', '.HEIC', '.heif', '.HEIF')
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    heic_files.append(os.path.join(root, file))
                    
        return heic_files
        
    def convert_heic_to_jpg(self, heic_path, output_path):
        """转换单个HEIC文件为JPG"""
        try:
            # 读取HEIC文件
            heif_file = pillow_heif.read_heif(heic_path)
            
            # 转换为PIL图像
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            
            # 保存为JPG
            image.save(
                output_path,
                'JPEG',
                quality=self.quality_var.get(),
                optimize=True
            )
            
            return True
        except Exception as e:
            print(f"转换失败: {heic_path} - {str(e)}")
            return False
            
    def conversion_worker(self):
        """转换工作线程"""
        source_dir = self.source_dir.get()
        output_dir = self.output_dir.get()
        
        if not source_dir or not output_dir:
            messagebox.showerror("错误", "请选择源目录和输出目录")
            self.root.after(0, self.reset_ui)
            return
            
        # 查找所有HEIC文件
        heic_files = self.find_heic_files(source_dir)
        self.total_files = len(heic_files)
        
        if self.total_files == 0:
            messagebox.showinfo("提示", "未找到HEIC文件")
            self.root.after(0, self.reset_ui)
            return
            
        self.converted_count = 0
        self.is_converting = True
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换文件
        for i, heic_path in enumerate(heic_files):
            if not self.is_converting:
                break
                
            # 更新状态
            self.root.after(0, self.update_status, f"正在转换: {os.path.basename(heic_path)}")
            
            # 生成输出路径
            if self.keep_name_var.get():
                # 保持原文件名
                base_name = os.path.splitext(os.path.basename(heic_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.jpg")
            else:
                # 使用新的文件名
                output_path = os.path.join(output_dir, f"converted_{i+1:04d}.jpg")
            
            # 转换文件
            success = self.convert_heic_to_jpg(heic_path, output_path)
            
            if success:
                self.converted_count += 1
                
                # 如果选择删除原文件
                if self.delete_original_var.get():
                    try:
                        os.remove(heic_path)
                    except:
                        pass
            
            # 更新进度
            progress = (i + 1) / self.total_files * 100
            self.root.after(0, self.update_progress, progress)
            
        # 转换完成
        self.root.after(0, self.conversion_complete)
        
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        
    def start_conversion(self):
        """开始转换"""
        self.convert_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # 在新线程中执行转换
        self.conversion_thread = threading.Thread(target=self.conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
    def cancel_conversion(self):
        """取消转换"""
        self.is_converting = False
        self.reset_ui()
        
    def conversion_complete(self):
        """转换完成"""
        if self.is_converting:
            message = f"转换完成！\n成功转换: {self.converted_count} / {self.total_files} 个文件"
            messagebox.showinfo("完成", message)
        else:
            messagebox.showinfo("已取消", f"转换已取消\n已转换: {self.converted_count} / {self.total_files} 个文件")
            
        self.reset_ui()
        
    def reset_ui(self):
        """重置UI状态"""
        self.is_converting = False
        self.convert_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.status_label.config(text="准备就绪")
        self.progress_var.set(0)

def main():
    # 注册HEIF插件
    pillow_heif.register_heif_opener()
    
    # 创建主窗口
    root = tk.Tk()
    app = HEICToJPGConverter(root)
    
    # 运行应用
    root.mainloop()

if __name__ == "__main__":
    main()