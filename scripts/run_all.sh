#!/usr/bin/env bash
# Chạy toàn bộ thí nghiệm từ thư mục gốc repo:  bash scripts/run_all.sh
set -e
mkdir -p out
javac -d out src/*.java
java -cp out MergeSortTest                                   # kiểm thử đúng đắn + ổn định
java -cp out DataGenerator data                              # (tuỳ chọn) xuất dataset ra data/
java -Xmx2g -cp out Benchmark results/benchmark_results.csv  # ~6-10 phút; đóng các chương trình khác khi đo
python3 scripts/analyze.py                                   # bảng thống kê + đồ thị -> results/
