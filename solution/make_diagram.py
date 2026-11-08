# -*- coding: utf-8 -*-
"""Схема процесса «Заявка на закупку», восстановленная по журналу. Запуск: python make_diagram.py"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

GREEN_F, GREEN_E = "#e8f5e9", "#2e7d32"
BLUE_F,  BLUE_E  = "#e3f2fd", "#1565c0"
ORNG_F,  ORNG_E  = "#fff3e0", "#e65100"
RED_F,   RED_E   = "#ffebee", "#b71c1c"
EDGE = "#37474f"
LOOP = "#6a1b9a"

fig, ax = plt.subplots(figsize=(30, 12.8))
ax.set_xlim(0, 30.7); ax.set_ylim(-6.0, 5.6); ax.axis("off")

def box(cx, cy, w, h, title, sub, fc, ec, tfs=12.5, sfs=9.2):
    ax.add_patch(FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                 boxstyle="round,pad=0.09,rounding_size=0.16",
                 linewidth=2.0, facecolor=fc, edgecolor=ec, zorder=3))
    if sub:
        ax.text(cx, cy + 0.17, title, ha="center", va="center", fontsize=tfs,
                fontweight="bold", color="#1a1a1a", zorder=4, linespacing=1.05)
        ax.text(cx, cy - 0.33, sub, ha="center", va="center", fontsize=sfs,
                color="#37474f", zorder=4, linespacing=1.25)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=tfs,
                fontweight="bold", color="#1a1a1a", zorder=4, linespacing=1.05)

def diamond(cx, cy, w, h, label):
    ax.add_patch(Polygon([(cx, cy + h/2), (cx + w/2, cy), (cx, cy - h/2), (cx - w/2, cy)],
                 closed=True, facecolor=ORNG_F, edgecolor=ORNG_E, linewidth=2.0, zorder=3))
    ax.text(cx, cy, label, ha="center", va="center", fontsize=9.5, fontweight="bold", color=ORNG_E, zorder=4)

def arrow(x1, y1, x2, y2, label=None, fs=10, color=EDGE, lw=2.2, dx=0.0, dy=0.14, bold=True):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=24,
                 linewidth=lw, color=color, shrinkA=2, shrinkB=2, zorder=2))
    if label:
        ax.text((x1 + x2)/2 + dx, (y1 + y2)/2 + dy, label, ha="center", va="bottom",
                fontsize=fs, fontweight="bold" if bold else "normal", color=color, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.7))

def seg(points, color=LOOP, lw=2.4):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=2)

# ---------- заголовок ----------
ax.text(15.35, 5.15, "Процесс «Заявка на закупку» — восстановлен по журналу событий",
        ha="center", va="center", fontsize=17, fontweight="bold", color="#1a1a1a")
ax.text(15.35, 4.45, "1 000 экземпляров · 6 508 событий · 12.01.2026–08.07.2026 · 8 вариантов (варианты V1–V8 см. variants.csv)",
        ha="center", va="center", fontsize=10.5, color="#455a64")

# ---------- основная линия (y = 0) ----------
box(1.3, 0, 2.1, 1.2, "Регистрация\nзаявки", "system · process_started\n1 000", GREEN_F, GREEN_E)
box(4.6, 0, 2.35, 1.2, "Первичная\nпроверка", "специалист · task_completed\n1 174 события (1 000 + 174 повт.)", BLUE_F, BLUE_E)
diamond(7.35, 0, 1.4, 1.55, "XOR")
box(10.4, 0, 2.35, 1.2, "Согласование\nруководителем", "руководитель · task_completed\n1 129 событий (955 + 174 повт.)", BLUE_F, BLUE_E)
diamond(13.4, 0, 1.4, 1.55, "XOR")
box(16.4, 0, 2.3, 1.2, "Проверка бюджета", "финансы · task_completed\n911 · всегда accept", BLUE_F, BLUE_E)
diamond(19.1, 0, 1.9, 1.6, "XOR")
box(24.35, 0, 2.35, 1.2, "Исполнение\nзакупки", "закупки · task_completed\n911 · всегда accept", BLUE_F, BLUE_E)
box(28.15, 0, 2.1, 1.2, "Заявка\nвыполнена", "system · process_completed\n911", RED_F, RED_E)

arrow(2.35, 0, 3.42, 0, "1 000")
arrow(5.78, 0, 6.65, 0)
arrow(8.05, 0, 9.22, 0, "accept · 1 129", dx=0.1)
arrow(11.58, 0, 12.70, 0)
arrow(14.10, 0, 15.25, 0, "accept · 911")
arrow(17.55, 0, 18.32, 0)
arrow(19.88, 0, 23.17, 0, "Amount < 150 000 руб. · 702", dy=0.16)
arrow(25.53, 0, 27.10, 0, "fulfilled · 911")

# ---------- ветка дополнительного согласования (сверху) ----------
box(22.15, 2.55, 3.15, 1.25, "Дополнительное\nсогласование", "директор · task_completed\n209 · всегда accept", BLUE_F, BLUE_E)
arrow(19.1, 0.78, 21.15, 1.95, "Amount ≥ 150 000 руб. · 209", color=EDGE, dx=0.35, dy=0.32)
arrow(23.35, 2.10, 24.75, 0.66, "accept · 209", dx=0.75, dy=0.30)

# ---------- контур возврата на доработку ----------
box(10.9, 2.55, 2.5, 1.25, "Доработка заявки", "заявитель · task_completed\n174 события в 156 экз.", BLUE_F, BLUE_E)
arrow(13.15, 0.78, 11.75, 1.92, "return · 174", color=LOOP, dx=0.95, dy=0.42)
seg([(10.9, 3.18), (10.9, 3.95), (4.6, 3.95), (4.6, 0.72)], color=LOOP, lw=2.6)
ax.add_patch(FancyArrowPatch((4.6, 0.9), (4.6, 0.64), arrowstyle="-|>", mutation_scale=26, linewidth=2.6, color=LOOP, zorder=2))
ax.text(7.7, 4.15, "Доработка → Первичная проверка · 174 перехода (цикл, не более 2 итераций в одном экземпляре)",
        ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=LOOP,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.6))

# ---------- окончания (снизу) ----------
box(5.7, -3.35, 2.5, 1.25, "Заявка отклонена", "system · process_completed\n63 (45 + 18)", RED_F, RED_E)
box(13.4, -3.35, 2.5, 1.25, "Заявка отменена", "system · process_completed\n26", RED_F, RED_E)
arrow(7.1, -0.78, 6.0, -2.72, "reject · 45", dx=-1.05, dy=0.0)
arrow(13.15, -0.78, 6.85, -2.72, "reject · 18", dx=-1.6, dy=-0.08)
arrow(13.4, -0.78, 13.4, -2.72, "cancel · 26", dx=1.35, dy=-0.05)

# ---------- легенда ----------
ly = -5.05
chips = [(GREEN_F, GREEN_E, "граница экземпляра (system):\nprocess_started / process_completed"),
         (BLUE_F,  BLUE_E,  "человеческое задание (task_completed);\nв подписи — роль и число событий"),
         (ORNG_F,  ORNG_E,  "XOR-развилка по Result задания\n(«Σ» — по Amount); добавлена на схему,\nв журнале это Result и Amount"),
         (RED_F,   RED_E,   "окончание экземпляра\n(process_completed)")]
lx = 0.35
for fc, ec, txt in chips:
    ax.add_patch(FancyBboxPatch((lx, ly - 0.52), 0.62, 0.62, boxstyle="round,pad=0.02,rounding_size=0.08",
                 facecolor=fc, edgecolor=ec, linewidth=1.6, zorder=3))
    ax.text(lx + 0.78, ly - 0.21, txt, ha="left", va="center", fontsize=8.2, color="#263238", linespacing=1.25)
    lx += 6.05
ax.text(0.35, ly - 1.28,
        "Число на стрелке — число переходов в журнале (сумма по всем экземплярам). Ромбы-шлюзы в student_transitions.csv не включены: там только пары непосредственно следующих активностей.",
        ha="left", va="center", fontsize=8.6, color="#455a64", style="italic")

plt.tight_layout()
plt.savefig("/home/user/-.-2-/solution/process_map.png", dpi=140, bbox_inches="tight", facecolor="white")
print("saved process_map.png")
