import pandas as pd
import matplotlib.pyplot as plt

# 데이터 로드 (경로 수정 가능)
baseline = pd.read_csv("/Users/henry/Desktop/FoRTE-FuzzBench/cjson/cjson-1.7.7/fuzzing/baseline_out_1h/default/plot_data")
counter = pd.read_csv("/Users/henry/Desktop/FoRTE-FuzzBench/cjson/cjson-1.7.7/fuzzing/counter_out_1h/default/plot_data")

# 열 이름 정리 (앞뒤 공백 제거)
baseline.columns = [col.strip().lstrip("#") for col in baseline.columns]
baseline.columns = baseline.columns.str.strip()
counter.columns = [col.strip().lstrip("#") for col in counter.columns]
counter.columns = counter.columns.str.strip()

# map_size를 퍼센트 문자열에서 float로 변환
for df in [baseline, counter]:
    df['map_size'] = df['map_size'].str.replace('%', '').astype(float)

# 시간 (초) 단위로 바꾸기
baseline['relative_time'] = baseline['relative_time'].astype(int)
counter['relative_time'] = counter['relative_time'].astype(int)

# 결과 요약 함수
def summarize(data, label):
    summary = {
        "Label": label,
        "Max Coverage (map_size)": data["map_size"].max(),
        "Mean Coverage (map_size)": data["map_size"].mean(),
        "Total Executions": data["total_execs"].iloc[-1],
        "Crashes Found": data["saved_crashes"].max(),
        "Hangs Found": data["saved_hangs"].max(),
        "Average Execs/sec": data["execs_per_sec"].mean(),
    }
    return summary

# 요약 정보 출력
baseline_summary = summarize(baseline, "Baseline")
counter_summary = summarize(counter, "Counter-Fuzzing")

summary_df = pd.DataFrame([baseline_summary, counter_summary])
print("🔍 Fuzzing Summary Comparison:")
print(summary_df)

# 그래프: Coverage over time
plt.figure(figsize=(10, 6))
plt.plot(baseline["relative_time"], baseline["map_size"], label="Baseline", linestyle="--")
plt.plot(counter["relative_time"], counter["map_size"], label="Counter-Fuzzing", linestyle="-")
plt.xlabel("Time (seconds)")
plt.ylabel("Code Coverage (map_size)")
plt.title("📈 Code Coverage Over Time")
plt.legend()
plt.grid(True)
plt.savefig("coverage_over_time_comparison.png")

# 그래프: Execs/sec over time
plt.figure(figsize=(10, 6))
plt.plot(baseline["relative_time"], baseline["execs_per_sec"], label="Baseline", linestyle="--")
plt.plot(counter["relative_time"], counter["execs_per_sec"], label="Counter-Fuzzing", linestyle="-")
plt.xlabel("Time (seconds)")
plt.ylabel("Executions per Second")
plt.title("⚙️ Execs/sec Over Time")
plt.legend()
plt.grid(True)
plt.savefig("execs_per_sec_comparison.png")

plt.show()
