import pandas as pd
import pm4py
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

SRC = "/home/user/-.-2-/students (1).csv"
df = pd.read_csv(SRC, encoding="utf-8-sig", parse_dates=["Timestamp"])
df = df.sort_values(["ProcessInstanceId","EventIndex"]).reset_index(drop=True)
elog = pd.DataFrame({
    "case:concept:name": df.ProcessInstanceId,
    "concept:name": df.ActivityName,
    "time:timestamp": df.Timestamp,
})
elog = dataframe_utils.convert_timestamp_columns_in_df(elog, "%Y-%m-%dT%H:%M:%S%z", "time:timestamp")
log = log_converter.apply(elog)

print("=== DFG (directly_follows_graph) ===")
dfg_all, sa_all, ea_all = pm4py.discover_directly_follows_graph(log)
print("start:", sa_all, "end:", ea_all)
for (a,b),c in sorted(dfg_all.items(), key=lambda kv:-kv[1]):
    print(f"{c:5d}  {a} -> {b}")

print("\n=== Inductive Miner (Petri net) ===")
net, im, fm = pm4py.discover_petri_net_inductive(log)
print("transitions:", sorted(t.label for t in net.transitions if t.label))
fitness = pm4py.fitness_alignments(log, net, im, fm)
precision = pm4py.precision_alignments(log, net, im, fm)
print("fitness:", fitness)
print("precision:", precision)

print("\n=== Heuristics Miner ===")
net2, im2, fm2 = pm4py.discover_petri_net_heuristics(log)
print("transitions:", sorted(t.label for t in net2.transitions if t.label))
print("fitness:", pm4py.fitness_token_based_replay(log, net2, im2, fm2))
print("precision:", pm4py.precision_token_based_replay(log, net2, im2, fm2))

print("\n=== If we erase the amount distinction (directly-follows view), what extra behavior is implied? ===")
from collections import Counter
traces = df.groupby("ProcessInstanceId").ActivityName.apply(list)
print("variants (DFG can't distinguish amount-based branch condition — it sees the same pair choice always allowed)")
print("n variants:", traces.nunique())
