import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

BG = "#f5f7fa"
CARD = "#ffffff"
ACCENT = "#3b82f6"
TEXT = "#1f2937"
MUTED = "#6b7280"
WATER_COLOR = "#3b82f6"
ELEC_COLOR = "#f59e0b"


def parse_presence(text):
    days = set()
    token = text.strip()
    if not token:
        return days
    for chunk in re.split(r"[;,，、\s]+", token):
        if not chunk:
            continue
        parts = re.split(r"[~～至]", chunk)
        if len(parts) == 1:
            s = e = parts[0].strip()
        elif len(parts) == 2:
            s, e = parts[0].strip(), parts[1].strip()
        else:
            raise ValueError(f"“{chunk}” 日期范围格式不正确，应为 开始~结束")
        sd = date.fromisoformat(s)
        ed = date.fromisoformat(e)
        if ed < sd:
            raise ValueError(f"“{chunk}” 结束日期早于开始日期")
        cur = sd
        while cur <= ed:
            days.add(cur)
            cur += timedelta(days=1)
    return days


def count_in(days, start, end):
    return sum(1 for d in days if start <= d <= end)


class DormFeeApp:
    def __init__(self, root):
        self.root = root
        root.title("宿舍水电费分摊计算器")
        root.geometry("820x700")
        root.minsize(780, 660)
        root.configure(bg=BG)

        self.water_var = tk.StringVar()
        self.elec_var = tk.StringVar()
        self.w_start_var = tk.StringVar(value="2026-10-01")
        self.w_end_var = tk.StringVar(value="2026-10-31")
        self.e_start_var = tk.StringVar(value="2026-10-01")
        self.e_end_var = tk.StringVar(value="2026-10-31")

        self.people = []
        default_names = ["室友A", "室友B", "室友C", "室友D"]
      
        for i in range(4):
            self.people.append({
                "name": tk.StringVar(value=default_names[i]),
                "present": tk.StringVar(value="2026-10-01~2026-10-31"),
            })

        self._build_header()
        self._build_inputs()
        self._build_people()
        self._build_actions()
        self._build_result()

    def _card(self, parent):
        frame = tk.Frame(parent, bg=CARD, highlightbackground="#e5e7eb", highlightthickness=1)
        frame.pack(fill="x", padx=16, pady=5)
        return frame

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=16, pady=(10, 2))
        tk.Label(header, text="宿舍水电费分摊计算器", bg=BG, fg=TEXT,
                 font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")
        tk.Label(header, text="水费、电费各自按自己的计费周期与住宿天数独立分摊",
                 bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 10)).pack(anchor="w")

    def _entry(self, parent, label, var, row, col, width=14):
        tk.Label(parent, text=label, bg=CARD, fg=TEXT,
                 font=("Microsoft YaHei UI", 10)).grid(row=row, column=col, sticky="w", padx=8, pady=6)
        ttk.Entry(parent, textvariable=var, width=width).grid(
            row=row, column=col + 1, sticky="w", padx=8, pady=6)

    def _build_inputs(self):
        card = self._card(self.root)
        tk.Label(card, text="费用与计费周期", bg=CARD, fg=ACCENT,
                 font=("Microsoft YaHei UI", 11, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 2))

        tk.Label(card, text="水费", bg=CARD, fg=WATER_COLOR,
                 font=("Microsoft YaHei UI", 10, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(2, 0))
        tk.Label(card, text="电费", bg=CARD, fg=ELEC_COLOR,
                 font=("Microsoft YaHei UI", 10, "bold")).grid(
            row=1, column=2, columnspan=2, sticky="w", padx=8, pady=(2, 0))

        self._entry(card, "金额 (元)", self.water_var, 2, 0)
        self._entry(card, "金额 (元)", self.elec_var, 2, 2)
        self._entry(card, "开始日期", self.w_start_var, 3, 0)
        self._entry(card, "开始日期", self.e_start_var, 3, 2)
        self._entry(card, "结束日期", self.w_end_var, 4, 0)
        self._entry(card, "结束日期", self.e_end_var, 4, 2)

        tk.Label(card, text="(日期格式 YYYY-MM-DD)", bg=CARD, fg=MUTED,
                 font=("Microsoft YaHei UI", 9)).grid(
            row=5, column=0, columnspan=4, sticky="w", padx=8, pady=(2, 8))

    def _build_people(self):
        card = self._card(self.root)
        tk.Label(card, text="各人在宿舍的日期", bg=CARD, fg=ACCENT,
                 font=("Microsoft YaHei UI", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(10, 2))
        tk.Label(card, text="姓名", bg=CARD, fg=MUTED,
                 font=("Microsoft YaHei UI", 9)).grid(row=1, column=0, sticky="w", padx=8)
        tk.Label(card, text="在宿舍日期 (如 2026-10-01~2026-10-15, 2026-10-20~2026-10-31)",
                 bg=CARD, fg=MUTED, font=("Microsoft YaHei UI", 9)).grid(
            row=1, column=1, sticky="w", padx=8)
        for i, p in enumerate(self.people):
            r = i + 2
            ttk.Entry(card, textvariable=p["name"], width=12).grid(
                row=r, column=0, sticky="w", padx=8, pady=4)
            ttk.Entry(card, textvariable=p["present"], width=48).grid(
                row=r, column=1, sticky="w", padx=8, pady=4)
        tk.Label(card, text="多个时间段用逗号分隔；范围用 ~ 连接。程序会分别截取到水/电各自周期内计算。",
                 bg=CARD, fg=MUTED, font=("Microsoft YaHei UI", 9)).grid(
            row=6, column=1, sticky="w", padx=8, pady=(0, 8))

    def _build_actions(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=16, pady=4)
        ttk.Button(bar, text="计算分摊", command=self.calculate).pack(side="left")
        ttk.Button(bar, text="重置", command=self.reset).pack(side="left", padx=8)

    def _build_result(self):
        self.result_card = self._card(self.root)
        tk.Label(self.result_card, text="分摊结果", bg=CARD, fg=ACCENT,
                 font=("Microsoft YaHei UI", 11, "bold")).pack(anchor="w", padx=8, pady=(10, 4))
        self.summary = tk.Label(self.result_card, text="", bg=CARD, fg=TEXT,
                                font=("Microsoft YaHei UI", 10), justify="left", anchor="w")
        self.summary.pack(fill="x", padx=16, pady=(0, 8))

    def _period(self, start_var, end_var, label):
        s = date.fromisoformat(start_var.get().strip())
        e = date.fromisoformat(end_var.get().strip())
        if e < s:
            raise ValueError(f"{label}结束日期不能早于开始日期")
        return s, e

    def calculate(self):
        try:
            water = float(self.water_var.get().strip() or 0)
            elec = float(self.elec_var.get().strip() or 0)
            if water < 0 or elec < 0:
                raise ValueError("费用不能为负数")
        except ValueError as ex:
            messagebox.showerror("输入错误", f"费用填写有误：{ex}")
            return

        try:
            ws, we = self._period(self.w_start_var, self.w_end_var, "水费")
            es, ee = self._period(self.e_start_var, self.e_end_var, "电费")
        except ValueError as ex:
            messagebox.showerror("日期错误", str(ex))
            return

        names = []
        presence = []
        for i, p in enumerate(self.people, 1):
            name = p["name"].get().strip() or f"室友{i}"
            try:
                days = parse_presence(p["present"].get())
            except ValueError as ex:
                messagebox.showerror("日期错误", f"{name}：{ex}")
                return
            names.append(name)
            presence.append(days)

        water_days = [count_in(d, ws, we) for d in presence]
        elec_days = [count_in(d, es, ee) for d in presence]
        total_water = sum(water_days)
        total_elec = sum(elec_days)

        if total_water == 0 and total_elec == 0:
            messagebox.showerror("无法计算", "所有人在水/电计费周期内的住宿天数都是 0")
            return

        water_shares = [water * d / total_water if total_water else 0 for d in water_days]
        elec_shares = [elec * d / total_elec if total_elec else 0 for d in elec_days]
        totals = [water_shares[i] + elec_shares[i] for i in range(len(names))]

        lines = [
            f"水费周期：{ws} ~ {we}（{(we - ws).days + 1} 天），合计 {water:.2f} 元，总人·天 {total_water}",
            f"电费周期：{es} ~ {ee}（{(ee - es).days + 1} 天），合计 {elec:.2f} 元，总人·天 {total_elec}",
            "",
        ]
        for i, name in enumerate(names):
            lines.append(
                f"{name}：水 {water_days[i]} 天 / 电 {elec_days[i]} 天  →  "
                f"水 {water_shares[i]:.2f} + 电 {elec_shares[i]:.2f} = {totals[i]:.2f} 元")
        lines.append("")
        lines.append(f"合计应缴：{sum(totals):.2f} 元")
        self.summary.config(text="\n".join(lines))

        self._draw_chart(names, water_shares, elec_shares, totals)

    def _draw_chart(self, names, water_shares, elec_shares, totals):
        c = self.canvas
        c.delete("all")
        c.update_idletasks()
        w = max(c.winfo_width(), 640)
        h = 200
        pad_l, pad_r, pad_t, pad_b = 60, 20, 40, 50
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        base_y = h - pad_b
        max_val = max(totals) if totals else 0
        if max_val <= 0:
            max_val = 1

        c.create_line(pad_l, base_y, w - pad_r, base_y, fill="#d1d5db")
        c.create_line(pad_l, pad_t, pad_l, base_y, fill="#d1d5db")
        for k in range(5):
            y = pad_t + plot_h * k / 4
            val = max_val * (4 - k) / 4
            c.create_line(pad_l - 4, y, pad_l, y, fill="#d1d5db")
            c.create_text(pad_l - 8, y, text=f"{val:.0f}", anchor="e",
                          fill=MUTED, font=("Microsoft YaHei UI", 8))

        n = len(names)
        slot = plot_w / n
        bw = slot * 0.28
        for i, name in enumerate(names):
            cx = pad_l + slot * (i + 0.5)
            w_h = (water_shares[i] / max_val) * plot_h
            e_h = (elec_shares[i] / max_val) * plot_h
            wx = cx - bw - 2
            ex = cx + 2
            c.create_rectangle(wx, base_y - w_h, wx + bw, base_y,
                               fill=WATER_COLOR, outline="")
            c.create_rectangle(ex, base_y - e_h, ex + bw, base_y,
                               fill=ELEC_COLOR, outline="")
            c.create_text(cx, min(base_y - w_h, base_y - e_h) - 10,
                          text=f"{totals[i]:.2f}元", fill=TEXT,
                          font=("Microsoft YaHei UI", 9, "bold"))
            c.create_text(cx, base_y + 16, text=name, fill=TEXT,
                          font=("Microsoft YaHei UI", 9))
            c.create_text(cx, base_y + 32, text=f"水{water_shares[i]:.2f} 电{elec_shares[i]:.2f}",
                          fill=MUTED, font=("Microsoft YaHei UI", 8))

        lx = pad_l
        c.create_rectangle(lx, 8, lx + 12, 20, fill=WATER_COLOR, outline="")
        c.create_text(lx + 18, 14, text="水费", anchor="w", fill=TEXT,
                      font=("Microsoft YaHei UI", 9))
        c.create_rectangle(lx + 70, 8, lx + 82, 20, fill=ELEC_COLOR, outline="")
        c.create_text(lx + 88, 14, text="电费", anchor="w", fill=TEXT,
                      font=("Microsoft YaHei UI", 9))
        c.create_text(pad_l - 40, pad_t - 18, text="元", anchor="w", fill=MUTED,
                      font=("Microsoft YaHei UI", 9))

    def reset(self):
        self.water_var.set("")
        self.elec_var.set("")
        self.w_start_var.set("2026-10-01")
        self.w_end_var.set("2026-10-31")
        self.e_start_var.set("2026-10-01")
        self.e_end_var.set("2026-10-31")
        defaults = ["室友A", "室友B", "室友C", "室友D"]
        for i, p in enumerate(self.people):
            p["name"].set(defaults[i])
            p["present"].set("2026-10-01~2026-10-31")
        self.summary.config(text="")
        self.canvas.delete("all")


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=6)
    app = DormFeeApp(root)
    root.update_idletasks()
    w = max(root.winfo_reqwidth(), 780)
    h = root.winfo_reqheight()
    root.geometry(f"{w}x{h}")
    root.minsize(w, h)
    root.mainloop()


if __name__ == "__main__":
    main()
