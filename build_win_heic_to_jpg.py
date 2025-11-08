import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_icon():
    """创建一个简单的图标文件"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的图标
        img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制一个简单的相机图标
        # 外框
        draw.rectangle([50, 50, 206, 206], outline=(0, 120, 215), width=10)
        # 镜头
        draw.ellipse([80, 80, 176, 176], outline=(0, 120, 215), width=10)
        # 内圆
        draw.ellipse([100, 100, 156, 156], fill=(0, 120, 215))
        
        # 保存为ico文件
        img.save('icon.ico', format='ICO', sizes=[(256, 256)])
        print("成功创建图标文件: icon.ico")
        return True
    except ImportError:
        print("警告: 未安装PIL，无法创建图标文件")
        return False
    except Exception as e:
        print(f"创建图标失败: {e}")
        return False

def build_exe():
    """使用PyInstaller打包程序"""
    # 检查主程序文件是否存在
    main_script = "win_heic_to_jpg.py"  # 修改为实际的主程序文件名
    if not os.path.exists(main_script):
        print(f"错误: 找不到主程序文件 {main_script}")
        return False
    
    # 创建图标文件
    icon_created = create_icon()
    icon_path = "icon.ico" if icon_created else None
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",              # 打包成单个exe文件
        "--noconsole",            # 不显示控制台窗口
        "--clean",                # 清理临时文件
        "--name=HEIC转JPG转换器", # 输出文件名
        "--hidden-import=pillow_heif",         # 隐式导入pillow_heif
        "--hidden-import=pil",                   # 隐式导入PIL
        "--hidden-import=PIL.Image",            # 隐式导入PIL.Image
        "--hidden-import=PIL._imagingtk",       # 隐式导入PIL._imagingtk
        "--hidden-import=PIL._tkinter_finder",  # 隐式导入PIL._tkinter_finder
        "--collect-data=pillow_heif",           # 收集pillow_heif的数据文件
        "--collect-data=PIL",                   # 收集PIL的数据文件
    ]
    
    # 如果有图标文件，添加图标选项
    if icon_path:
        cmd.append(f"--icon={icon_path}")
    
    # 添加主程序文件
    cmd.append(main_script)
    
    print("开始打包程序...")
    print("执行命令:", " ".join(cmd))
    
    try:
        # 运行PyInstaller
        result = subprocess.run(cmd, check=True)
        print("\n打包成功！")
        print(f"可执行文件位于: {os.path.abspath('dist/HEIC转JPG转换器.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败，错误代码: {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n错误: 未找到PyInstaller。请先安装: pip install pyinstaller")
        return False

def clean_build_files():
    """清理打包过程中产生的临时文件"""
    print("\n清理临时文件...")
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["icon.ico", "HEIC转JPG转换器.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"已删除目录: {dir_name}")
            except Exception as e:
                print(f"删除目录失败 {dir_name}: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"已删除文件: {file_name}")
            except Exception as e:
                print(f"删除文件失败 {file_name}: {e}")

def main():
    """主函数"""
    print("=== HEIC转JPG转换器 打包工具 ===\n")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return
    
    # 打包程序
    if build_exe():
        # 询问是否清理临时文件
        clean = input("\n是否清理临时文件？(y/n): ").lower().strip()
        if clean == 'y' or clean == 'yes':
            clean_build_files()
            print("\n清理完成！")
        
        print("\n打包过程全部完成！")
        print("您可以将 dist/HEIC转JPG转换器.exe 分发给用户使用。")
    else:
        print("\n打包失败，请检查错误信息并重试。")

if __name__ == "__main__":
    main()