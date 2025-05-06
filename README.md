# 🛡️ Counter-Fuzzing: Stealthy and Effective Techniques Against Coverage-Guided Fuzzers

This repository contains the code, evaluation results, and documentation for our research project on **counter-fuzzing**—a defensive software strategy designed to resist coverage-guided fuzzers like AFL++.

📄 **[Research Paper (PDF)](./CS5590_Counter_Fuzzing_Research_Project_Paper.pdf)**  
📊 **[Fuzzing Summary Table Screenshot](./Screenshot_2025-04-22.png)**  
🖼️ **Figures** (see `/figures` folder for all evaluation graphs)

---

## 🔍 Overview

Coverage-guided fuzzing is one of the most effective methods for vulnerability discovery. However, its widespread usage also exposes programs to automated reverse engineering and black-box fuzzing attacks.

This project presents **three counter-fuzzing strategies** that intentionally disrupt fuzzers without breaking normal execution:

1. **Busy Loop (BL)** – Adds constant delay through infinite loop constructs.
2. **Input-Dependent Delay (IDD)** – Slows execution only when specific input hash patterns are matched.
3. **Dynamic Self-Modification (DSM)** – Redirects control flow at runtime to stealthy slowdown stubs.

All techniques were integrated into the [`cJSON`](https://github.com/DaveGamble/cJSON) parser and evaluated using [AFL++](https://github.com/AFLplusplus/AFLplusplus) on [FoRTE-FuzzBench](https://github.com/FoRTE-Research/FoRTE-FuzzBench).

---

## 🛠️ Implementation

Each strategy was implemented and tested on top of the `cjson-1.7.7` benchmark:

- `baseline/` – unmodified cJSON
- `bl_busy_loop/` – busy loop inserted in `parse_value()`
- `idd_input_delay/` – hash-triggered delay logic
- `dsm_dynamic_self_mod/` – function pointer rewrite in `ParseWithOpts()`

Each directory contains instrumented code and AFL run scripts.

---

## 📈 Results Summary

| Strategy              | Max Coverage | Avg Exec/sec | Crashes | Comments                    |
|----------------------|--------------|---------------|---------|-----------------------------|
| Baseline             | 16.57        | 647           | 0       | High throughput & coverage  |
| Counter-Fuzzing (BL) | 13.30        | 2.66          | 0       | Effective but detectable    |
| Counter-Fuzzing (IDD)| 17.07        | 533           | 0       | Stealthy with good coverage |
| Counter-Fuzzing (DSM)| 0.03         | 11            | 0       | Blocks fuzzing completely   |

📌 Refer to figures in `/figures`:
- `Code_Coverage_Over_Time.png`
- `Execs_Over_Time_Smoothed.png`
- `html_results_*.png` (internal AFL++ stats)

---

## 👥 Team Members

This project was developed as part of the CS5590 System & Software Security course at Virginia Tech.

- **Hyungmin Kim** – [GitHub](https://github.com/hyungminkim-dev)
- **Chia-Yu Chang** – [GitHub](https://github.com/chickk)
- **Hsiang-Jou Chuang** – [GitHub](https://github.com/kimiichuang)
- **Sheng-Fang Chien** – [GitHub](https://github.com/Serenechien0172)

---

## 🧪 Experimental Setup

- **Fuzzer**: AFL++ 4.09c in QEMU mode
- **Target Program**: `cjson-1.7.7`
- **Run Time**: 1 hour per strategy
- **Platform**: Ubuntu 22.04 (AWS EC2)

---

## 🪜 How to Reproduce (Step-by-Step)

This section provides a complete guide to reproducing our experiments using **AFL++**, **FoRTE-FuzzBench**, and `cJSON`. We evaluated four experimental setups:

- 🟢 `baseline` — No counter-fuzzing
- 🔵 `bl` — Static busy loop inserted
- 🟠 `idd` — Input-dependent delay based on input hash
- 🟣 `dsm` — Dynamic self-modifying control redirection (optional enhancement)

---

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

### ⚙️ 5. Build cJSON and Fuzz Target (for all versions)

```bash
# Compile libraries
gcc -c -fPIC -std=c89 -g -O2 -o cJSON.o cJSON.c
gcc -c -fPIC -std=c89 -g -O2 -o cJSON_Utils.o cJSON_Utils.c
ar rcs libcjson.a cJSON.o
ar rcs libcjson_utils.a cJSON_Utils.o

# Build fuzzing target
cd fuzzing
gcc -Wall -pedantic -g -O2 -o cjson cjson.c ../libcjson.a ../libcjson_utils.a
```

---

## 🔬 Variant-Specific Setups

---

### 🟢 Baseline (No counter-fuzzing)

```bash
mkdir -p seed_dir baseline_out
echo '{"key": "value"}' > seed_dir/test1
cp /usr/share/afl/dictionaries/json.dict .

afl-fuzz -i seed_dir -o baseline_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 🔵 BL (Busy Loop)

**Edit `parse_value()` in `cJSON.c`**:

```c
static void busy_loop(uint64_t cycles) {
    volatile uint64_t i;
    for (i = 0; i < cycles; i++);
}

static cJSON_bool parse_value(...) {
    ...
    busy_loop(10000000); // Inserted delay
    ...
}
```

**Rebuild and run**:

```bash
make clean && make distclean
CC=afl-clang-fast CXX=afl-clang-fast++ \
CFLAGS="-g -O2 -no-pie -std=c99" \
CXXFLAGS="-g -O2 -no-pie" \
make all

mkdir bl_out
afl-fuzz -i seed_dir -o bl_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 🟠 IDD (Input-Dependent Delay)

**Edit `parse_value()` in `cJSON.c`**:

```c
static uint32_t simple_hash(const unsigned char *data, size_t len) {
    uint32_t hash = 0;
    for (size_t i = 0; i < len; i++) {
        hash ^= data[i];
        hash = (hash << 5) | (hash >> (32 - 5));
    }
    return hash;
}

static void busy_loop(uint64_t cycles) {
    volatile uint64_t i;
    for (i = 0; i < cycles; i++);
}

static cJSON_bool parse_value(...) {
    ...
    const unsigned char *data = input_buffer->content + input_buffer->offset;
    size_t len = input_buffer->length - input_buffer->offset;
    if (len > 0) {
        uint32_t hash = simple_hash(data, len > 16 ? 16 : len);
        if ((hash & 0xFF) == 0xFF) {
            busy_loop(50000000);
        } else if (hash > 0xF0000000 && hash < 0xF1000000) {
            busy_loop(20000000);
        }
    }
    ...
}
```

**Rebuild and run**:

```bash
make clean && make distclean
CC=afl-clang-fast CXX=afl-clang-fast++ \
CFLAGS="-g -O2 -no-pie -std=c99" \
CXXFLAGS="-g -O2 -no-pie" \
make all

mkdir idd_out
afl-fuzz -i seed_dir -o idd_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 🟣 DSM (Dynamic Control Flow Redirection)

**Modify `cjson.c` or `afl.c` to insert logic that alters execution path dynamically.**

> E.g., use `getenv()` to jump to costly paths only if environment variable is set.

```c
if (getenv("DSM_ENABLE")) {
    busy_loop(40000000);
}
```

**Rebuild and run**:

```bash
make clean && make distclean
CC=afl-clang-fast CXX=afl-clang-fast++ \
CFLAGS="-g -O2 -no-pie -std=c99" \
CXXFLAGS="-g -O2 -no-pie" \
make all

mkdir dsm_out
DSM_ENABLE=1 afl-fuzz -i seed_dir -o dsm_out -x json.dict -t 2000+ -- ./cjson @@
```

---

### 📊 Visualization and Comparison

```bash
afl-plot baseline_out        # → baseline_out/index.html
afl-plot bl_out              # → bl_out/index.html
afl-plot idd_out             # → idd_out/index.html
afl-plot dsm_out             # → dsm_out/index.html
```

Open each folder’s `index.html` file to visually compare throughput, edge coverage, and crash discovery across variants.


---

## 🛡️ Use Cases

Counter-fuzzing is particularly useful for:

- Binary obfuscation in proprietary software
- Embedded firmware with limited compute budgets
- Protecting against greybox fuzzing or reverse engineering

---

## 📌 Future Work

- Extend testing to grammar-based or concolic fuzzers
- Design adaptive (runtime-reactive) defenses
- Explore integration with software diversity & randomization
- Benchmark at scale on production codebases

---

## License

This repository is intended for academic, educational, and ethical research purposes only. Do not use the techniques described here against unauthorized systems.
