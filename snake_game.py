"""一个基于 Tkinter 的经典贪吃蛇小游戏。

运行方式:
    python snake_game.py

操作说明:
    - 方向键 / WASD: 控制蛇移动
    - 空格: 暂停/继续
    - R: 游戏结束后重新开始
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class SnakeGame:
    def __init__(self) -> None:
        self.cell_size = 20
        self.grid_width = 30
        self.grid_height = 20
        self.width = self.grid_width * self.cell_size
        self.height = self.grid_height * self.cell_size

        self.initial_speed_ms = 140
        self.speed_up_every_food = 2
        self.min_speed_ms = 70

        self.root = tk.Tk()
        self.root.title("贪吃蛇 Snake Game")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#0f172a",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status_var = tk.StringVar(value="按方向键或 WASD 开始")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 12),
            anchor="w",
            padx=10,
        )
        self.status_label.pack(fill="x")

        self.root.bind("<Up>", lambda _: self.set_direction(Point(0, -1)))
        self.root.bind("<Down>", lambda _: self.set_direction(Point(0, 1)))
        self.root.bind("<Left>", lambda _: self.set_direction(Point(-1, 0)))
        self.root.bind("<Right>", lambda _: self.set_direction(Point(1, 0)))

        self.root.bind("w", lambda _: self.set_direction(Point(0, -1)))
        self.root.bind("s", lambda _: self.set_direction(Point(0, 1)))
        self.root.bind("a", lambda _: self.set_direction(Point(-1, 0)))
        self.root.bind("d", lambda _: self.set_direction(Point(1, 0)))

        self.root.bind("<space>", lambda _: self.toggle_pause())
        self.root.bind("r", lambda _: self.restart_if_over())

        self.game_over = False
        self.paused = False
        self.pending_job: str | None = None

        self.reset_game()

    def reset_game(self) -> None:
        center = Point(self.grid_width // 2, self.grid_height // 2)
        self.snake = [center, Point(center.x - 1, center.y), Point(center.x - 2, center.y)]
        self.direction = Point(1, 0)
        self.next_direction = self.direction

        self.score = 0
        self.speed_ms = self.initial_speed_ms
        self.food = self.random_food_position()

        self.game_over = False
        self.paused = False
        self.update_status("开始游戏！")
        self.draw()

        if self.pending_job is not None:
            self.root.after_cancel(self.pending_job)
            self.pending_job = None
        self.schedule_tick()

    def schedule_tick(self) -> None:
        self.pending_job = self.root.after(self.speed_ms, self.tick)

    def set_direction(self, direction: Point) -> None:
        if self.game_over:
            return
        if direction.x == -self.direction.x and direction.y == -self.direction.y:
            return
        self.next_direction = direction

    def toggle_pause(self) -> None:
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.update_status(f"已暂停 | 分数: {self.score} | 空格继续")
        else:
            self.update_status(f"继续游戏 | 分数: {self.score}")

    def restart_if_over(self) -> None:
        if self.game_over:
            self.reset_game()

    def random_food_position(self) -> Point:
        occupied = set(self.snake)
        all_cells = [
            Point(x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if Point(x, y) not in occupied
        ]
        return random.choice(all_cells)

    def tick(self) -> None:
        if self.game_over:
            return
        if self.paused:
            self.schedule_tick()
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        hit_wall = (
            new_head.x < 0
            or new_head.x >= self.grid_width
            or new_head.y < 0
            or new_head.y >= self.grid_height
        )
        hit_self = new_head in self.snake

        if hit_wall or hit_self:
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            if self.score % self.speed_up_every_food == 0:
                self.speed_ms = max(self.min_speed_ms, self.speed_ms - 8)
            self.food = self.random_food_position()
        else:
            self.snake.pop()

        self.update_status(f"分数: {self.score} | 速度: {1000 // self.speed_ms} 格/秒")
        self.draw()
        self.schedule_tick()

    def end_game(self) -> None:
        self.game_over = True
        self.draw()
        self.update_status(f"游戏结束！最终分数: {self.score} | 按 R 重新开始")

    def draw(self) -> None:
        self.canvas.delete("all")

        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#0f172a", outline="")

        fx1 = self.food.x * self.cell_size
        fy1 = self.food.y * self.cell_size
        fx2 = fx1 + self.cell_size
        fy2 = fy1 + self.cell_size
        self.canvas.create_oval(fx1 + 2, fy1 + 2, fx2 - 2, fy2 - 2, fill="#ef4444", outline="")

        for idx, segment in enumerate(self.snake):
            x1 = segment.x * self.cell_size
            y1 = segment.y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            color = "#22c55e" if idx == 0 else "#16a34a"
            self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline="")

        if self.game_over:
            self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text="GAME OVER",
                fill="white",
                font=("Arial", 30, "bold"),
            )

    def update_status(self, text: str) -> None:
        self.status_var.set(text)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    SnakeGame().run()
