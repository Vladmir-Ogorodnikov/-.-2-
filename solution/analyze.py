# -*- coding: utf-8 -*-
"""
Восстановление процесса по журналу событий students (1).csv.
Запуск:  python analyze.py
Требуется: pandas (см. README.md). Результаты: variants.csv, student_transitions.csv + сводка в stdout.
Входной CSV: UTF-8 с BOM, разделитель — запятая. Сортировка внутри экземпляра — по ЧИСЛОВОМУ EventIndex.
"""
import pandas as pd
from collections import Counter
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "students (1).csv")

df = pd.read_csv(SRC, encoding="utf-8-sig")
df = df.sort_values(["ProcessInstanceId", "EventIndex"], kind="stable").reset_index(drop=True)

print(f"Событий: {len(df)}, экземпляров: {df.ProcessInstanceId.nunique()}")
assert df.groupby("ProcessInstanceId").EventIndex.apply(list).apply(lambda x: x == list(range(1, len(x) + 1))).all(), "EventIndex не с 1 или не сплошной"

# ---- трассы ----
traces = df.groupby("ProcessInstanceId").ActivityName.apply(tuple)
N = len(traces)

print("\n== Активности (число событий / экземпляров, где встречается) ==")
inst_counts = df.groupby("ActivityName").ProcessInstanceId.nunique()
for name, cnt in df.ActivityName.value_counts().items():
    print(f"{cnt:5d} событий | {inst_counts[name]:5d} экз. | {name}")

print("\n== Начала и окончания ==")
print("Первая активность:", Counter(t[0] for t in traces))
print("Последняя активность:", Counter(t[-1] for t in traces))
print("Тип первого события:", Counter(df.groupby("ProcessInstanceId").EventType.first()))
print("Тип последнего события:", Counter(df.groupby("ProcessInstanceId").EventType.last()))

# ---- переходы ----
trans = Counter()
for t in traces:
    for a, b in zip(t, t[1:]):
        trans[(a, b)] += 1

print("\n== Переходы (ActivityName -> ActivityName) ==")
for (a, b), c in trans.most_common():
    print(f"{c:5d}  {a} -> {b}")

print("\n== Результаты по активностям ==")
print(df.groupby(["ActivityName", "Result"], dropna=False).size().to_string())

print("\n== Развилка 'Проверка бюджета': сумма заявки ==")
amt = df.groupby("ProcessInstanceId").Amount.first()
add = traces.apply(lambda t: "Дополнительное согласование" in t)
reach_budget = traces.apply(lambda t: "Проверка бюджета" in t)
hi = amt[reach_budget]
print(f"Дошли до проверки бюджета: {reach_budget.sum()} экз.")
print(f"  из них Amount >= 150 000: {(hi >= 150000).sum()}, с доп. согласованием: {add[hi.index][hi >= 150000].sum()}")
print(f"  из них Amount <  150 000: {(hi < 150000).sum()}, с доп. согласованием: {add[hi.index][hi < 150000].sum()}")
print(f"Минимальный Amount с доп. согласованием: {amt[add].min():.2f}; максимальный без него (среди дошедших до бюджета): {hi[~add[hi.index]].max():.2f}")

print("\n== Возвраты на доработку ==")
rew = traces.apply(lambda t: t.count("Доработка заявки"))
print(rew.value_counts().sort_index().to_string())
print(f"Экземпляров с >=1 возвратом: {(rew > 0).sum()} ({(rew > 0).mean() * 100:.1f}%)")

# ---- варианты ----
var_counter = Counter(traces)
print(f"\n== Варианты: {len(var_counter)} ==")
rows = []
for i, (v, c) in enumerate(var_counter.most_common(), 1):
    rows.append((f"V{i}", " > ".join(v), c, c / N))
    print(f"V{i}  {c:5d}  {c / N:.4f}  {' > '.join(v)}")
print("Сумма:", sum(r[2] for r in rows), "экз., доля:", sum(r[3] for r in rows))

variants_csv = os.path.join(HERE, "variants.csv")
with open(variants_csv, "w", encoding="utf-8", newline="") as f:
    f.write("Variant,Route,NumberOfCases,Share\n")
    for name, route, cnt, share in rows:
        f.write(f"{name},{route},{cnt},{share:.3f}\n")

ORDER = ["Регистрация заявки", "Первичная проверка", "Согласование руководителем",
         "Доработка заявки", "Проверка бюджета", "Дополнительное согласование",
         "Исполнение закупки", "Заявка выполнена", "Заявка отклонена", "Заявка отменена"]
transitions_csv = os.path.join(HERE, "student_transitions.csv")
with open(transitions_csv, "w", encoding="utf-8", newline="") as f:
    f.write("SourceActivity,TargetActivity\n")
    for (a, b) in sorted(trans, key=lambda p: (ORDER.index(p[0]), ORDER.index(p[1]))):
        f.write(f"{a},{b}\n")
print(f"\nЗаписано: {variants_csv}, {transitions_csv}")

# ---- циклы / время ----
dur = df.groupby("ProcessInstanceId").Timestamp
mins = pd.to_datetime(df.Timestamp).groupby(df.ProcessInstanceId).agg(["min", "max"])
tot = (mins["max"] - mins["min"]).dt.total_seconds() / 3600
print("\n== Полный цикл, часы ==\n", tot.describe().round(2).to_string())
outcome = traces.apply(lambda t: t[-1])
print("\n== Цикл по исходу (медиана, ч) ==\n", tot.groupby(outcome).median().round(2).to_string())
print("\nУникальных исполнителей:", df.UserId.nunique(), "| Период:", df.Timestamp.min(), "...", df.Timestamp.max())
