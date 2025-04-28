import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = []          # 存储地雷和数字信息（-1表示雷，0-8表示周围雷数）
        self.buttons = []       # 存储按钮控件
        self.first_click = True # 标记首次点击
        self.flags = 0          # 标记的旗帜数量
        self.create_widgets()
        self.init_grid()

    def create_widgets(self):
        # 创建游戏窗口和按钮布局
        self.master.title("扫雷")
        self.flag_label = tk.Label(self.master, text=f"剩余雷数: {self.mines}")
        self.flag_label.grid(row=self.rows, columnspan=self.cols)

        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(self.master, width=2, height=1, relief="raised",
                                font=("Arial", 12, "bold"))
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                btn.grid(row=r, column=c)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def init_grid(self):
        # 初始化所有格子为0（未生成地雷）
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def generate_mines(self, exclude_r, exclude_c):
        # 排除首次点击位置后随机生成地雷
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
        # 统计周围8格中的地雷数量
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] == -1:
                        count += 1
        return count

    def left_click(self, r, c):
        # 左键点击事件
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
        # 右键标记地雷
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
        # 递归展开空白区域
        if 0 <= r < self.rows and 0 <= c < self.cols and self.buttons[r][c]["state"] == "normal":
            value = self.grid[r][c]
            self.buttons[r][c].config(
                text=str(value) if value > 0 else "",
                relief="sunken",
                state="disabled",
                bg="#d9d9d9"
            )
            if value == 0:
                # 递归展开周围8格
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        self.reveal(r + dr, c + dc)

    def check_win(self):
        # 检查是否胜利（所有安全格已点开）
        safe_cells = self.rows * self.cols - self.mines
        opened = sum(
            1 for r in range(self.rows)
            for c in range(self.cols)
            if self.buttons[r][c]["state"] == "disabled"
        )
        if opened == safe_cells:
            messagebox.showinfo("胜利", "你成功了！")
            self.master.destroy()

    def game_over(self):
        # 显示所有地雷位置
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.buttons[r][c].config(text="💣", bg="red")
        messagebox.showinfo("游戏结束", "你踩到地雷了！")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root, rows=10, cols=10, mines=10)
    root.mainloop()