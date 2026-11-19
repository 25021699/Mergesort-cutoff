# Báo cáo thí nghiệm: tìm giá trị CUTOFF tốt nhất cho Mergesort



## 1. Mục tiêu và câu hỏi thí nghiệm
## 1. Mục tiêu và câu hỏi thí nghiệm

Mergesort có chi phí gọi đệ quy và sao chép mảng phụ đáng kể khi kích thước mảng con trở nên nhỏ. Một cải tiến kinh điển trong giáo trình là đặt ngưỡng **CUTOFF** để chuyển sang **Insertion Sort** khi mảng con đủ nhỏ. Các phiên bản giáo trình thường gợi ý `CUTOFF = 7` (cũ) hoặc `CUTOFF = 10` (mới), nhưng giá trị tối ưu thực tế phụ thuộc vào phần cứng, bộ nhớ đệm (CPU cache), trình biên dịch JIT và cách cài đặt.

Thí nghiệm này nhằm trả lời 3 câu hỏi trên chính cấu hình máy đo và bản cài đặt Mergesort từ bài giảng:
1. Giá trị (hoặc khoảng giá trị) `CUTOFF` nào cho thời gian chạy tốt nhất trên dữ liệu ngẫu nhiên (`random`)?
2. Hai giá trị giáo trình (`7` và `10`) có khác biệt có ý nghĩa thống kê không, và so với điểm tối ưu đo được thì chênh lệch bao nhiêu?
3. Điểm `CUTOFF` tối ưu thay đổi như thế nào khi dữ liệu đầu vào có cấu trúc (`sorted`, `reverse`, `nearly`, `dups`)?
## 2. Mô tả thí nghiệm

### 2.1 Môi trường
| |                                    |
|---|------------------------------------|
| CPU | Intel(R) Core(TM) Ultra 5 225H     |
| Số nhân khả dụng | 14                                 |
| Hệ điều hành | Windows 11 10.0 amd64      |
| Java | OpenJDK 64-Bit Server VM 26 |
| Heap tối đa | 8064 MB                            |

### 2.2 Cài đặt (`src/MergeSort.java`)
- Cài đặt **từ bài giảng**: `merge(a, aux, lo, mid, hi)` , `sort(a, aux, lo, hi)` top-down
  , điều kiện cutoff `if (hi <= lo + CUTOFF - 1) { insertionSort(a, lo, hi); return; }` ,
  insertion sort dùng `less`/`exch` . Không dùng thêm cải tiến nào khác (không có "stop if already sorted",
  không "eliminate the copy") để chỉ đo ảnh hưởng của CUTOFF.
- CUTOFF là tham số thay vì hằng số. `cutoff = 1` tương đương mergesort thuần (không insertion sort) và là mốc so sánh.
- Kiểu dữ liệu: `Integer[]` qua `Comparable[]` (đúng giao diện trong bài giảng).
- Kiểm thử (`MergeSortTest`): 639 phép kiểm tra – kết quả trùng `Arrays.sort` với 9 giá trị cutoff × 5 loại dữ liệu × 14 kích thước (0…5000),
  và kiểm tra tính **ổn định** (đúng với mọi cutoff vì cả merge lẫn insertion sort đều ổn định).

### 2.3 Dữ liệu (`src/DataGenerator.java`, thư mục `data/`)
Seed cố định nên tái lập được. Năm loại dữ liệu, ba kích thước N = 10⁴, 10⁵, 10⁶:
`random` (số nguyên ngẫu nhiên), `sorted`, `reverse` (giảm dần), `nearly` (đã sắp rồi hoán đổi ngẫu nhiên N/100 cặp),
`dups` (chỉ 100 giá trị khác nhau). Dữ liệu `random` là kịch bản chính (trường hợp trung bình điển hình);
các loại còn lại để xem cutoff có "ổn định" khi đầu vào có cấu trúc.

### 2.4 Quy trình đo (`src/Benchmark.java`)
- 19 giá trị CUTOFF: 1–10, 12, 14, 16, 20, 24, 32, 48, 64, 100.
- Số lần lặp: 101 (N=10⁴), 41 (N=10⁵), 15 (N=10⁶); tổng 14 915 phép đo (`results/benchmark_results.csv`).
- **Warm-up JIT** trước khi đo (toàn cục + cục bộ cho từng bộ dữ liệu); thời gian sao chép mảng không tính.
- **Xen kẽ:** trong mỗi lần lặp, chạy lần lượt cả 19 cutoff (thứ tự xoay vòng) trên bản sao mới của cùng mảng. Nhờ vậy mọi cutoff
  chịu cùng nhiễu của máy (GC, tải nền, tần số CPU), và có thể so sánh **theo cặp** giữa các cutoff.
- Đo bằng `System.nanoTime()`, đơn vị ms.

### 2.5 Thống kê (`scripts/analyze.py`)
Với mỗi (loại dữ liệu, N, cutoff): mean, median, độ lệch chuẩn, khoảng tin cậy 95% (phân phối t). Cutoff "tốt nhất" là cutoff có
**mean nhỏ nhất**. Vì các giá trị gần đáy rất sát nhau, ta dùng **paired t-test** (cặp theo lần lặp) giữa từng cutoff và cutoff tốt nhất;
cutoff nào có p ≥ 0.05 được coi là *không khác biệt có ý nghĩa thống kê* với cutoff tốt nhất.
## 3. Kết quả

### 3.1 Cutoff tốt nhất theo từng nhóm
| dataset   |       n |   best_cutoff |   best (ms) |   cutoff=1 (ms) |   speedup_vs_pure |   cutoff=7 (ms) |   cutoff=10 (ms) |   p(7 vs 10) | cutoff không khác best (p>=0.05)   |
|:----------|--------:|--------------:|------------:|----------------:|------------------:|----------------:|-----------------:|-------------:|:-----------------------------------|
| random    |   10000 |            14 |       1.179 |           1.334 |             1.132 |           1.186 |            1.195 |        0.506 | 5 6 7 8 9 10 12 14 16 20 24 32     |
| random    |  100000 |            20 |      15.729 |          17.250 |             1.097 |          15.935 |           15.941 |        0.959 | 7 8 10 12 14 16 20 24 32           |
| random    | 1000000 |            16 |     215.663 |         236.383 |             1.096 |         220.665 |          218.278 |        0.088 | 8 12 16 20 24                      |
| sorted    |   10000 |           100 |       0.309 |           0.618 |             2.001 |           0.471 |            0.445 |        0.004 | 100                                |
| sorted    |  100000 |           100 |       4.291 |           7.447 |             1.735 |           6.106 |            5.970 |        0.066 | 100                                |
| sorted    | 1000000 |            64 |      60.614 |          89.202 |             1.472 |          77.433 |           73.562 |        0.052 | 64 100                             |
| reverse   |   10000 |             8 |       0.529 |           0.608 |             1.150 |           0.532 |            0.570 |        0.000 | 4 5 6 7 8                          |
| reverse   |  100000 |             4 |       6.617 |           7.362 |             1.113 |           6.853 |            6.797 |        0.412 | 3 4 5                              |
| reverse   | 1000000 |             7 |      82.196 |          91.314 |             1.111 |          82.196 |           83.652 |        0.022 | 4 5 7 14                           |
| nearly    |   10000 |           100 |       0.353 |           0.634 |             1.799 |           0.490 |            0.452 |        0.000 | 100                                |
| nearly    |  100000 |           100 |       4.992 |           7.895 |             1.581 |           6.543 |            6.349 |        0.006 | 100                                |
| nearly    | 1000000 |            64 |      70.469 |          98.877 |             1.403 |          86.877 |           83.119 |        0.001 | 64 100                             |
| dups      |   10000 |            24 |       0.946 |           1.120 |             1.184 |           0.981 |            0.968 |        0.359 | 10 12 14 16 20 24 32               |
| dups      |  100000 |            20 |      11.093 |          12.700 |             1.145 |          11.310 |           11.367 |        0.605 | 14 16 20 24                        |
| dups      | 1000000 |            20 |     125.569 |         142.231 |             1.133 |         130.743 |          127.718 |        0.003 | 16 20 24                           |

### 3.2 Dữ liệu random (kịch bản chính)

### N = 10,000

|   cutoff |    reps |   mean |   median |   std |   ci95 |   rel_to_c1 |
|---------:|--------:|-------:|---------:|------:|-------:|------------:|
|    1.000 | 101.000 |  1.334 |    1.317 | 0.050 |  0.010 |       1.000 |
|    2.000 | 101.000 |  1.285 |    1.234 | 0.179 |  0.035 |       0.963 |
|    3.000 | 101.000 |  1.260 |    1.220 | 0.154 |  0.030 |       0.945 |
|    4.000 | 101.000 |  1.242 |    1.209 | 0.109 |  0.022 |       0.931 |
|    5.000 | 101.000 |  1.192 |    1.175 | 0.042 |  0.008 |       0.893 |
|    6.000 | 101.000 |  1.194 |    1.176 | 0.056 |  0.011 |       0.895 |
|    7.000 | 101.000 |  1.186 |    1.173 | 0.046 |  0.009 |       0.889 |
|    8.000 | 101.000 |  1.216 |    1.167 | 0.200 |  0.039 |       0.911 |
|    9.000 | 101.000 |  1.203 |    1.174 | 0.092 |  0.018 |       0.902 |
|   10.000 | 101.000 |  1.195 |    1.162 | 0.133 |  0.026 |       0.896 |
|   12.000 | 101.000 |  1.211 |    1.158 | 0.215 |  0.042 |       0.908 |
|   14.000 | 101.000 |  1.179 |    1.153 | 0.118 |  0.023 |       0.884 |
|   16.000 | 101.000 |  1.208 |    1.163 | 0.204 |  0.040 |       0.905 |
|   20.000 | 101.000 |  1.207 |    1.164 | 0.137 |  0.027 |       0.905 |
|   24.000 | 101.000 |  1.213 |    1.161 | 0.188 |  0.037 |       0.909 |
|   32.000 | 101.000 |  1.190 |    1.160 | 0.101 |  0.020 |       0.892 |
|   48.000 | 101.000 |  1.274 |    1.236 | 0.114 |  0.023 |       0.955 |
|   64.000 | 101.000 |  1.277 |    1.245 | 0.158 |  0.031 |       0.957 |
|  100.000 | 101.000 |  1.502 |    1.478 | 0.081 |  0.016 |       1.126 |

### N = 100,000

|   cutoff |   reps |   mean |   median |   std |   ci95 |   rel_to_c1 |
|---------:|-------:|-------:|---------:|------:|-------:|------------:|
|    1.000 | 41.000 | 17.250 |   16.962 | 0.667 |  0.211 |       1.000 |
|    2.000 | 41.000 | 16.800 |   16.503 | 0.721 |  0.228 |       0.974 |
|    3.000 | 41.000 | 16.289 |   16.008 | 0.718 |  0.227 |       0.944 |
|    4.000 | 41.000 | 16.178 |   16.009 | 0.574 |  0.181 |       0.938 |
|    5.000 | 41.000 | 16.219 |   15.954 | 0.605 |  0.191 |       0.940 |
|    6.000 | 41.000 | 16.163 |   15.992 | 0.663 |  0.209 |       0.937 |
|    7.000 | 41.000 | 15.935 |   15.613 | 0.657 |  0.207 |       0.924 |
|    8.000 | 41.000 | 15.907 |   15.802 | 0.545 |  0.172 |       0.922 |
|    9.000 | 41.000 | 16.018 |   15.976 | 0.621 |  0.196 |       0.929 |
|   10.000 | 41.000 | 15.941 |   15.722 | 0.586 |  0.185 |       0.924 |
|   12.000 | 41.000 | 15.811 |   15.473 | 0.676 |  0.213 |       0.917 |
|   14.000 | 41.000 | 15.838 |   15.692 | 0.710 |  0.224 |       0.918 |
|   16.000 | 41.000 | 15.750 |   15.469 | 0.683 |  0.216 |       0.913 |
|   20.000 | 41.000 | 15.729 |   15.518 | 0.525 |  0.166 |       0.912 |
|   24.000 | 41.000 | 15.803 |   15.622 | 0.560 |  0.177 |       0.916 |
|   32.000 | 41.000 | 15.900 |   15.598 | 0.647 |  0.204 |       0.922 |
|   48.000 | 41.000 | 16.150 |   15.908 | 0.613 |  0.193 |       0.936 |
|   64.000 | 41.000 | 17.037 |   16.833 | 0.537 |  0.170 |       0.988 |
|  100.000 | 41.000 | 20.487 |   20.152 | 0.931 |  0.294 |       1.188 |

### N = 1,000,000

|   cutoff |   reps |    mean |   median |   std |   ci95 |   rel_to_c1 |
|---------:|-------:|--------:|---------:|------:|-------:|------------:|
|    1.000 | 15.000 | 236.383 |  234.337 | 5.815 |  3.220 |       1.000 |
|    2.000 | 15.000 | 229.144 |  228.556 | 5.512 |  3.052 |       0.969 |
|    3.000 | 15.000 | 228.023 |  226.903 | 4.332 |  2.399 |       0.965 |
|    4.000 | 15.000 | 220.914 |  219.797 | 4.050 |  2.243 |       0.935 |
|    5.000 | 15.000 | 223.139 |  222.824 | 3.377 |  1.870 |       0.944 |
|    6.000 | 15.000 | 224.418 |  223.778 | 3.701 |  2.050 |       0.949 |
|    7.000 | 15.000 | 220.665 |  219.985 | 3.676 |  2.036 |       0.934 |
|    8.000 | 15.000 | 217.401 |  217.003 | 3.545 |  1.963 |       0.920 |
|    9.000 | 15.000 | 219.385 |  219.589 | 2.463 |  1.364 |       0.928 |
|   10.000 | 15.000 | 218.278 |  218.722 | 2.854 |  1.581 |       0.923 |
|   12.000 | 15.000 | 218.194 |  216.675 | 4.320 |  2.392 |       0.923 |
|   14.000 | 15.000 | 219.462 |  218.106 | 3.745 |  2.074 |       0.928 |
|   16.000 | 15.000 | 215.663 |  215.124 | 1.856 |  1.028 |       0.912 |
|   20.000 | 15.000 | 215.963 |  216.019 | 1.848 |  1.023 |       0.914 |
|   24.000 | 15.000 | 217.148 |  216.285 | 5.835 |  3.231 |       0.919 |
|   32.000 | 15.000 | 224.709 |  222.370 | 5.527 |  3.061 |       0.951 |
|   48.000 | 15.000 | 221.816 |  222.802 | 4.045 |  2.240 |       0.938 |
|   64.000 | 15.000 | 239.001 |  239.413 | 3.456 |  1.914 |       1.011 |
|  100.000 | 15.000 | 236.740 |  236.472 | 2.490 |  1.379 |       1.002 |


### 3.3 Đồ thị

![Thời gian theo CUTOFF](../results/charts/time_vs_cutoff.png)

![Tỉ lệ so với cutoff=1](../results/charts/relative_to_pure.png)

![random, N lớn nhất](../results/charts/random_largest_zoom.png)

![Tổng hợp](../results/charts/aggregate_relative.png)

![Heatmap random](../results/charts/heatmap_random.png)

## Độ chậm tương đối trung bình so với cutoff tốt nhất (1.000 = tốt nhất)

|   cutoff |   mọi nhóm |   N>=1e5 |   random N>=1e5 |
|---------:|-----------:|---------:|----------------:|
|    1.000 |      1.343 |    1.289 |           1.096 |
|    2.000 |      1.263 |    1.228 |           1.065 |
|    3.000 |      1.218 |    1.186 |           1.046 |
|    4.000 |      1.196 |    1.157 |           1.026 |
|    5.000 |      1.173 |    1.156 |           1.033 |
|    6.000 |      1.162 |    1.144 |           1.034 |
|    7.000 |      1.156 |    1.138 |           1.018 |
|    8.000 |      1.152 |    1.120 |           1.010 |
|    9.000 |      1.155 |    1.126 |           1.018 |
|   10.000 |      1.134 |    1.117 |           1.013 |
|   12.000 |      1.128 |    1.111 |           1.008 |
|   14.000 |      1.134 |    1.112 |           1.012 |
|   16.000 |      1.131 |    1.103 |           1.001 |
|   20.000 |      1.125 |    1.100 |           1.001 |
|   24.000 |      1.134 |    1.114 |           1.006 |
|   32.000 |      1.149 |    1.142 |           1.026 |
|   48.000 |      1.197 |    1.153 |           1.028 |
|   64.000 |      1.281 |    1.282 |           1.096 |
|  100.000 |      1.498 |    1.447 |           1.200 |


## 4. Phân tích

## 4. Phân tích

1. **Cutoff mang lại cải thiện rõ rệt so với mergesort thuần (`cutoff = 1`).**
   Trên dữ liệu `random`, việc áp dụng cutoff giúp giảm thời gian chạy trung bình khoảng **11,6%** ở N = 10⁴ (từ 1,334 ms xuống 1,179 ms tại `cutoff = 14`, tăng tốc 1,132×), **8,8%** ở N = 10⁵ (từ 17,250 ms xuống 15,729 ms tại `cutoff = 20`, tăng tốc 1,097×) và **8,8%** ở N = 10⁶ (từ 236,383 ms xuống 215,663 ms tại `cutoff = 16`, tăng tốc 1,096×). Ở tầng lá của cây đệ quy, mergesort phải gọi hàm đệ quy, sao chép sang mảng phụ `aux` và trộn cho các mảng chỉ vài phần tử; chuyển sang insertion sort giúp loại bỏ phần lớn chi phí phụ (overhead) này và tận dụng tốt bộ nhớ đệm L1 của CPU.


2. **Đường cong có vùng đáy phẳng và rộng, tập trung quanh `12–24`.**
   Khi cutoff quá lớn (`64`, `100`), độ phức tạp bậc hai của insertion sort bắt đầu lấn át lợi ích giảm đệ quy nên thời gian tăng vọt trở lại — ở N = 10⁶, `cutoff = 64` (239,001 ms) và `cutoff = 100` (236,740 ms) thậm chí chậm hơn cả mergesort thuần (236,383 ms). Ngược lại, trong khoảng `8–24` (đặc biệt là **`12–24`**), hiệu năng gần như đi ngang: vùng giao của nhóm "không khác best (p >= 0,05)" trên cả ba kích thước N của `random` là **{8, 12, 16, 20, 24}**. Điều này cho thấy trên thực tế không tồn tại một con số tối ưu duy nhất mà là một *khoảng tối ưu*.


3. **So sánh hai giá trị giáo trình `7` và `10` với kết quả đo được.**
    - **Giữa 7 và 10:** Kiểm định paired t-test trên dữ liệu `random` cho `p = 0,506` (N = 10⁴), `p = 0,959` (N = 10⁵) và `p = 0,088` (N = 10⁶) — đều lớn hơn 0,05. Như vậy **7 và 10 không có sự khác biệt có ý nghĩa thống kê** trên dữ liệu ngẫu nhiên.
    - **So với điểm tối ưu trên máy này:** Ở N = 10⁴ và N = 10⁵, cả 7 và 10 vẫn nằm trong nhóm không khác best (ở N = 10⁵ chỉ chậm hơn `cutoff = 20` khoảng 1,3%). Tuy nhiên khi tăng lên N = 10⁶, cả `cutoff = 7` (220,665 ms, chậm hơn best 2,3%) và `cutoff = 10` (218,278 ms, chậm hơn best 1,2%) đều **nằm ngoài nhóm không khác best**, cho thấy trên CPU hiện đại và JVM mới (OpenJDK 26), ngưỡng tối ưu dịch chuyển lên cao hơn một chút (quanh **16–20**) so với gợi ý cổ điển của giáo trình.


4. **Dữ liệu có cấu trúc tạo ra các điểm tối ưu rất khác nhau.**
    - `sorted` và `nearly`: cutoff lớn (**64–100**, chạm biên trên của dải khảo sát) đạt hiệu năng tốt nhất, nhanh hơn mergesort thuần từ **1,40× đến 2,00×**. Nguyên nhân là insertion sort chạy tuyến tính $O(k)$ trên các đoạn đã hoặc gần có thứ tự, trong khi mergesort bài giảng không cài bước dừng sớm (*stop if already sorted*) nên luôn tốn đủ chi phí trộn.
    - `reverse`: đây là trường hợp xấu nhất $O(k^2)$ của insertion sort, nên cutoff tối ưu bị kéo xuống rất thấp, chỉ nằm trong khoảng **4–8** (cụ thể tốt nhất ở `8` với N = 10⁴, `4` với N = 10⁵ và `7` với N = 10⁶; ở N = 10⁴ và N = 10⁶, `cutoff = 7` nhanh hơn `cutoff = 10` có ý nghĩa thống kê với `p = 0,000` và `p = 0,022`).
    - `dups` (nhiều phần tử trùng lặp): ít phải hoán đổi hơn so với mảng ngẫu nhiên thuần túy nên ưu ái cutoff nhỉnh hơn một chút, tối ưu ổn định ở **20–24** (`24` ở N = 10⁴ và `20` ở N = 10⁵, 10⁶; nhóm không khác best ở N = 10⁶ là `{16, 20, 24}`).

   Xét bảng độ chậm tương đối trung bình, **`cutoff = 20`** đạt giá trị nhỏ nhất trên toàn bộ 15 kịch bản (**1,125**), nhỏ nhất trên các bộ dữ liệu lớn `N >= 10⁵` (**1,100**), và đồng hạng nhất với `cutoff = 16` trên `random N >= 10⁵` (**1,001** — chỉ lệch 0,1% so với mốc tốt nhất).


5. **Độ tin cậy của phép đo.**

   Nhờ cơ chế warm-up JIT và chạy xen kẽ (interleaved) trên phần cứng ổn định, sai số đo ở quy mô lớn rất nhỏ: tại N = 10⁶ (15 lần lặp), khoảng tin cậy 95% (`ci95`) của dữ liệu `random` chỉ nằm trong khoảng **±1,02 đến ±3,23 ms** (tương đương 0,5%–1,5% giá trị trung bình; riêng tại `cutoff = 16` và `20` chỉ khoảng ±1,03 ms). Ở N = 10⁴, thời gian chạy rất ngắn (~1,2 ms) nên nhiễu tương đối lớn hơn (`std` dao động từ 0,042 đến 0,215 ms), khiến dải rộng 5–32 không thể phân biệt rạch ròi về mặt thống kê.

## 5. Kết luận

- Trên cấu hình máy thử nghiệm (`Intel Core Ultra 5 225H`, 14 nhân, Windows 11, OpenJDK 26) với bản cài đặt Mergesort theo bài giảng, **khoảng CUTOFF tối ưu trên dữ liệu `random` là `16–20`** (nằm gọn trong vùng đáy phẳng an toàn `12–24`).
- Nếu phải chọn **một giá trị duy nhất** cân bằng tốt cho cả dữ liệu ngẫu nhiên lẫn các phân bố có cấu trúc, **`CUTOFF = 20`** là lựa chọn khuyến nghị tốt nhất (đạt độ chậm tương đối trung bình nhỏ nhất khi gộp mọi nhóm ở mức 1,125; đồng hạng nhất 1,001 trên `random N >= 10⁵`; nằm trong nhóm không khác best ở cả 3 kích thước của `random` và `dups`). `CUTOFF = 16` là phương án thay thế gần như tương đương.
- So với mergesort thuần (`cutoff = 1`), dùng `CUTOFF = 16–20` giúp giảm khoảng **8,8%–11,6%** thời gian chạy trên dữ liệu `random` (và lên tới 40%–50% trên dữ liệu đã/gần sắp xếp).
- Hai con số giáo trình **`7` và `10`** không khác nhau có ý nghĩa thống kê trên dữ liệu `random`, vẫn đem lại phần lớn lợi ích so với mergesort thuần, nhưng chậm hơn khoảng **1,2%–2,3%** so với vùng tối ưu `16–20` ở N = 10⁶. Kết quả này khẳng định cần đo thực nghiệm trên đúng môi trường đích thay vì áp dụng cứng nhắc hằng số trong sách.
## 6. Hạn chế
- Đo trên một máy (VM 1 vCPU), một JVM, nên nhiễu nền có thể lớn; chỉ có 15 lần lặp ở N=10⁶.
- Chỉ thử kiểu `Integer` (đối tượng đóng hộp, so sánh qua `compareTo`); kiểu khác (String, đối tượng lớn, `int[]`) có thể cho cutoff khác.
- Lưới cutoff thưa ở phía lớn (32, 48, 64, 100); có thể mịn hơn quanh 12–32 và tăng số lần lặp nếu cần phân biệt chính xác.
- Chưa so sánh với các cải tiến khác (stop-if-sorted, bỏ bước copy), vốn sẽ thay đổi kết quả trên dữ liệu có thứ tự.

## 7. Tái lập
Xem `README.md`: `bash scripts/run_all.sh` biên dịch, kiểm thử, sinh dữ liệu, đo, và vẽ đồ thị. Dữ liệu thô: `results/benchmark_results.csv`.
