import tkinter as tk
from tkinter import messagebox
import random
import json
from PIL import Image,ImageTk
import sys
import os
import math

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后的路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Minesweeper:
    def __init__(self, master, sizes=(8,8), mines=10,size=35):
        self.root = master
        # 统一设置 Tk 默认背景为浅蓝色
        try:
            self.root.option_add("*Background", "#EAF6FF")
        except Exception:
            pass
        self.rows = sizes[0]
        self.cols = sizes[1]
        self.mines = mines
        self.size=size
        # 画布与窗口之间的边距（像素）
        self.pad = 20
        # 顶部闪电与画布的间距
        self.top_margin = 4
        # 游戏是否已经结束（胜利或失败）
        self.finished = False
        self.mode="tradition"
        self._skin_label_to_path = {
            '联萌经典款': 'images/skins/联萌经典款',
            '电脑经典款': 'images/skins/电脑经典款',
            'WOM': 'images/skins/WOM',
            'WOM夜间': 'images/skins/WOM夜间',
            '晚灯夜': 'images/skins/晚灯夜',
            '夜间': 'images/skins/夜间',
            'win7': 'images/skins/win7',
            '巧克力扫雷': 'images/skins/巧克力扫雷'
        }
        self._skin_path_to_label = {v: k for k, v in self._skin_label_to_path.items()}
        self.skin_name_var = tk.StringVar(value='联萌经典款')
        self.images_path = self._skin_label_to_path[self.skin_name_var.get()]
        #录入图片
        imgs0 = [Image.open(resource_path(f'{self.images_path}/type{i}.jpg')).resize((self.size,self.size)) for i in range(9)]
        imgs1 = [Image.open(resource_path(f'{self.images_path}/mine{i}.jpg')).resize((self.size,self.size)) for i in range(4)]
        self.type_imgs = [ImageTk.PhotoImage(img) for img in imgs0]
        self.mine_imgs = [ImageTk.PhotoImage(img) for img in imgs1]
        # 载入重启按钮图标（闪电）及失败/成功图标，若加载失败则使用文本按钮作为回退
        def _load_icon(fname, scale=1.5):
            try:
                s = max(1, int(round(self.size * scale)))
                img = Image.open(resource_path(f'images/{fname}')).resize((s, s))
                return ImageTk.PhotoImage(img)
            except Exception:
                return None


        self.restart_img = _load_icon('闪电.jpg', scale=1.5)
        self.restart_img_press = _load_icon('闪电2.jpg', scale=1.5)
        self.restart_img_fail = _load_icon('闪电1.jpg', scale=1.5)
        self.restart_img_success = _load_icon('闪电3.jpg', scale=1.5)
        # 设置项变量：失败/胜利自动重开与R键重开
        self.auto_restart_on_fail_var = tk.BooleanVar(value=False)
        self.auto_restart_on_win_var = tk.BooleanVar(value=False)
        self.enable_r_restart_var = tk.BooleanVar(value=False)
        # 高级训练参数
        self.training_n_var = tk.IntVar(value=4)
        self.training_s1_var = tk.IntVar(value=2)
        self.training_s2_var = tk.IntVar(value=3)
        self.training_d_var = tk.IntVar(value=3)
        self.training_p_var = tk.DoubleVar(value=0.5)
        self.training_three_con_var = tk.BooleanVar(value=False)
        self.training_random_mode_var = tk.BooleanVar(value=False)
        self.training_highlight_var = tk.BooleanVar(value=True)
        # 格子像素大小设置（默认与当前 size 一致）
        self.cell_size_var = tk.IntVar(value=self.size)
        self._s_label_to_value = {'墙': 1, '端': 2, '开放': 3}
        self._s_value_to_label = {1: '墙', 2: '端', 3: '开放'}
        self._d_label_to_value = {'普通': 2, '困难': 3}
        self._d_value_to_label = {2: '普通', 3: '困难'}
        self.training_s1_label_var = tk.StringVar(value='端')
        self.training_s2_label_var = tk.StringVar(value='开放')
        self.training_d_label_var = tk.StringVar(value='困难')
        self.training_case_info_var = tk.StringVar(value='')
        # 找漏雷模式参数
        self.find_mine_rows_var = tk.IntVar(value=16)
        self.find_mine_cols_var = tk.IntVar(value=30)
        self.find_mine_mines_var = tk.IntVar(value=99)
        # 持久化配置文件路径
        self.settings_path = os.path.join(os.path.abspath('.'), 'minesweeper_settings.json')
        # 监听变量修改以自动保存并即时生效
        try:
            self.auto_restart_on_fail_var.trace_add('write', lambda *args: self.save_settings())
            self.auto_restart_on_win_var.trace_add('write', lambda *args: self.save_settings())
            self.enable_r_restart_var.trace_add('write', lambda *args: (self._toggle_r_bind(), self.save_settings()))
        except Exception:
            pass
        # 加载保存的设置（如果存在）
        try:
            self.load_settings()
        except Exception:
            pass
        # 让启动时贴图与设置中的皮肤保持一致
        try:
            self.reload_images()
        except Exception:
            pass
        self._sync_training_label_vars()
        self.menu()
        # 顶部工具栏（放置重启按钮）
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side='top', fill='x')
        # 如果图片加载成功，使用图片按钮；否则使用文字按钮
        if getattr(self, 'restart_img', None) is not None:
            self.restart_button = tk.Button(self.top_frame, image=self.restart_img, command=self.restart, bd=0)
        else:
            self.restart_button = tk.Button(self.top_frame, text='新游戏', command=self.restart)
        # 缩小闪电与游戏的像素间距
        self.restart_button.pack(pady=(4, 0))

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side='left', fill='both', expand=True)

        self.training_panel = tk.LabelFrame(self.main_frame, text='高级训练参数', padx=8, pady=8)
        self._training_panel_pack_opts = {'side': 'right', 'fill': 'y', 'padx': (0, 10), 'pady': (8, 10)}
        self._build_training_panel()

        self.find_mine_panel = tk.LabelFrame(self.main_frame, text='找漏雷参数', padx=8, pady=8)
        self._find_mine_panel_pack_opts = {'side': 'right', 'fill': 'y', 'padx': (0, 10), 'pady': (8, 10)}
        self._build_find_mine_panel()

        h=self.rows*self.size
        w=self.cols*self.size
        self.canvas=tk.Canvas(self.board_frame,height=h,width=w)
        self.new_game((8,8),10)
        self._update_training_panel_visibility()

    def reload_images(self):
        """根据当前 self.size (像素) 重新加载并缩放图片资源（若缺文件会抛异常）"""
        image_path=self.images_path
        imgs0 = [Image.open(resource_path(f'{image_path}/type{i}.jpg')).resize((self.size, self.size)) for i in range(9)]
        imgs1 = [Image.open(resource_path(f'{image_path}/mine{i}.jpg')).resize((self.size, self.size)) for i in range(4)]
        self.type_imgs = [ImageTk.PhotoImage(img) for img in imgs0]
        self.mine_imgs = [ImageTk.PhotoImage(img) for img in imgs1]
        # 也尝试重载重启图标（如果存在）
        try:
            if getattr(self, 'restart_img', None) is not None:
                s = max(1, int(round(self.size * 1.5)))
                self.restart_img = ImageTk.PhotoImage(Image.open(resource_path('images/闪电.jpg')).resize((s, s)))
            if getattr(self, 'restart_img_press', None) is not None:
                s = max(1, int(round(self.size * 1.5)))
                self.restart_img_press = ImageTk.PhotoImage(Image.open(resource_path('images/闪电2.jpg')).resize((s, s)))
            if getattr(self, 'restart_img_fail', None) is not None:
                s = max(1, int(round(self.size * 1.5)))
                self.restart_img_fail = ImageTk.PhotoImage(Image.open(resource_path('images/闪电1.jpg')).resize((s, s)))
            if getattr(self, 'restart_img_success', None) is not None:
                s = max(1, int(round(self.size * 1.5)))
                self.restart_img_success = ImageTk.PhotoImage(Image.open(resource_path('images/闪电3.jpg')).resize((s, s)))
        except Exception:
            pass

    def set_restart_icon(self, state='normal'):
        """切换顶部重启按钮图标：state in ('normal','fail','success')"""
        if not hasattr(self, 'restart_button'):
            return
        if state == 'fail' and getattr(self, 'restart_img_fail', None) is not None:
            self.restart_button.config(image=self.restart_img_fail, text='')
        elif state == 'success' and getattr(self, 'restart_img_success', None) is not None:
            self.restart_button.config(image=self.restart_img_success, text='')
        elif state == 'press' and getattr(self, 'restart_img_press', None) is not None:
            self.restart_button.config(image=self.restart_img_press, text='')
        elif getattr(self, 'restart_img', None) is not None:
            self.restart_button.config(image=self.restart_img, text='')
        else:
            txt = '新游戏'
            if state == 'fail':
                txt = '失败'
            elif state == 'success':
                txt = '胜利'
            self.restart_button.config(image='', text=txt)

    def create_widgets(self):
        """创建游戏界面"""
        self.canvas.delete("all")
        h=self.rows*self.size
        w=self.cols*self.size
        self.canvas.config(height=h,width=w)
        # 临时按下状态跟踪（用于在按下时显示 type0 临时图标）
        self.pressed_cells = set()
        self.both_pressed = False
        self.last_press_center = None
        self.image_map = [[None]*self.cols for i in range(self.rows)]
        for row in range(self.rows): 
            for col in range(self.cols): 
                x = (col+1/2) * self.size  # 计算x坐标
                y = (row+1/2) * self.size  # 计算y坐标
                self.image_map[row][col]=self.canvas.create_image(x, y, image=self.mine_imgs[-1])
        
        # 绑定事件处理器
        self.left_pressed = False
        self.right_pressed = False
        self.left_press_coord = None
        # 记录右键按下时是否已执行标记，以避免 release 时重复
        self.right_did_mark_on_press = False
        self.right_marked_coord = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        self.canvas.bind("<ButtonPress-2>", self.on_middle_press)
        # 顶部与画布之间使用较小的上边距
        self.canvas.pack(padx=self.pad, pady=(self.top_margin, self.pad))
        
    def menu(self):
        # 主菜单
        self.menubar = tk.Menu(self.root)
        
        self.menubar.add_command(label="新游戏", command=self.restart)
        
        menu_new = tk.Menu(self.menubar, tearoff=False)
        grade = ('初级8x8','中级16x16','高级16x30','自定义')
        menu_new.add_command(label=grade[0], command=lambda *e: self.new_game((8,8),10))
        menu_new.add_command(label=grade[1], command=lambda *e: self.new_game((16,16),40))
        menu_new.add_command(label=grade[2], command=lambda *e: self.new_game((16,30),99))
        menu_new.add_command(label=grade[3], command= self.open_input_dialog)
        self.menubar.add_cascade(label="经典模式", menu=menu_new)
        
        menu1 = tk.Menu(self.menubar, tearoff=False)
        grade = ('找漏雷','直线判雷','定式判雷',"定式判雷2")
        menu1.add_command(label=grade[0], command=self.find_mine)
        menu1.add_command(label=grade[1], command=self.exercise1)
        menu1.add_command(label=grade[2], command=self.exercise2)
        menu1.add_command(label=grade[3], command=self.exercise3)
        self.menubar.add_cascade(label="训练模式", menu=menu1)

        self.menubar.add_command(label="高级训练", command=self.training_mode)
        
        # 设置菜单：允许修改格子像素大小和其他选项（并提供单独设置界面）
        self.menubar.add_command(label="设置", command=self.open_settings_window)

        self.menubar.add_command(label="关于", command=self.show_about)

        self.root.config(menu=self.menubar)

    def show_about(self):
        """显示项目信息。"""
        info = (
            "项目介绍：闪电扫雷，一款扫雷判雷训练器\n"
            "项目作者：闪电小雷友\n"
            "项目地址：https://github.com/lghtnire/lightning-minesweeper\n"
            "\n"
            "对使用有疑惑请查看Help.md文件\n"
            "发现Bug或有任何建议欢迎在Github提交Issue！\n"
            "感谢所有提供反馈和建议的玩家朋友们！"
        )
        try:
            messagebox.showinfo("关于", info, parent=self.root)
        except Exception:
            pass

    def _sync_training_label_vars(self):
        """根据数值变量同步下拉文本。"""
        try:
            self.training_s1_label_var.set(self._s_value_to_label.get(int(self.training_s1_var.get()), '端'))
            self.training_s2_label_var.set(self._s_value_to_label.get(int(self.training_s2_var.get()), '开放'))
            self.training_d_label_var.set(self._d_value_to_label.get(int(self.training_d_var.get()), '困难'))
        except Exception:
            pass

    def _sync_skin_name_var(self):
        """根据当前图片路径同步皮肤名称变量。"""
        try:
            self.skin_name_var.set(self._skin_path_to_label.get(self.images_path, '联萌经典款'))
        except Exception:
            pass

    def _apply_skin_change(self, restart_game=True):
        """应用皮肤设置：重载图片，并可选重开当前模式。"""
        try:
            selected = self.skin_name_var.get()
            new_path = self._skin_label_to_path.get(selected, self._skin_label_to_path['联萌经典款'])
            changed = (new_path != self.images_path)
            self.images_path = new_path
            self._sync_skin_name_var()
            self.save_settings()
            if changed:
                self.reload_images()
                if restart_game and hasattr(self, 'canvas'):
                    self.restart()
        except Exception:
            pass

    def _on_training_select_change(self, key):
        """处理 s1/s2/d 选择项修改。"""
        try:
            if key == 's1':
                self.training_s1_var.set(self._s_label_to_value.get(self.training_s1_label_var.get(), 2))
            elif key == 's2':
                self.training_s2_var.set(self._s_label_to_value.get(self.training_s2_label_var.get(), 3))
            elif key == 'd':
                self.training_d_var.set(self._d_label_to_value.get(self.training_d_label_var.get(), 3))
        except Exception:
            pass
        self._on_training_param_changed()

    def _on_training_param_changed(self, event=None):
        """高级训练参数更新后，立即校验并保存；若在训练模式则实时刷新。"""
        try:
            self._sanitize_training_settings()
            self._sync_training_label_vars()
            if not self.training_random_mode_var.get():
                self.training_case_info_var.set('')
            self.save_settings()
            if getattr(self, 'mode', None) == 'training_mode':
                self.training_mode()
            elif not self.training_highlight_var.get():
                try:
                    self.canvas.delete("training_win_highlight")
                except Exception:
                    pass
        except Exception:
            pass

    def _set_training_case_info(self, n, s1, s2, d, p, three_con, random_mode):
        """在随机训练模式下显示当前题目的实际参数。"""
        if not random_mode:
            self.training_case_info_var.set('')
            return
        s1_text = self._s_value_to_label.get(s1, str(s1))
        s2_text = self._s_value_to_label.get(s2, str(s2))
        d_text = self._d_value_to_label.get(d, str(d))
        three_text = '开' if three_con else '关'
        self.training_case_info_var.set(
            f"n={n}  s1={s1}({s1_text})  s2={s2}({s2_text})\n"
            f"d={d}({d_text})  p={p:.2f}  three_con={three_text}"
        )

    def _build_training_panel(self):
        """在游戏右侧创建高级训练参数面板。"""
        panel = self.training_panel

        row_n = tk.Frame(panel)
        row_n.pack(fill='x', pady=2)
        tk.Label(row_n, text='n (>=3)').pack(side='left')
        sp_n = tk.Spinbox(row_n, from_=3, to=99, increment=1, width=8,
                          textvariable=self.training_n_var, command=self._on_training_param_changed)
        sp_n.pack(side='right')
        sp_n.bind('<FocusOut>', self._on_training_param_changed)
        sp_n.bind('<Return>', self._on_training_param_changed)

        row_s = tk.Frame(panel)
        row_s.pack(fill='x', pady=2)
        tk.Label(row_s, text='s1 左侧').grid(row=0, column=0, sticky='w')
        tk.OptionMenu(row_s, self.training_s1_label_var, '墙', '端', '开放',
                      command=lambda *_: self._on_training_select_change('s1')).grid(row=0, column=1, sticky='e')
        tk.Label(row_s, text='s2 右侧').grid(row=1, column=0, sticky='w')
        tk.OptionMenu(row_s, self.training_s2_label_var, '墙', '端', '开放',
                      command=lambda *_: self._on_training_select_change('s2')).grid(row=1, column=1, sticky='e')
        row_s.grid_columnconfigure(0, weight=1)

        row_d = tk.Frame(panel)
        row_d.pack(fill='x', pady=2)
        tk.Label(row_d, text='d 难度').pack(side='left')
        tk.OptionMenu(row_d, self.training_d_label_var, '普通', '困难',
                      command=lambda *_: self._on_training_select_change('d')).pack(side='right')

        row_p = tk.Frame(panel)
        row_p.pack(fill='x', pady=2)
        tk.Label(row_p, text='p 密度参数(0,1)').pack(side='left')
        sp_p = tk.Spinbox(row_p, from_=0.01, to=0.99, increment=0.01, width=8,
                          format='%.2f', textvariable=self.training_p_var, command=self._on_training_param_changed)
        sp_p.pack(side='right')
        sp_p.bind('<FocusOut>', self._on_training_param_changed)
        sp_p.bind('<Return>', self._on_training_param_changed)

        tk.Checkbutton(panel, text='允许三连雷', variable=self.training_three_con_var,
                       command=self._on_training_param_changed).pack(anchor='w', pady=(4, 2))
        tk.Checkbutton(panel, text='随机训练模式', variable=self.training_random_mode_var,
                   command=self._on_training_param_changed).pack(anchor='w', pady=(2, 2))
        tk.Checkbutton(panel, text='高亮提示', variable=self.training_highlight_var,
               command=self._on_training_param_changed).pack(anchor='w', pady=(2, 2))
        #tk.Label(panel, text='本题参数').pack(anchor='w', pady=(4, 0))
        #tk.Label(panel, textvariable=self.training_case_info_var, justify='left', wraplength=190).pack(anchor='w', pady=(0, 2))
        tk.Label(panel, text='墙=1 端=2 开放=3').pack(anchor='w', pady=(2, 0))

    def _build_find_mine_panel(self):
        """在游戏右侧创建找漏雷模式参数面板。"""
        panel = self.find_mine_panel

        def _make_row(label_text, var, from_, to):
            f = tk.Frame(panel)
            f.pack(fill='x', pady=3)
            tk.Label(f, text=label_text).pack(side='left')
            sb = tk.Spinbox(f, from_=from_, to=to, increment=1, width=8, textvariable=var)
            sb.pack(side='right')
            return sb

        _make_row('行数', self.find_mine_rows_var, 2, 50)
        _make_row('列数', self.find_mine_cols_var, 2, 50)
        _make_row('雷数', self.find_mine_mines_var, 1, 9999)
        tk.Button(panel, text='重新生成', command=self.find_mine).pack(fill='x', pady=(10, 2))

    def _update_training_panel_visibility(self):
        """根据当前模式控制右侧参数面板的显示/隐藏。"""
        mode = getattr(self, 'mode', None)
        # 高级训练面板
        try:
            if mode == 'training_mode':
                if not self.training_panel.winfo_ismapped():
                    self.training_panel.pack(**self._training_panel_pack_opts)
            else:
                if self.training_panel.winfo_ismapped():
                    self.training_panel.pack_forget()
        except Exception:
            pass
        # 找漏雷面板
        try:
            if mode == 'find_mine':
                if not self.find_mine_panel.winfo_ismapped():
                    self.find_mine_panel.pack(**self._find_mine_panel_pack_opts)
            else:
                if self.find_mine_panel.winfo_ismapped():
                    self.find_mine_panel.pack_forget()
        except Exception:
            pass

    def open_input_dialog(self):
        """创建自定义模式输入弹窗（使用 Spinbox 精确输入）"""
        # 防止重复打开
        try:
            if getattr(self, '_input_dialog', None) and self._input_dialog.winfo_exists():
                self._input_dialog.lift()
                return
        except Exception:
            pass

        dialog = tk.Toplevel(self.root)
        dialog.title('自定义模式')
        dialog.resizable(False, False)
        self._input_dialog = dialog

        frm = tk.Frame(dialog, padx=16, pady=12)
        frm.pack(fill='both', expand=True)

        rows_var = tk.IntVar(value=self.rows)
        cols_var = tk.IntVar(value=self.cols)
        mines_var = tk.IntVar(value=self.mines)

        def make_row(parent, label, var, from_, to):
            f = tk.Frame(parent)
            f.pack(fill='x', pady=4)
            tk.Label(f, text=label, width=6, anchor='w').pack(side='left')
            sb = tk.Spinbox(f, from_=from_, to=to, increment=1, width=8, textvariable=var)
            sb.pack(side='right')
            return sb

        sp_rows = make_row(frm, '行数', rows_var, 2, 50)
        sp_cols = make_row(frm, '列数', cols_var, 2, 50)
        sp_mines = make_row(frm, '雷数', mines_var, 1, 9999)
        sp_rows.focus_set()

        def on_confirm():
            try:
                r = max(2, int(rows_var.get()))
                c = max(2, int(cols_var.get()))
                m = max(1, min(int(mines_var.get()), r * c - 1))
            except Exception:
                tk.messagebox.showerror('输入错误', '请确认行数、列数、雷数均为有效整数。', parent=dialog)
                return
            self.new_game((r, c), m)
            self.mode = 'tradition'
            dialog.destroy()

        btn_frm = tk.Frame(frm)
        btn_frm.pack(fill='x', pady=(8, 0))
        tk.Button(btn_frm, text='确定', width=8, command=on_confirm).pack(side='right', padx=(4, 0))
        tk.Button(btn_frm, text='取消', width=8, command=dialog.destroy).pack(side='right')
        dialog.bind('<Return>', lambda e: on_confirm())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def open_size_dialog(self):
        """创建输入弹窗，用于设置每个格子的像素大小（重新开始游戏）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置格子大小")
        dialog.geometry("300x150")
        tk.Label(dialog, text="请输入格子像素大小（默认35）：").pack(pady=10)
        entry = tk.Entry(dialog, width=25)
        entry.pack(pady=5)
        entry.insert(0, str(self.size))
        entry.focus_set()

        def on_confirm_size():
            try:
                new_size = int(entry.get())
                if new_size <= 0:
                    raise ValueError
            except Exception:
                tk.messagebox.showerror("输入错误", "请输入一个正整数作为像素大小。")
                return
            self.cell_size_var.set(new_size)
            self._apply_cell_size_setting(restart_game=True)
            dialog.destroy()

        tk.Button(dialog, text="确定", command=on_confirm_size).pack(pady=10)

    def _apply_cell_size_setting(self, restart_game=True):
        """应用格子像素大小设置：重载图片并可选重开当前模式。"""
        try:
            new_size = int(self.cell_size_var.get())
            if new_size <= 0:
                raise ValueError
        except Exception:
            self.cell_size_var.set(self.size)
            return

        if new_size == self.size:
            return

        old_size = self.size
        self.size = new_size
        try:
            self.reload_images()
        except Exception:
            self.size = old_size
            self.cell_size_var.set(old_size)
            try:
                messagebox.showwarning("警告", "图片资源加载失败，保持旧大小。", parent=self.root)
            except Exception:
                pass
            return

        # 同步变量，避免 UI 与实际值不一致
        self.cell_size_var.set(self.size)

        # 调整画布尺寸与窗口最小尺寸
        try:
            h = self.rows * self.size
            w = self.cols * self.size
            self.canvas.config(width=w, height=h)
            try:
                self.root.minsize(w + 2 * self.pad, h + 2 * self.pad)
            except Exception:
                pass
        except Exception:
            pass

        if restart_game and hasattr(self, 'canvas'):
            try:
                self.restart()
            except Exception:
                pass

    def open_settings_window(self):
        """打开单独的设置界面（Toplevel），以更直观地调整选项并保存"""
        # 防止同时打开多个设置窗口
        try:
            if getattr(self, '_settings_window', None) and tk.Toplevel.winfo_exists(self._settings_window):
                self._settings_window.lift()
                return
        except Exception:
            pass

        w = tk.Toplevel(self.root)
        w.title('设置')
        w.geometry('320x300')
        self._settings_window = w

        frm = tk.Frame(w)
        frm.pack(fill='both', expand=True, padx=12, pady=12)

        cb1 = tk.Checkbutton(frm, text='失败自动重开', variable=self.auto_restart_on_fail_var)
        cb1.pack(anchor='w', pady=4)
        cb2 = tk.Checkbutton(frm, text='胜利自动重开', variable=self.auto_restart_on_win_var)
        cb2.pack(anchor='w', pady=4)
        cb3 = tk.Checkbutton(frm, text='启用 R 键重开', variable=self.enable_r_restart_var, command=self._toggle_r_bind)
        cb3.pack(anchor='w', pady=4)

        skin_row = tk.Frame(frm)
        skin_row.pack(fill='x', pady=(8, 4))
        tk.Label(skin_row, text='皮肤').pack(side='left')
        tk.OptionMenu(skin_row, self.skin_name_var, '联萌经典款', '电脑经典款', 'WOM', 'WOM夜间', '晚灯夜', '夜间', 'win7', '巧克力扫雷',
                  command=lambda *_: self._apply_skin_change(restart_game=True)).pack(side='right')

        # 格子像素大小设置
        cell_size_row = tk.Frame(frm)
        cell_size_row.pack(fill='x', pady=(8, 4))
        tk.Label(cell_size_row, text='格子像素大小').pack(side='left')
        tk.Spinbox(cell_size_row, from_=10, to=80, textvariable=self.cell_size_var, width=5).pack(side='right')

        def on_close():
            try:
                self._sanitize_training_settings()
                self._apply_cell_size_setting(restart_game=True)
                self._apply_skin_change(restart_game=False)
                # 保存设置并更新菜单状态
                self.save_settings()
            except Exception:
                pass
            try:
                w.destroy()
            except Exception:
                pass

        tk.Button(frm, text='保存并关闭', command=on_close).pack(side='right', pady=8)

    def _toggle_r_bind(self):
        """绑定或解绑 R 键用于重开（由设置菜单中的复选框控制）"""
        try:
            if getattr(self, 'enable_r_restart_var', None) and self.enable_r_restart_var.get():
                # 绑定小写与大写 r
                self.root.bind('<r>', self._on_r_key)
                self.root.bind('<R>', self._on_r_key)
            else:
                try:
                    self.root.unbind('<r>')
                except Exception:
                    pass
                try:
                    self.root.unbind('<R>')
                except Exception:
                    pass
        except Exception:
            pass

    def _on_r_key(self, event):
        """R 键按下事件处理器，触发重开"""
        try:
            self.restart()
        except Exception:
            pass


    def save_settings(self):
        """将当前设置保存到磁盘（JSON）。"""
        try:
            train_cfg = self._sanitize_training_settings()
            data = {
                'auto_restart_on_fail': bool(self.auto_restart_on_fail_var.get()),
                'auto_restart_on_win': bool(self.auto_restart_on_win_var.get()),
                'enable_r_restart': bool(self.enable_r_restart_var.get()),
                'skin_name': str(self.skin_name_var.get()),
                'images_path': str(self.images_path),
                'training_n': train_cfg['n'],
                'training_s1': train_cfg['s1'],
                'training_s2': train_cfg['s2'],
                'training_d': train_cfg['d'],
                'training_p': train_cfg['p'],
                'training_three_con': train_cfg['three_con'],
                'training_random_mode': train_cfg['random_mode'],
                'training_highlight': train_cfg['highlight'],
                'cell_size': int(self.cell_size_var.get())
            }
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_settings(self):
        """从磁盘加载设置（如果存在），并应用到变量。"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                try:
                    self.auto_restart_on_fail_var.set(bool(data.get('auto_restart_on_fail', False)))
                except Exception:
                    pass
                try:
                    self.auto_restart_on_win_var.set(bool(data.get('auto_restart_on_win', False)))
                except Exception:
                    pass
                try:
                    self.enable_r_restart_var.set(bool(data.get('enable_r_restart', False)))
                except Exception:
                    pass
                try:
                    skin_name = str(data.get('skin_name', ''))
                    if skin_name in self._skin_label_to_path:
                        self.skin_name_var.set(skin_name)
                        self.images_path = self._skin_label_to_path[skin_name]
                    else:
                        legacy_path = str(data.get('images_path', self.images_path))
                        if legacy_path in self._skin_path_to_label:
                            self.images_path = legacy_path
                        self._sync_skin_name_var()
                except Exception:
                    self.images_path = self._skin_label_to_path['联萌经典款']
                    self.skin_name_var.set('联萌经典款')
                try:
                    self.training_n_var.set(int(data.get('training_n', 4)))
                except Exception:
                    self.training_n_var.set(4)
                try:
                    self.training_s1_var.set(int(data.get('training_s1', 2)))
                except Exception:
                    self.training_s1_var.set(2)
                try:
                    self.training_s2_var.set(int(data.get('training_s2', 3)))
                except Exception:
                    self.training_s2_var.set(3)
                try:
                    self.training_d_var.set(int(data.get('training_d', 3)))
                except Exception:
                    self.training_d_var.set(3)
                try:
                    self.training_p_var.set(float(data.get('training_p', 0.5)))
                except Exception:
                    self.training_p_var.set(0.5)
                try:
                    self.training_three_con_var.set(bool(data.get('training_three_con', False)))
                except Exception:
                    self.training_three_con_var.set(False)
                try:
                    self.training_random_mode_var.set(bool(data.get('training_random_mode', False)))
                except Exception:
                    self.training_random_mode_var.set(False)
                try:
                    self.training_highlight_var.set(bool(data.get('training_highlight', True)))
                except Exception:
                    self.training_highlight_var.set(True)
                try:
                    # 兼容旧键 font_size
                    cell_size = int(data.get('cell_size', data.get('font_size', self.size)))
                    if cell_size > 0:
                        self.size = cell_size
                    else:
                        self.size = 35
                    self.cell_size_var.set(self.size)
                except Exception:
                    self.size = 35
                    self.cell_size_var.set(self.size)
                try:
                    self._sanitize_training_settings()
                    self._sync_training_label_vars()
                except Exception:
                    pass
                # 根据加载的值更新 R 绑定状态
                try:
                    self._toggle_r_bind()
                except Exception:
                    pass
        except Exception:
            pass

    def _sanitize_training_settings(self):
        """校验并标准化高级训练设置参数。"""
        cfg = {}

        try:
            cfg['n'] = max(3, int(self.training_n_var.get()))
        except Exception:
            cfg['n'] = 4

        try:
            cfg['s1'] = int(self.training_s1_var.get())
        except Exception:
            cfg['s1'] = 2
        if cfg['s1'] not in (1, 2, 3):
            cfg['s1'] = 2

        try:
            cfg['s2'] = int(self.training_s2_var.get())
        except Exception:
            cfg['s2'] = 3
        if cfg['s2'] not in (1, 2, 3):
            cfg['s2'] = 3

        try:
            cfg['d'] = int(self.training_d_var.get())
        except Exception:
            cfg['d'] = 3
        if cfg['d'] not in (2, 3):
            cfg['d'] = 3

        try:
            cfg['p'] = float(self.training_p_var.get())
        except Exception:
            cfg['p'] = 0.5
        if not (0 < cfg['p'] < 1):
            cfg['p'] = 0.5

        try:
            cfg['three_con'] = bool(self.training_three_con_var.get())
        except Exception:
            cfg['three_con'] = False

        try:
            cfg['random_mode'] = bool(self.training_random_mode_var.get())
        except Exception:
            cfg['random_mode'] = False

        try:
            cfg['highlight'] = bool(self.training_highlight_var.get())
        except Exception:
            cfg['highlight'] = True

        try:
            self.training_n_var.set(cfg['n'])
            self.training_s1_var.set(cfg['s1'])
            self.training_s2_var.set(cfg['s2'])
            self.training_d_var.set(cfg['d'])
            self.training_p_var.set(cfg['p'])
            self.training_three_con_var.set(cfg['three_con'])
            self.training_random_mode_var.set(cfg['random_mode'])
            self.training_highlight_var.set(cfg['highlight'])
        except Exception:
            pass

        return cfg

    def _sample_random_training_n(self):
        """随机模式下采样 n: 3-10 的递减几何分布，且 P(n=3)=0.3。"""
        n_values = list(range(3, 11))
        p0 = 0.3

        # 找到等比系数 r，使 sum_{k=0..7} p0*r^k = 1，并保持单调递减
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2.0
            if mid == 1.0:
                s = p0 * len(n_values)
            else:
                s = p0 * (1 - mid**len(n_values)) / (1 - mid)
            if s > 1.0:
                hi = mid
            else:
                lo = mid
        r = (lo + hi) / 2.0

        weights = [p0 * (r**k) for k in range(len(n_values))]
        weight_sum = sum(weights)
        if weight_sum <= 0:
            return 3
        normalized = [w / weight_sum for w in weights]
        return random.choices(n_values, weights=normalized, k=1)[0]

    def restart(self):
        # 重置 finished 标志并恢复为普通新游戏图标
        try:
            self.finished = False
        except Exception:
            pass
        try:
            self.set_restart_icon('normal')
        except Exception:
            pass
        # 重置首次点击状态
        try:
            self.first_click = True
        except Exception:
            pass
        if self.mode=="tradition":
            self.create_widgets()
            self.mine_coords = set()
            self.revealed = set()
            self.marked = set()
            self.place_mines()
            self.calculate_numbers()
        elif self.mode=="find_mine":
            self.find_mine()
        elif self.mode=="exercise1":
            self.exercise1()
        elif self.mode=="exercise2":
            self.exercise2()
        elif self.mode=="exercise3":
            self.exercise3()
        elif self.mode=="training_mode":
            self.training_mode()

            
            


    def new_game(self,sizes,mines):
        self.rows=sizes[0]
        self.cols=sizes[1]
        self.mines=mines
        # 首次点击需保证开空
        self.first_click = True
        self.create_widgets()
        self.mine_coords = set()
        self.revealed = set()
        self.marked = set()
        self.place_mines()
        self.calculate_numbers()
        self.mode="tradition"
        self._update_training_panel_visibility()
        
    def find_mine(self):
        # 读取面板参数
        try:
            fm_rows = max(2, int(self.find_mine_rows_var.get()))
        except Exception:
            fm_rows = 16
        try:
            fm_cols = max(2, int(self.find_mine_cols_var.get()))
        except Exception:
            fm_cols = 30
        try:
            fm_mines = max(1, min(int(self.find_mine_mines_var.get()), fm_rows * fm_cols - 1))
        except Exception:
            fm_mines = 99
        # 回写栄位（确保显示尺寸一致）
        try:
            self.find_mine_rows_var.set(fm_rows)
            self.find_mine_cols_var.set(fm_cols)
            self.find_mine_mines_var.set(fm_mines)
        except Exception:
            pass


        self.new_game((fm_rows, fm_cols), fm_mines)
        for r in range(16):
            for c in range(30):
                if self.numbers.get((r,c),None)==0:
                    self.reveal(r,c)
        optional_lst=[]
        for r in range(16):
            for c in range(30):
                if (r,c) in self.revealed or (r,c) in self.mine_coords:
                    continue
                else:
                    optional_lst.append((r,c))
        choice_coord=random.choice(optional_lst)        
        optional_lst.remove(choice_coord)
        for coord in optional_lst:
            self.reveal(coord[0],coord[1])
        

            '''
            def unique():
                infor_lst=[]
                array_lst=[]
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        array_lst.append((dr,dc))
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) in self.revealed:
                            infor_lst.append((nr,nc))
                if len(infor_lst)==0

                
                for (dr,dc) in array_lst:
                    judge_coord=(infor_lst[0][0]+dr,infor_lst[0][1]+dc)
                    for i in range(1,len(infor_lst))
            '''

            
            
            
        self.mode="find_mine"
        self._update_training_panel_visibility()
    
    def exercise1(self):
        sizes=(4,30)
        self.rows=sizes[0]
        self.cols=sizes[1]
        self.create_widgets()
        self.mine_coords = set()
        self.revealed = set()
        self.marked = set()
        self.mines=0
        def generate_binary_list(k):
            #没有三连0
            lst = []
            # 第一位
            lst.append(random.choice([0,1]))            
            # 第二位
            lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
            for _ in range(k):
                if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                    lst.append(1)                    
                else:
                    lst.append(random.choice([0,1]))
            return lst
        frmine_lst=generate_binary_list(30)
        for c in range(30):
            if not frmine_lst[c]:
                self.mine_coords.add((0,c))
#         while len(self.mine_coords) < self.mines-10: #特殊布雷
#             r = random.randint(0, 1)
#             c = random.randint(0, self.cols-1)
#             if r==0:
#                 self.mine_coords.add((0, c))
#             else:
#                 self.mine_coords.add((2, c))
        srmine_lst = generate_binary_list(28)
        self.mine_coords.add((2,1))
        for c in range(28):
            if srmine_lst[c]:            
                self.mine_coords.add((2,c+2))
        for _ in range(10):
            self.mine_coords.add((3,3*_+1))
        self.calculate_numbers()
        self.reveal(2,0)
        for c in range(self.cols):
            self.reveal(1,c)
            if (0,c) in self.mine_coords:
                self.mark_mine(0,c)
            else:
                self.reveal(0,c)
        self.mode="exercise1"    
        self._update_training_panel_visibility()
        
    def exercise2(self):
        self.mines=0
        sizes=(5,6)
        self.rows=sizes[0]
        self.cols=sizes[1]
        self.create_widgets()
        self.mine_coords = set()
        self.revealed = set()
        self.marked = set()
        def generate_binary_list(k):
            lst = []
            # 第一位
            lst.append(random.choice([0,1]))            
            # 第二位
            lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
            for _ in range(k):
                if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                    lst.append(1)                    
                else:
                    lst.append(random.choice([0,1]))
            return lst
        srmine_lst=generate_binary_list(4)
        for c in range(4):
            if not srmine_lst[c]:
                self.mine_coords.add((1,c))
        mine_lsts=[[0,1],[0,2],[1,2],[1]]
        mine_lst=random.choice(mine_lsts)
        for c in mine_lst:
            self.mine_coords.add((3,c))
        self.mine_coords.add((4,4))
        self.mine_coords.add((2,3))
        self.calculate_numbers()
        for c in range(self.cols):
            self.reveal(0,c)
            if (1,c) in self.mine_coords:
                self.mark_mine(1,c)
            else:
                self.reveal(1,c)
             
            if (2,c) in self.mine_coords:
                self.mark_mine(2,c)
            else:
                self.reveal(2,c)
        self.reveal(3,3)
        self.mode="exercise2" 
        self._update_training_panel_visibility()

    def exercise3(self):
        self.mines=0
        sizes=(5,7)
        self.rows=sizes[0]
        self.cols=sizes[1]
        self.create_widgets()
        self.mine_coords = set()
        self.revealed = set()
        self.marked = set()
        def generate_binary_list(k):
            lst = []           
            # 第一位
            lst.append(random.choice([0,1]))            
            # 第二位
            lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
            for _ in range(k):
                if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                    lst.append(1)                    
                else:
                    lst.append(random.choice([0,1]))
            return lst
        srmine_lst=generate_binary_list(5)
        for c in range(5):
            if not srmine_lst[c]:
                self.mine_coords.add((1,c))
        mine_lsts=[[1,2],[0,3],[1,3],[0,2],[1,2,3],[0,1,2],[0,1,3],[0,2,3]]
        mine_lst=random.choice(mine_lsts)
        for c in mine_lst:
            self.mine_coords.add((3,c))  #第四行布雷
        self.mine_coords.add((4,5))
        self.mine_coords.add((2,4))
        self.calculate_numbers()
        for c in range(self.cols):
            self.reveal(0,c)
            if (1,c) in self.mine_coords:  #处理第二行
                self.mark_mine(1,c)
            else:
                self.reveal(1,c)
             
            if (2,c) in self.mine_coords:   #处理第三行
                self.mark_mine(2,c)
            else:
                self.reveal(2,c)
        self.reveal(3,4)
        self.mode="exercise3" 
        self._update_training_panel_visibility()
    






#高级训练！！！
    def training_mode(self, n=None, s1=None, s2=None, d=None, p=None, three_con=None):
        cfg = self._sanitize_training_settings()
        random_mode = cfg.get('random_mode', False)
        if random_mode:
            if n is None:
                n = self._sample_random_training_n()
            if s1 is None:
                s1 = random.choice((1, 2, 3))
            if s2 is None:
                s2 = random.choice((1, 2, 3))
        else:
            if n is None:
                n = cfg['n']
            if s1 is None:
                s1 = cfg['s1']
            if s2 is None:
                s2 = cfg['s2']
        if d is None:
            d = cfg['d']
        if p is None:
            p = cfg['p']
        if three_con is None:
            three_con = cfg['three_con']
        if random_mode:
            try:
                # 随机模式下将本题参数写回设置变量，而不是仅用临时局部变量
                self.training_n_var.set(int(n))
                self.training_s1_var.set(int(s1))
                self.training_s2_var.set(int(s2))
                self._sync_training_label_vars()
                self.save_settings()
            except Exception:
                pass
        self._set_training_case_info(n, s1, s2, d, p, three_con, random_mode)
        #0
        self.mines=0
        self.rows=6
        col=n
        k=0
        k1=0
        if s1==1:
            t1=0
            col+=t1
            k1+=1
            k+=1
        elif s1==2:
            t1=3
            col+=t1
            k+=1
        elif s1==3:
            t1=5
            col+=t1
        if s2==1:
            t2=0
            k1+=1
            k+=1
        elif s2==2:
            t2=3
            col+=t2
            k+=1
        elif s2==3:
            t2=5
            col+=t2
        self.cols=col   
        self.create_widgets()
        #清盘
        self.mine_coords = set()
        self.revealed = set()
        self.marked = set()

        #1 雷行算法
        n1=n+2-k1 
        lst=[]


        def generate_sequence(n, p, constraint_type=1):
            """
            n: 序列长度
            p: 密度参数 [0, 1]
            constraint_type: 
                1 - 仅满足：没有连续三个 1
                2 - 满足：没有连续三个 1；且 1与2不能同时选中
                3 - 满足：没有连续三个 1；且 1与2不能同时选中，且 n-1与n不能同时选中
            """
            if n <= 0: return []
            if n == 1: return [1] if random.random() < p else [0]

            # 将 p 映射为权重 w (exp映射使 p 在 [0.1, 0.9] 之间时密度变化更线性)
            w = math.exp(p * 6 - 2) 

            # dp[i][j] 表示前 i 个数，末尾连续选了 j 个 1 的权重
            dp = [[0.0] * 3 for _ in range(n + 1)]
            
            # 初始化 i=1
            dp[1][0] = 1.0
            dp[1][1] = w
            
            # 正向计算权重
            for i in range(2, n + 1):
                # 状态 0: 当前不选
                dp[i][0] = dp[i-1][0] + dp[i-1][1] + dp[i-1][2]
                
                # 状态 1: 当前选，前一个没选
                dp[i][1] = dp[i-1][0] * w
                
                # 状态 2: 当前选，前一个也选了
                if (constraint_type >= 2) and (i == 2):
                    # 情况2和3：强制 1,2 不同选
                    dp[i][2] = 0.0
                else:
                    dp[i][2] = dp[i-1][1] * w

            # 
            if (constraint_type == 3):
                # 强制 n-1, n 不同选 (即不能以状态2结束)
                dp[n][2] = 0.0

            # 反向回溯采样
            sequence = [0] * n
            total_w = sum(dp[n])
            if total_w <= 0: return [0] * n
            
            # 抽取最后一个位置的状态
            r = random.uniform(0, total_w)
            if r < dp[n][0]: curr_state = 0
            elif r < dp[n][0] + dp[n][1]: curr_state = 1
            else: curr_state = 2
                
            for i in range(n, 0, -1):
                sequence[i-1] = 1 if curr_state > 0 else 0
                if i == 1: break
                
                if curr_state == 2:
                    curr_state = 1
                elif curr_state == 1:
                    curr_state = 0
                else:
                    # 当前没选，按比例回溯上一个状态
                    prev_sum = sum(dp[i-1])
                    r_p = random.uniform(0, prev_sum)
                    if r_p < dp[i-1][0]: curr_state = 0
                    elif r_p < dp[i-1][0] + dp[i-1][1]: curr_state = 1
                    else: curr_state = 2
                        
            return sequence

        
        if three_con:
            for _ in range(k):
                if random.random()<p:
                    lst.append(1)
                else:
                    lst.append(0)
        else:
            if s1==1 and s2==1:
                lst=generate_sequence(n1,p,3)
            elif s1==1 or s2==1:
                lst=list(reversed(generate_sequence(n1,p,2))) if s2==1 else generate_sequence(n1,p,2)
            else:
                lst=generate_sequence(n1,p,1)      

            
        #2难度选择

        def generate_sequence_advanced(n, p, d, constraint_type):
            """
            n: 长度
            p: 1的密度参数 [0, 1]
            d: 模式 (1:禁111, 2:禁000, 3:双禁)
            constraint_type: 
                1 - 无边际限制
                2 - 限制1&2: d=1时不能同为1, d=2时不能同为0, d=3时既不能同1也不能同0
                3 - 限制1&2 且 n-1&n: 规则同上
            """
            if n <= 0: return []
            if n == 1: return [1] if random.random() < p else [0]
            
            # 权重分配
            w = math.exp(p * 6 - 3)
            
            # 状态定义：-2(连00), -1(单0), 1(单1), 2(连11)
            all_states = [-2, -1, 1, 2]
            dp = [ {s: 0.0 for s in all_states} for _ in range(n + 1) ]
            
            # 初始化 i=1
            dp[1][-1] = 1.0  # 第一个选0
            dp[1][1] = w     # 第一个选1

            for i in range(2, n + 1):
                # --- 转移逻辑 ---
                # 变成单0 (-1): 前一个状态必须是 1 或 2
                dp[i][-1] = dp[i-1][1] + dp[i-1][2]
                
                # 变成连00 (-2): 前一个状态必须是 -1
                # 如果 d=1，-2代表“2个或更多0”；如果 d=2/3，最多只能连两个0
                dp[i][-2] = dp[i-1][-1]
                if d == 1: dp[i][-2] += dp[i-1][-2]

                # 变成单1 (1): 前一个状态必须是 -1 或 -2
                dp[i][1] = (dp[i-1][-1] + dp[i-1][-2]) * w
                
                # 变成连11 (2): 前一个状态必须是 1
                # 如果 d=2，2代表“2个或更多1”；如果 d=1/3，最多只能连两个1
                dp[i][2] = dp[i-1][1] * w
                if d == 2: dp[i][2] += dp[i-1][2] * w

                # --- 处理限制 2 (1&2 的边际约束) ---
                if i == 2 and constraint_type >= 2:
                    if d == 1 or d == 3:
                        dp[2][2] = 0.0  # 禁止 1,2 同时为 1
                    if d == 2 or d == 3:
                        dp[2][-2] = 0.0 # 禁止 1,2 同时为 0

            # --- 处理限制 3 (n-1&n 的边际约束) ---
            if constraint_type == 3:
                if d == 1 or d == 3:
                    dp[n][2] = 0.0  # 禁止最后两个同为 1
                if d == 2 or d == 3:
                    dp[n][-2] = 0.0 # 禁止最后两个同为 0

            # --- 反向回溯采样 ---
            sequence = [0] * n
            def get_state(weights_dict):
                s_list = list(weights_dict.keys())
                w_list = list(weights_dict.values())
                if sum(w_list) <= 0: return random.choice(s_list)
                return random.choices(s_list, weights=w_list)[0]

            curr_s = get_state(dp[n])
            for i in range(n, 0, -1):
                sequence[i-1] = 1 if curr_s > 0 else 0
                if i == 1: break
                
                prev_w = {s: 0.0 for s in all_states}
                if curr_s == -1:
                    prev_w[1], prev_w[2] = dp[i-1][1], dp[i-1][2]
                elif curr_s == -2:
                    prev_w[-1] = dp[i-1][-1]
                    if d == 1: prev_w[-2] = dp[i-1][-2]
                elif curr_s == 1:
                    prev_w[-1], prev_w[-2] = dp[i-1][-1], dp[i-1][-2]
                elif curr_s == 2:
                    prev_w[1] = dp[i-1][1]
                    if d == 2: prev_w[2] = dp[i-1][2]
                    
                curr_s = get_state(prev_w)
                    
            return sequence
                          

        #有解分析
        def judge(lst):
            #如果列表全为1
            if sum(lst)==len(lst):
                return False
            
            solu=False            
            if (s1==1 or s1==2) and (s2==1 or s2==2):
                if len(lst)%3!=2:
                    solu=True
                else:
                    k1,k2=0,1
                    if lst[0]==lst[1]:
                        solu=True
                    else:
                        while k1<len(lst):
                            if lst[k1]==lst[0]:
                                k1+=3
                            else:
                                solu=True
                                break
                        while k2<len(lst):
                            if lst[k2]==lst[1]:
                                k2+=3
                            else:
                                solu=True
                                break



            else:
                if s1==1 or s1 ==2:
                    k1,k2=0,1
                    if lst[0]==lst[1]:
                        solu=True
                    else:
                        while k1<len(lst):
                            if lst[k1]==lst[0]:
                                k1+=3
                            else:
                                solu=True
                                break
                        while k2<len(lst):
                            if lst[k2]==lst[1]:
                                k2+=3
                            else:
                                solu=True
                                break
                elif s2==1 or s2==2:
                    reve_lst=list(reversed(lst))
                    k1,k2=0,1
                    if reve_lst[0]==reve_lst[1]:
                        solu=True
                    else:
                        while k1<len(lst):
                            if reve_lst[k1]==reve_lst[0]:
                                k1+=3
                            else:
                                solu=True
                                break
                        while k2<len(lst):
                            if reve_lst[k2]==reve_lst[1]:
                                k2+=3
                            else:
                                solu=True
                                break
                elif s1==3 and s2==3:
                    if lst[0]==lst[1]==lst[2]:
                        solu=True
                    solu_lst=[0,0,0]
                    k1,k2,k3=0,1,2
                    while k1<len(lst):
                        if lst[k1]==lst[0]:
                            k1+=3
                        else:
                            solu_lst[0]=1
                            break
                    while k2<len(lst):
                        if lst[k2]==lst[1]:
                            k2+=3
                        else:
                            solu_lst[1]=1
                            break
                    while k3<len(lst):
                        if lst[k3]==lst[2]:
                            k3+=3
                        else:
                            solu_lst[2]=1
                            break
                    if sum(solu_lst)==0:
                        return False
                    elif sum(solu_lst)==1:
                        if solu_lst[0]==1 and lst[1]!=lst[2]:
                            return False
                        elif solu_lst[1]==1 and lst[0]!=lst[2]:
                            return False
                        elif solu_lst[2]==1 and lst[0]!=lst[1]:
                            return False
                        else:
                            solu=True
                    else:
                        solu=True
            return solu

        n2=n+2-k
        def generate2():
            if (s1==1 or s1==2) and (s2==1 or s2==2):
                lst2=generate_sequence_advanced(n2, 0.5, d, 3)
            elif s1==1 or s1==2:
                lst2=generate_sequence_advanced(n2, 0.5, d, 2)
            elif s2==1 or s2==2:
                lst2=list(reversed(generate_sequence_advanced(n2, 0.5, d, 2)))
            else:
                lst2=generate_sequence_advanced(n2, 0.5, d, 1)            
            return lst2
        
                
        solu=False
        while not solu :
            lst2=generate2()
            solu=judge(lst2)
            


        #开始布雷
        #雷行，墙从0开始，端从2开始，开放从4开始
        if s1==1:
            mine_dist=0
        if s1==2:
            mine_dist=2
        if s1==3:
            mine_dist=4
        
        for c in range(len(lst)):
            if lst[c] :
                self.mine_coords.add((2,c+mine_dist))
        
        #第四行小雷

        if s1==1:
            pass
        if s1==2:
            self.mine_coords.add((3,mine_dist))
        if s1==3:
            self.mine_coords.add((3,mine_dist))
        if s2==1:
            pass
        if s2==2:
            self.mine_coords.add((3,self.cols-1-2))
        if s2==3:
            self.mine_coords.add((3,self.cols-1-4))

        #第五行判雷区域

        if s1==1:
            train_dist=0
        if s1==2:
            train_dist=3
        if s1==3:
            train_dist=4
        for c in range(len(lst2)):
            if lst2[c] :
                self.mine_coords.add((4,c+train_dist))
        #第五行可选雷

        if s1==2:
            if random.random()<p:
                self.mine_coords.add((4,2))
        if s2==2:
            if random.random()<p:
                self.mine_coords.add((4,self.cols-1-2))


        #泛化最后一行

        if col%3==0:
            fan=1
            while fan<col:
                self.mine_coords.add((5,fan))
                fan+=3
                
        if col%3!=0:
            fan=0
            while fan<col:
                self.mine_coords.add((5,fan))
                fan+=3
                
        #泛化倒数第二行

        if s1==3:
            if (4,4) not in self.mine_coords:
                self.mine_coords.add((4,0))
                self.mine_coords.add((4,3))
            else:
                self.mine_coords.add((4,1))
            if random.random()<0.5:
                self.mine_coords.add((4,2))
        if s2==3:
            if (4,col-5) not in self.mine_coords:
                self.mine_coords.add((4,col-1))
                self.mine_coords.add((4,col-4))
            else:
                self.mine_coords.add((4,col-2))
            if random.random()<0.5:
                self.mine_coords.add((4,col-3))

        self.calculate_numbers()

        #最后进行揭开和标旗操作
        self.reveal(0,0)
        for c in range(col):
            if (2,c) in self.mine_coords:  #处理第三行
                self.mark_mine(2,c)
            else:
                self.reveal(2,c)
             
            if (3,c) in self.mine_coords:   #处理第四行
                self.mark_mine(3,c)
            else:
                self.reveal(3,c)
        if s1==2:
            self.reveal(4,0)
            self.reveal(4,1)
            if (4,2) not in self.mine_coords:   
                self.reveal(4,2)
            else:
                self.mark_mine(4,2) 
        if s2==2:
            self.reveal(4,col-1)
            self.reveal(4,col-2)
            if (4,col-3) not in self.mine_coords:
                self.reveal(4,col-3)
            else:
                self.mark_mine(4,col-3)


        self.mode="training_mode" 
        self._update_training_panel_visibility()
        self._refresh_training_win_highlight({'s1': s1, 's2': s2})

    




    def reveal(self,r,c):
        """翻开格子"""
        if (r, c) in self.marked or (r, c) in self.revealed:
            return

        # 在传统模式下，首次点击应保证开空（数字0）——在 reveal 开始时调整雷位
        try:
            if getattr(self, 'mode', None) == 'tradition' and getattr(self, 'first_click', True):
                # 如果总格子数过小或雷太多，跳过保证开空以避免无限重排
                total = self.rows * self.cols
                if self.mines <= max(0, total - 9):
                    try:
                        self._ensure_first_click_empty(r, c)
                    except Exception:
                        pass
                self.first_click = False
        except Exception:
            pass

        if (r, c) in self.mine_coords:
            self.game_over()
            return
        
        if r>self.rows-1 or c>self.cols-1:
            return
        
        self.revealed.add((r, c))
        num = self.numbers.get((r, c), 0)
        self.canvas.delete(self.image_map[r][c])
        x1,y1=(c+0.5)*self.size,(r+0.5)*self.size
        self.image_map[r][c]=self.canvas.create_image(x1, y1, image=self.type_imgs[num])
        
        if num == 0:
            # 自动翻开周围格子
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal(nr, nc)
                        self.revealed.add((nr, nc))
        
        self.check_win()
        
    def on_left_press(self, event):
        """左键按下"""
        self.left_pressed = True
        r = event.y//self.size
        c = event.x//self.size
        self.left_press_coord = (r, c)
        # 按下时切换重启图标为按下状态（闪电2.jpg）
        try:
            if not getattr(self, 'finished', False):
                self.set_restart_icon('press')
        except Exception:
            pass
        if self.right_pressed:
            # 同时按下左右键，显示中心及周围临时 type0 图标，延迟实际 double_click 到释放时
            self.both_pressed = True
            self.last_press_center = (r, c)
            # 显示临时图标
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if (nr, nc) in self.revealed or (nr, nc) in self.marked:
                            continue
                        try:
                            self.canvas.delete(self.image_map[nr][nc])
                        except Exception:
                            pass
                        x = (nc+0.5) * self.size
                        y = (nr+0.5) * self.size
                        self.image_map[nr][nc] = self.canvas.create_image(x, y, image=self.type_imgs[0])
                        self.pressed_cells.add((nr, nc))
        else:
            # 单纯左键按下，仅把该格变为 type0（临时）
            if 0 <= r < self.rows and 0 <= c < self.cols and (r, c) not in self.revealed and (r, c) not in self.marked:
                try:
                    self.canvas.delete(self.image_map[r][c])
                except Exception:
                    pass
                x = (c+0.5) * self.size
                y = (r+0.5) * self.size
                self.image_map[r][c] = self.canvas.create_image(x, y, image=self.type_imgs[0])
                self.pressed_cells.add((r, c))
    
    def on_left_release(self, event):
        """左键释放"""
        r = event.y//self.size
        c = event.x//self.size
        # 先记录当前双键状态，然后标记左键已释放
        was_both = self.both_pressed
        self.left_pressed = False

        if was_both:
            # 在双键按下场景，只需任意一个键松开即可执行 double_click
            center = self.last_press_center or (r, c)
            before = set(self.revealed)
            self.double_click(center[0], center[1])
            after = set(self.revealed)
            # 如果 double_click 没有实际翻开任何新格，则需要把临时显示的格恢复为覆盖态
            if after == before:
                for (nr, nc) in list(self.pressed_cells):
                    if (nr, nc) not in self.revealed and (nr, nc) not in self.marked:
                        try:
                            self.canvas.delete(self.image_map[nr][nc])
                        except Exception:
                            pass
                        x = (nc+0.5) * self.size
                        y = (nr+0.5) * self.size
                        self.image_map[nr][nc] = self.canvas.create_image(x, y, image=self.mine_imgs[-1])
            # 清理状态
            self.pressed_cells.clear()
            self.both_pressed = False
            self.last_press_center = None
        else:
            # 单次左键释放且右键未按下 -> 翻开
            if not self.right_pressed:
                press_coord = self.left_press_coord
                if press_coord is not None and press_coord == (r, c):
                    self.reveal(r, c)
                else:
                    # 拖拽到其他位置释放：恢复按下时临时显示的格子
                    for (nr, nc) in list(self.pressed_cells):
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in self.revealed and (nr, nc) not in self.marked:
                            try:
                                self.canvas.delete(self.image_map[nr][nc])
                            except Exception:
                                pass
                            x = (nc+0.5) * self.size
                            y = (nr+0.5) * self.size
                            self.image_map[nr][nc] = self.canvas.create_image(x, y, image=self.mine_imgs[-1])
                self.pressed_cells.clear()
        self.left_press_coord = None

        # 释放后恢复重启图标为普通状态（若游戏未结束）
        try:
            if not getattr(self, 'finished', False):
                self.set_restart_icon('normal')
        except Exception:
            pass
    
    def on_right_press(self, event):
        """右键按下"""
        self.right_pressed = True
        r = event.y//self.size
        c = event.x//self.size
        # 右键按下不改变闪电图标（只在左键按下时切换）
        if self.left_pressed:
            # 同时按下左右键，显示中心及周围临时 type0 图标，延迟实际 double_click 到释放时
            self.both_pressed = True
            self.last_press_center = (r, c)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if (nr, nc) in self.revealed or (nr, nc) in self.marked:
                            continue
                        try:
                            self.canvas.delete(self.image_map[nr][nc])
                        except Exception:
                            pass
                        x = (nc+0.5) * self.size
                        y = (nr+0.5) * self.size
                        self.image_map[nr][nc] = self.canvas.create_image(x, y, image=self.type_imgs[0])
                        self.pressed_cells.add((nr, nc))
        else:
            # 若未同时按下左键，则在按下时立即执行标记操作（按下即布雷）
            try:
                self.mark_mine(r, c)
                # 记录此坐标以在 release 时避免重复标记
                self.right_did_mark_on_press = True
                self.right_marked_coord = (r, c)
            except Exception:
                # 忽略任何标记时的异常，保证按下不会中断流程
                self.right_did_mark_on_press = False
                self.right_marked_coord = None
    
    def on_right_release(self, event):
        """右键释放"""
        r = event.y//self.size
        c = event.x//self.size
        was_both = self.both_pressed
        # 标记右键已释放
        self.right_pressed = False

        if was_both:
            # 在双键按下场景，只需任意一个键松开即可执行 double_click
            center = self.last_press_center or (r, c)
            before = set(self.revealed)
            self.double_click(center[0], center[1])
            after = set(self.revealed)
            if after == before:
                for (nr, nc) in list(self.pressed_cells):
                    if (nr, nc) not in self.revealed and (nr, nc) not in self.marked:
                        try:
                            self.canvas.delete(self.image_map[nr][nc])
                        except Exception:
                            pass
                        x = (nc+0.5) * self.size
                        y = (nr+0.5) * self.size
                        self.image_map[nr][nc] = self.canvas.create_image(x, y, image=self.mine_imgs[-1])
            self.pressed_cells.clear()
            self.both_pressed = False
            self.last_press_center = None
        else:
            # 单独右键释放，且左键未按下 -> 若按下时未已执行标记，则在释放时执行标记
            if not self.left_pressed:
                if not self.right_did_mark_on_press:
                    # 只有在按下时未标记过同一格时，才在释放时执行标记
                    self.mark_mine(r, c)

        # 无论如何，清理按下时记录的标记状态（避免长期保留）
        self.right_did_mark_on_press = False
        self.right_marked_coord = None

        # 右键释放不改变闪电图标（闪电由左键按下/释放控制）
    
    def on_middle_press(self, event):
        """中键按下，重新开始游戏"""
        self.restart()
        
    def double_click(self, r, c):
        """双击翻开周围格子"""
        if (r, c) not in self.revealed or (r, c) in self.marked:
            return
        
        num = self.numbers.get((r, c), 0)
        if num == 0:
            return
        
        # 检查周围是否有标记的地雷
        marked_count = sum((r+dr, c+dc) in self.marked for dr in [-1, 0, 1] for dc in [-1, 0, 1])
        
        if marked_count == num:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal(nr, nc)

    def mark_mine(self,r,c):
        """右键标记地雷"""
        x1,y1=(c+0.5)*self.size,(r+0.5)*self.size
        if (r, c) in self.revealed:
            return
        
        if r>self.rows-1 or c>self.cols-1:
            return
        
        if (r, c) in self.marked:
            self.marked.remove((r, c))
            self.canvas.delete(self.image_map[r][c])
            self.image_map[r][c]=self.canvas.create_image(x1, y1, image=self.mine_imgs[-1])
        else:
            self.marked.add((r, c))
            self.canvas.delete(self.image_map[r][c])
            self.image_map[r][c]=self.canvas.create_image(x1, y1, image=self.mine_imgs[-2])


    def place_mines(self):
        """随机布置地雷"""
        while len(self.mine_coords) < self.mines:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            self.mine_coords.add((r, c))

    def calculate_numbers(self):
        """计算每个格子的数字"""
        self.numbers = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.mine_coords:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if (r+dr, c+dc) in self.mine_coords:
                            count += 1
                self.numbers[(r, c)] = count

    def _ensure_first_click_empty(self, r, c):
        """确保在第一次点击 (r,c) 时该格及其 8 个邻格没有地雷。
        通过从这些格子中移除地雷并在其他合法格子补回相同数量的雷来保持总雷数不变。
        在极端情况下（雷过多）此函数会跳过修改。
        """
        # 确定禁止放雷的格子（中心及其周围 3x3）
        forbidden = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    forbidden.add((nr, nc))

        # 移除 forbidden 区域内的雷并记录被移除的数量
        removed = 0
        for coord in list(self.mine_coords):
            if coord in forbidden:
                self.mine_coords.remove(coord)
                removed += 1

        # 将移除的雷在其他可用格子中随机补回，避免放到 forbidden 或已存在雷的格子
        available = [ (rr,cc) for rr in range(self.rows) for cc in range(self.cols)
                      if (rr,cc) not in self.mine_coords and (rr,cc) not in forbidden ]
        # 如果可用格子不足，退回：把移除的雷放回并放弃确保
        if len(available) < removed:
            # 回填回原始（把刚刚移除的坐标重新加入）
            for coord in list(forbidden):
                if coord not in self.mine_coords and len(self.mine_coords) < self.mines:
                    self.mine_coords.add(coord)
            return

        # 随机选择位置补雷
        if removed > 0:
            new_positions = random.sample(available, removed)
            for pos in new_positions:
                self.mine_coords.add(pos)

        # 重新计算数字字典
        self.calculate_numbers()

    
        

    def game_over(self):
        """游戏失败处理"""
        for r, c in self.mine_coords:
            self.canvas.delete(self.image_map[r][c])
            self.image_map[r][c]=self.canvas.create_image((c+0.5)*self.size, (r+0.5)*self.size, image=self.mine_imgs[1])
        # 不弹窗也不自动重置，直接切换重启图标为失败并禁用操作
        try:
            self.set_restart_icon('fail')
        except Exception:
            pass
        # 标记游戏已结束，禁用后续切换到普通图标
        self.finished = True
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<ButtonPress-3>")
        self.canvas.unbind("<ButtonRelease-3>")
        # 若设置了失败自动重开，则在短延迟后重开（800ms），以便玩家看到失败反馈
        try:
            if getattr(self, 'auto_restart_on_fail_var', None) and self.auto_restart_on_fail_var.get():
                try:
                    self.root.after(800, self.restart)
                except Exception:
                    # 回退到立即重开
                    self.restart()
        except Exception:
            pass

    def _refresh_training_win_highlight(self, cfg=None):
        """高亮 training_mode 中第四行满足胜利判定条件的格子。"""
        try:
            self.canvas.delete("training_win_highlight")
        except Exception:
            pass

        try:
            if not self.training_highlight_var.get():
                return
        except Exception:
            return

        if getattr(self, 'mode', None) != 'training_mode':
            return

        if cfg is None:
            try:
                cfg = self._sanitize_training_settings()
            except Exception:
                return

        row = 4
        if row < 0 or row >= self.rows:
            return

        for c in range(self.cols):
            ok = True
            if (row, c) in self.revealed:
                ok = False
            elif (row, c) in self.marked:
                ok = False
            elif cfg['s1'] == 3 and c in range(0, 4):
                ok = False
            elif cfg['s2'] == 3 and c in range(self.cols-4, self.cols):
                ok = False

            if ok:
                x0 = c * self.size + 1
                y0 = row * self.size + 1
                x1 = (c + 1) * self.size - 1
                y1 = (row + 1) * self.size - 1
                try:
                    self.canvas.create_rectangle(
                        x0, y0, x1, y1,
                        outline="#24A9FF",
                        width=2,
                        tags="training_win_highlight"
                    )
                except Exception:
                    pass

    def check_win(self):
        """检查胜利条件"""
        # 所有非雷格子都被翻开
        finish=False
        if self.mode in ("tradition", "find_mine"):
            non_mines = self.rows * self.cols - self.mines
            if len(self.revealed) == non_mines:
                finish = True

        elif self.mode =='exercise1':
            finish=True
            for c in range(30):
                if (2,c) in self.revealed:
                    pass
                elif (2,c) in self.mine_coords:
                    pass
                else:
                    finish=False
                    break
        elif self.mode =='exercise2':
            finish=True
            for c in range(3):
                if (3,c) in self.revealed:
                    pass
                elif (3,c) in self.mine_coords:
                    pass
                else:
                    finish=False
                    break
        elif self.mode =='exercise3':
            finish=True
            for c in range(4):
                if (3,c) in self.revealed:
                    pass
                elif (3,c) in self.mine_coords:
                    pass
                else:
                    finish=False
                    break

        if self.mode =='training_mode':

            finish=True
            cfg=self._sanitize_training_settings()
            self._refresh_training_win_highlight(cfg)
            for c in range(self.cols):
                if (4,c) in self.revealed:
                    pass
                elif (4,c) in self.mine_coords:
                    pass
                elif cfg['s1'] == 3 and c in range(0,4):
                    pass
                elif cfg['s2'] == 3 and c in range(self.cols-4,self.cols):
                    pass
                else:
                    finish=False
                    break
        
        if finish:
        # 胜利：切换重启图标为 success，禁用输入，不自动重启
            try:
                self.set_restart_icon('success')
            except Exception:
                pass
            # 标记游戏已结束
            self.finished = True
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.unbind("<ButtonPress-3>")
            self.canvas.unbind("<ButtonRelease-3>")
            # 若设置了胜利自动重开，则在短延迟后重开（800ms），以便玩家看到胜利反馈
            try:
                if getattr(self, 'auto_restart_on_win_var', None) and self.auto_restart_on_win_var.get():
                    try:
                        self.root.after(800, self.restart)
                    except Exception:
                        self.restart()
            except Exception:
                pass

        
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("闪电扫雷")
    game = Minesweeper(master=root)
    root.mainloop()
    
# 


