from pathlib import Path
import sys

from PIL import Image


NAME_MAP = {
	1: "type1",
	2: "type2",
	3: "type3",
	4: "type4",
	5: "type5",
	6: "type6",
	7: "type7",
	8: "type8",
	9: "type0",
	10: "mine0",
	11: "mine1",
	12: "mine3",
	14: "mine2",
}


def split_image_4x4(image_path: Path) -> Path:
	if not image_path.exists() or not image_path.is_file():
		raise FileNotFoundError(f"Image not found: {image_path}")

	output_dir = image_path.parent / image_path.stem
	output_dir.mkdir(parents=True, exist_ok=True)

	with Image.open(image_path) as img:
		width, height = img.size
		if width % 4 != 0 or height % 4 != 0:
			raise ValueError(
				f"Image size must be divisible by 4. Current size: {width}x{height}"
			)

		tile_w = width // 4
		tile_h = height // 4

		index = 1
		for row in range(4):
			for col in range(4):
				left = col * tile_w
				upper = row * tile_h
				right = left + tile_w
				lower = upper + tile_h

				if index in NAME_MAP:
					tile = img.crop((left, upper, right, lower))
					out_name = f"{NAME_MAP[index]}.jpg"
					out_path = output_dir / out_name
					tile.convert("RGB").save(out_path, "JPEG", quality=95)

				index += 1

	return output_dir


def normalize_input_path(raw_path: str) -> Path:
	text = raw_path.strip()
	# 兼容用户粘贴时带引号："C:\\path\\to\\image.jpg"
	if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
		text = text[1:-1].strip()
	return Path(text).expanduser().resolve()


def main() -> None:
    for i in range(5):
        if len(sys.argv) > 1:
            raw_path = sys.argv[1]
        else:
            raw_path = input("请输入图片路径: ").strip()

        if not raw_path:
            print("未提供图片路径")
            return

        image_path = normalize_input_path(raw_path)
        output_dir = split_image_4x4(image_path)
        print(f"完成，输出目录: {output_dir}")


if __name__ == "__main__":
	main()
