import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = []          # 存储地雷和数字信息
        self.buttons = []       # 存储按钮控件
        self.first_click = True # 首次点击标记
        self.flags = 0          # 旗帜数量
        self.create_widgets()
        self.init_grid()

        # 绑定窗口关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.master.title("扫雷")
        self.flag_label = tk.Label(self.master, text=f"剩余雷数: {self.mines}")
        self.flag_label.grid(row=self.rows, columnspan=self.cols)

        # 动态调整按钮大小
        btn_width = 3 if self.cols > 15 else 2
        btn_font = ("Arial", 8 if self.cols > 15 else 10, "bold")
        
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(self.master, width=btn_width, height=1, 
                               relief="raised", font=btn_font)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                btn.grid(row=r, column=c)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

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

        # 计算周围雷数
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1:
                    self.grid[r][c] = self.count_mines(r, c)

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
        if self.buttons[r][c]["state"] == "disabled" or self.buttons[r][c]["text"] == "🚩":
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
        if self.buttons[r][c]["state"] == "disabled":
            return

        if self.buttons[r][c]["text"] == "🚩":
            self.buttons[r][c].config(text="")
            self.flags -= 1
        else:
            if self.flags < self.mines:
                self.buttons[r][c].config(text="🚩")
                self.flags += 1
        self.flag_label.config(text=f"剩余雷数: {self.mines - self.flags}")

    def reveal(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols and self.buttons[r][c]["state"] == "normal":
            value = self.grid[r][c]
            self.buttons[r][c].config(
                text=str(value) if value > 0 else "",
                relief="sunken",
                state="disabled",
                bg="#d9d9d9"
            )
            if value == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        self.reveal(r + dr, c + dc)

    def check_win(self):
        safe_cells = self.rows * self.cols - self.mines
        opened = sum(
            1 for r in range(self.rows)
            for c in range(self.cols)
            if self.buttons[r][c]["state"] == "disabled"
        )
        if opened == safe_cells:
            if messagebox.askyesno("胜利", "你成功了！\n再玩一局吗？"):
                self.restart_game()
            else:
                self.master.destroy()

    def game_over(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.buttons[r][c].config(text="💣", bg="red")
        if messagebox.askyesno("游戏结束", "你踩到地雷了！\n再试一次吗？"):
            self.restart_game()
        else:
            self.master.destroy()

    def restart_game(self):
        self.master.destroy()
        new_window = tk.Toplevel()
        Minesweeper(new_window, self.rows, self.cols, self.mines)

    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            self.master.destroy()

class DifficultySelector:
    def __init__(self, master):
        self.master = master
        self.master.title("扫雷 - 设置")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="选择难度级别", font=("Arial", 12)).pack(pady=10)
        
        difficulties = [
            ("简单 (9×9, 10雷)", 9, 9, 10),
            ("中等 (16×16, 40雷)", 16, 16, 40),
            ("困难 (30×16, 99雷)", 16, 30, 99)
        ]
        
        for text, r, c, m in difficulties:
            btn = tk.Button(self.master, text=text, width=20,
                           command=lambda r=r, c=c, m=m: self.start_game(r, c, m))
            btn.pack(pady=2)

        custom_frame = tk.Frame(self.master)
        custom_frame.pack(pady=15)
        
        entries = [
            ("行数 (1-30):", "rows_entry", 10),
            ("列数 (1-30):", "cols_entry", 10),
            ("地雷数:", "mines_entry", 10)
        ]
        
        for idx, (label_text, entry_name, default) in enumerate(entries):
            frame = tk.Frame(custom_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=label_text, width=12).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=8)
            entry.pack(side=tk.LEFT)
            entry.insert(0, str(default))
            setattr(self, entry_name, entry)
        
        tk.Button(self.master, text="开始自定义游戏", command=self.start_custom_game,
                 bg="#e0e0ff").pack(pady=10)

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
            messagebox.showerror("输入错误", f"无效设置:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    DifficultySelector(root)
    root.mainloop()