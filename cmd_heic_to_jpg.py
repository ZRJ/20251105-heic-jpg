import os
from pathlib import Path
from PIL import Image

# 如果没安装 pillow-heif，请先运行： pip install pillow pillow-heif
import pillow_heif


def convert_heic_to_jpg(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ 文件夹不存在：{folder_path}")
        return

    # 注册 HEIF 插件
    pillow_heif.register_heif_opener()

    count = 0
    for heic_path in folder.rglob("*.heic"):
        jpg_path = heic_path.with_suffix(".jpg")

        try:
            with Image.open(heic_path) as img:
                img.convert("RGB").save(jpg_path, "JPEG", quality=95)
            count += 1
            print(f"✅ 转换成功: {heic_path.name} → {jpg_path.name}")
        except Exception as e:
            print(f"⚠️ 转换失败: {heic_path.name} ({e})")

    print(f"\n转换完成，共转换 {count} 个文件。")


if __name__ == "__main__":
    # 在这里修改你的目标目录
    target_dir = r"C:\path_to_heic_folder"  # 改成你的目录路径
    convert_heic_to_jpg(target_dir)
