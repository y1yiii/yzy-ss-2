import tkinter as tk
from tkinter import messagebox
import random
import time

class Minesweeper:
    COLOR_SCHEME = {
        -1: "#424242",   # 地雷颜色
        0: "#e0e0e0",    # 空白区域
        1: "#1976d2",    # 蓝色
        2: "#388e3c",    # 绿色
        3: "#d32f2f",    # 红色
        4: "#7b1fa2",    # 紫色
        5: "#ff8f00",    # 橙色
        6: "#0097a7",    # 青色
        7: "#5d4037",    # 棕色
        8: "#616161"      # 灰色
    }

    def __init__(self, master, rows=10, cols=10, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = []
        self.buttons = []
        self.first_click = True
        self.flags = 0
        self.start_time = None
        
        master.configure(bg="#f5f5f5")
        self.create_widgets()
        self.init_grid()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.master.title("🎯 趣味扫雷 🎯")
        # 顶部状态栏
        status_bar = tk.Frame(self.master, bg="#f5f5f5")
        status_bar.grid(row=0, columnspan=self.cols, sticky="ew")
        
        self.flag_label = tk.Label(status_bar, 
                                 text=f"🚩 {self.mines}",
                                 font=("微软雅黑", 12, "bold"),
                                 bg="#f5f5f5",
                                 fg="#d32f2f")
        self.flag_label.pack(side=tk.LEFT, padx=10)
        
        self.timer_label = tk.Label(status_bar, 
                                  text="⏳ 00:00",
                                  font=("微软雅黑", 12),
                                  bg="#f5f5f5")
        self.timer_label.pack(side=tk.RIGHT, padx=10)

        # 游戏网格
        grid_frame = tk.Frame(self.master, bg="#bdbdbd")
        grid_frame.grid(row=1, columnspan=self.cols, padx=5, pady=5)
        
        btn_size = 28 if self.cols <= 15 else 24
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(grid_frame, 
                              width=2, 
                              height=1,
                              font=("Arial", 10, "bold"),
                              relief="raised",
                              bg="#eeeeee",
                              activebackground="#bdbdbd")
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        self.start_timer()

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"⏳ {elapsed//60:02d}:{elapsed%60:02d}")
        self.master.after(1000, self.update_timer)

    def init_grid(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def generate_mines(self, exclude_r, exclude_c):
        mines_placed = 0
        while mines_placed < self.mines:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            if (r != exclude_r or c != exclude_c) and self.grid[r][c] != -1:
                self.grid[r][c] = -1
                mines_placed += 1

        # 计算周围雷数并应用颜色方案
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1:
                    count = self.count_mines(r, c)
                    self.grid[r][c] = count

    def count_mines(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] == -1:
                        count += 1
        return count

    def left_click(self, r, c):
        btn = self.buttons[r][c]
        if btn["state"] == "disabled" or btn["text"] == "🚩":
            return

        if self.first_click:
            self.generate_mines(r, c)
            self.first_click = False

        if self.grid[r][c] == -1:
            self.game_over()
        else:
            self.reveal(r, c)
            self.check_win()

    def right_click(self, r, c):
        btn = self.buttons[r][c]
        if btn["state"] == "disabled":
            return

        if btn["text"] == "🚩":
            btn.config(text="", fg="black")
            self.flags -= 1
        else:
            if self.flags < self.mines:
                btn.config(text="🚩", fg="#d32f2f", font=("Segoe UI Emoji", 10))
                self.flags += 1
        self.flag_label.config(text=f"🚩 剩余雷数: {self.mines - self.flags}")

    def reveal(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols and self.buttons[r][c]["state"] == "normal":
            value = self.grid[r][c]
            btn = self.buttons[r][c]
            
            if value > 0:
                color = self.COLOR_SCHEME.get(value, "black")
                btn.config(text=str(value), fg=color, relief="sunken", state="disabled")
            else:
                btn.config(relief="sunken", bg="#e0e0e0", state="disabled")
                # 递归展开空白区域
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr != 0 or dc != 0:
                            self.reveal(r + dr, c + dc)

    def check_win(self):
        safe_cells = self.rows * self.cols - self.mines
        opened = sum(1 for row in self.buttons for btn in row if btn["state"] == "disabled")
        if opened == safe_cells:
            self.show_victory_animation()
            if messagebox.askyesno("🎉 胜利！", "恭喜扫雷成功！\n\n再玩一局吗？", 
                                  icon="info", parent=self.master):
                self.restart_game()
            else:
                self.master.destroy()

    def game_over(self):
        self.show_mine_explosion()
        if messagebox.askyesno("💥 游戏结束", "很遗憾踩到地雷了！\n\n再试一次吗？", 
                             icon="warning", parent=self.master):
            self.restart_game()
        else:
            self.master.destroy()

    def show_mine_explosion(self):
        # 地雷爆炸动画效果
        colors = ["#ff0000", "#ff4444", "#ff8888"]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    btn = self.buttons[r][c]
                    btn.config(text="💣", bg="#ff0000", font=("Segoe UI Emoji", 10))
                    for i, color in enumerate(colors):
                        self.master.after(100*i, lambda btn=btn, color=color: 
                                         btn.config(bg=color))

    def show_victory_animation(self):
        # 胜利动画效果
        colors = ["#4CAF50", "#81C784", "#A5D6A7"]
        for i, color in enumerate(colors * 2):
            self.master.after(200*i, lambda: [
                btn.config(bg=color) for row in self.buttons for btn in row 
                if btn["state"] == "disabled"
            ])

    def restart_game(self):
        self.master.destroy()
        new_window = tk.Toplevel()
        Minesweeper(new_window, self.rows, self.cols, self.mines)

    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出游戏吗？", parent=self.master):
            self.master.destroy()

class DifficultySelector:
    THEME_COLORS = {
        "background": "#f0f2f5",
        "button_bg": "#ffffff",
        "button_fg": "#2d3436",
        "hover_bg": "#dfe6e9"
    }

    def __init__(self, master):
        self.master = master
        self.master.title("⚙️ 扫雷 - 难度选择")
        self.master.geometry("400x500")
        self.master.resizable(False, False)
        self.master.configure(bg=self.THEME_COLORS["background"])
        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(self.master, 
                         text="选择游戏难度",
                         font=("微软雅黑", 14, "bold"),
                         bg=self.THEME_COLORS["background"],
                         fg="#2d3436")
        header.pack(pady=15)

        difficulties = [
            ("🍀 简单模式 (9×9, 10雷)", 9, 9, 10, "#4CAF50"),
            ("🎯 中等模式 (16×16, 40雷)", 16, 16, 40, "#FF9800"),
            ("💣 困难模式 (30×16, 99雷)", 16, 30, 99, "#D32F2F")
        ]

        for text, r, c, m, color in difficulties:
            btn = tk.Button(self.master,
                           text=text,
                           width=25,
                           font=("微软雅黑", 11),
                           bg=self.THEME_COLORS["button_bg"],
                           fg=color,
                           activebackground=color,
                           activeforeground="white",
                           relief="groove",
                           borderwidth=2,
                           padx=10,
                           pady=5)
            btn.config(command=lambda r=r, c=c, m=m: self.start_game(r, c, m))
            btn.pack(pady=6, ipady=3)
            btn.bind("<Enter>", lambda e, btn=btn: btn.config(bg=btn.cget("fg"), fg="white"))
            btn.bind("<Leave>", lambda e, btn=btn: btn.config(bg=self.THEME_COLORS["button_bg"], fg=btn.cget("fg")))

        # 自定义设置区域
        custom_frame = tk.Frame(self.master, bg=self.THEME_COLORS["background"])
        custom_frame.pack(pady=15, padx=20)

        entries = [
            ("📏 行数 (1-30):", "rows_entry", 10),
            ("📐 列数 (1-30):", "cols_entry", 10),
            ("💥 地雷数:", "mines_entry", 10)
        ]

        for label_text, entry_name, default in entries:
            frame = tk.Frame(custom_frame, bg=self.THEME_COLORS["background"])
            frame.pack(fill=tk.X, pady=4)
            
            tk.Label(frame, 
                    text=label_text,
                    font=("微软雅黑", 10),
                    bg=self.THEME_COLORS["background"],
                    fg="#2d3436").pack(side=tk.LEFT, padx=5)
            
            entry = tk.Entry(frame, 
                            width=8,
                            font=("Arial", 10),
                            relief="solid",
                            borderwidth=1)
            entry.insert(0, str(default))
            entry.pack(side=tk.RIGHT)
            setattr(self, entry_name, entry)

        custom_btn = tk.Button(self.master,
                              text="🎮 开始自定义游戏",
                              font=("微软雅黑", 11, "bold"),
                              bg="#2196F3",
                              fg="white",
                              activebackground="#1976D2",
                              relief="groove",
                              command=self.start_custom_game)
        custom_btn.pack(pady=15, ipadx=10, ipady=5)
        self.add_hover_effect(custom_btn, "#1976D2")

    def add_hover_effect(self, widget, hover_color):
        original_bg = widget.cget("bg")
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color, fg="white"))
        widget.bind("<Leave>", lambda e: widget.config(bg=original_bg, fg=hover_color))

    def validate_input(self, rows, cols, mines):
        if not (1 <= rows <= 30 and 1 <= cols <= 30):
            raise ValueError("行数和列数必须在1-30之间")
        if mines <= 0:
            raise ValueError("地雷数必须大于0")
        if mines >= rows * cols:
            raise ValueError("地雷数不能超过总格子数")
        return True

    def start_game(self, rows, cols, mines):
        game_window = tk.Toplevel(self.master)
        Minesweeper(game_window, rows=rows, cols=cols, mines=mines)

    def start_custom_game(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            mines = int(self.mines_entry.get())
            
            self.validate_input(rows, cols, mines)
            self.start_game(rows, cols, mines)
            
        except ValueError as e:
            messagebox.showerror("输入错误", 
                               f"无效设置:\n{str(e)}",
                               parent=self.master)


if __name__ == "__main__":
    root = tk.Tk()
    DifficultySelector(root)
    root.mainloop()