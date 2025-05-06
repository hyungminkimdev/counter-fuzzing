# counter-fuzzing
System and Software Security Course (cs5590) Project

# 🛡️ Counter-Fuzzing: Stealthy and Effective Techniques Against Coverage-Guided Fuzzers

> Course: CS5590 – System and Software Security  
> Project Type: Research Paper Assignment  
> Semester: Spring 2025  
> Status: ✅ Completed

---

## 🧠 Overview

Coverage-guided fuzzers such as AFL(++) are effective tools for discovering vulnerabilities in software. However, many real-world applications may seek to resist fuzzing attacks without breaking functionality. This project explores **counter-fuzzing** techniques: methods that degrade fuzzer performance by introducing **stealthy, timeout-inducing code paths** that are difficult to detect and remove.

We apply and evaluate several counter-fuzzing strategies on the open-source `cJSON` parser using the [FoRTE-FuzzBench](https://github.com/FoRTE-Research/FoRTE-FuzzBench) benchmark and measure their impact using AFL++.

---

## 👥 Team Members

- **Hyungmin Kim** — 🔗 [GitHub](https://github.com/hyungminkim-dev)
- **Chia-Yu Chang** — 🔗 [GitHub](https://github.com/USERNAME1)
- **Hsiang-Jou Chuang** — 🔗 [GitHub](https://github.com/USERNAME2)
- **Sheng-Fang Chien** — 🔗 [GitHub](https://github.com/USERNAME3)

📁 Project Repository: [github.com/hyungminkim-dev/counter-fuzzing-cjson](https://github.com/hyungminkim-dev/counter-fuzzing-cjson)

---

## 🎯 Goal

To design and implement counter-fuzzing code that:
- Substantially reduces fuzzing throughput
- Degrades mutation and coverage exploration efficiency
- Remains undetectable via static analysis or obvious timeout patterns
- Does not crash the target or interfere with normal functionality

---

## 📈 Summary of Results

| Metric              | Baseline (No Counter) | Counter-Fuzzing |
|---------------------|-----------------------|-----------------|
| Edge Coverage       | ~148 edges            | ~119 edges      |
| Corpus Count        | >320                  | ~100            |
| Execs/sec           | ~400                  | ~4–5            |
| Cycles Completed    | ≥ 2                   | 0               |
| Crashes / Hangs     | None                  | None            |
| Fuzzing Depth       | 14+ levels            | Up to 5         |

📊 Full visualizations and comparison charts can be found in the `figures/` folder.

---

## 🧪 How to Reproduce (Step-by-Step)

This section provides a complete guide to reproducing our experiments using **AFL++**, **FoRTE-FuzzBench**, and `cJSON`.

### ☁️ 1. Launch AWS EC2 (Ubuntu 22.04)

- Instance type: `t2.medium` or higher
- Security group: Allow SSH (port 22)
- Download `.pem` key for SSH access

```bash
chmod 400 afl-key.pem
ssh -i "afl-key.pem" ubuntu@<your-ec2-ip>
```

---

### 🔧 2. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential clang libgpg-error-dev libfontconfig1-dev libpcap-dev \
                    git python3 python3-pip curl wget unzip
```

---

### 🧬 3. Install AFL++

```bash
sudo apt install afl++ -y
afl-fuzz --help
```

---

### 📦 4. Clone FoRTE-FuzzBench and Extract cJSON

```bash
git clone https://github.com/FoRTE-Research/FoRTE-FuzzBench.git
cd FoRTE-FuzzBench/cjson
tar -xzf cjson-1.7.7.tar.gz
cd cjson-1.7.7
```

---

### ⚙️ 5. Build cJSON and Fuzz Target

```bash
# Build libraries
gcc -c -fPIC -std=c89 -g -O2 -o cJSON.o cJSON.c
gcc -c -fPIC -std=c89 -g -O2 -o cJSON_Utils.o cJSON_Utils.c
ar rcs libcjson.a cJSON.o
ar rcs libcjson_utils.a cJSON_Utils.o

# Build fuzz target
cd fuzzing
gcc -Wall -pedantic -g -O2 -o cjson cjson.c ../libcjson.a ../libcjson_utils.a
```

---

### 🧪 6. Run Baseline Fuzzing

```bash
echo '{"key": "value"}' > seed_dir/test1
cp /usr/share/afl/dictionaries/json.dict .
mkdir baseline_out

afl-fuzz -i seed_dir -o baseline_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 🔁 7. Insert Counter-Fuzzing Code

Example (input-dependent delay):

```c
static void busy_loop(uint64_t cycles) {
    volatile uint64_t i;
    for (i = 0; i < cycles; i++);
}

static cJSON_bool parse_value(...) {
    if (!input_buffer || !input_buffer->content)
        return false;

    const unsigned char *data = input_buffer->content + input_buffer->offset;
    size_t len = input_buffer->length - input_buffer->offset;
    if (len > 0) {
        uint32_t hash = simple_hash(data, len > 16 ? 16 : len);
        if ((hash & 0xFF) == 0xFF) {
            busy_loop(50000000);
        }
    }
    ...
}
```

---

### 🔨 8. Rebuild with AFL Instrumentation

```bash
make clean || true
make distclean || true

CC=afl-clang-fast CXX=afl-clang-fast++ \
CFLAGS="-g -O2 -std=c99 -no-pie" \
CXXFLAGS="-g -O2 -std=c++11 -no-pie" \
make all
```

---

### 🧪 9. Run Counter-Fuzzing

```bash
mkdir counter_out
AFL_COUNTER_FUZZ=1 afl-fuzz -i seed_dir -o counter_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 📊 10. Visualize and Compare

```bash
afl-plot baseline_out        # → baseline_out/index.html
afl-plot counter_out         # → counter_out/index.html
```

---

## 🖼️ Example Figures

| Code Coverage Over Time | Execution Speed |
|--------------------------|------------------|
| ![Code Coverage](figures/Code_Coverage_Over_Time.png) | ![Exec Speed](figures/Execs_Over_Time_Smoothed.png) |

---

## 🗂️ Project Structure

```
counter-fuzzing-cjson/
├── fuzzing/
│   ├── seed_dir/
│   ├── json.dict
│   ├── baseline_out/
│   ├── counter_out/
│   └── cjson.c
├── figures/
│   ├── Code_Coverage_Over_Time.png
│   ├── Execs_Over_Time_Smoothed.png
│   ├── html_results_baseline.png
│   └── html_results_bl.png
├── analysis/
│   └── plot_data_analysis.ipynb
├── report/
│   └── CS5590_Counter_Fuzzing_Research_Project_Paper.pdf
```

---

## ✅ Final Verdict

> The counter-fuzzing implementation was successful.
> 
> It introduced significant computational overhead or complexity that drastically reduced fuzzing efficiency, **slowed execution by 100x**, and severely limited the ability to discover new paths or mutate inputs effectively — all without causing hangs or crashes.

---

## 📎 Related Links

- 🔗 [FoRTE-FuzzBench Benchmark](https://github.com/FoRTE-Research/FoRTE-FuzzBench)
- 📘 [CS5590 Course Page (Virginia Tech)](https://cs.vt.edu/)
- 📄 [Research Paper (PDF)](report/CS5590_Counter_Fuzzing_Research_Project_Paper.pdf)
