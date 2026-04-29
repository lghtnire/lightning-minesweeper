import os
from datetime import datetime

from PIL import ImageGrab


def save_board_canvas_image(canvas, output_dir='captures', prefix='board'):
	"""截取并保存 Tkinter Canvas 的可见区域，返回保存后的绝对路径。"""
	if canvas is None:
		raise ValueError('canvas is None')

	canvas.update_idletasks()

	x0 = canvas.winfo_rootx()
	y0 = canvas.winfo_rooty()
	w = canvas.winfo_width()
	h = canvas.winfo_height()
	if w <= 1 or h <= 1:
		raise RuntimeError('canvas size is invalid')

	bbox = (x0, y0, x0 + w, y0 + h)
	image = ImageGrab.grab(bbox=bbox)

	save_dir = os.path.abspath(output_dir)
	os.makedirs(save_dir, exist_ok=True)
	#ts = datetime.now().strftime('%Y%m%d_%H%M%S')
	filename = f'{prefix}.png'
	save_path = os.path.join(save_dir, filename)
	image.save(save_path)
	return save_path

