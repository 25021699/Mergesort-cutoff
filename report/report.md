# Báo cáo thí nghiệm: tìm giá trị CUTOFF tốt nhất cho Mergesort

> **Ghi chú trước khi nộp:** các số liệu dưới đây đo trên máy ảo ghi trong mục 2.1 (1 vCPU). Đề bài yêu cầu
> giá trị tốt nhất *cho cấu hình máy của bạn*, vì vậy hãy chạy lại `bash scripts/run_all.sh` trên máy của mình,
> thay mục 2.1 bằng nội dung `results/machine_info.txt` mới, cập nhật các bảng/số trong mục 3–5 theo
> `results/summary.md` mới và chép đúng kết luận mà dữ liệu của bạn cho thấy.

## 1. Mục tiêu và câu hỏi thí nghiệm

Slide bài giảng (2.2, "practical improvements") cho biết mergesort có thể chuyển sang insertion sort khi mảng con
đủ nhỏ vì mergesort có nhiều overhead với mảng rất nhỏ; giáo trình nhắc tới CUTOFF = 7 (cũ) và 10 (mới).
Câu hỏi: **với mergesort tự cài đặt theo bài giảng, trên máy này, CUTOFF nào cho thời gian chạy nhỏ nhất?**
Giá trị 7 và 10 có thực sự khác nhau không?

## 2. Mô tả thí nghiệm

### 2.1 Môi trường
| | |
|---|---|
| CPU | Intel(R) Xeon(R) Processor @ 2.10GHz |
| Số nhân khả dụng | 1 |
| Hệ điều hành | Linux 6.18.44-fc-v653 amd64 |
| Java | OpenJDK 64-Bit Server VM 21.0.13.1 |
| Heap tối đa | 1979 MB |

### 2.2 Cài đặt (`src/MergeSort.java`)
- Cài đặt **từ bài giảng**: `merge(a, aux, lo, mid, hi)` (slide 7: copy sang `aux[]` rồi trộn), `sort(a, aux, lo, hi)` top-down
  (slide 8), điều kiện cutoff `if (hi <= lo + CUTOFF - 1) { insertionSort(a, lo, hi); return; }` (slide 18),
  insertion sort dùng `less`/`exch` (slide 52). Không dùng thêm cải tiến nào khác (không có "stop if already sorted",
  không "eliminate the copy") để chỉ đo ảnh hưởng của CUTOFF.
- Khác slide duy nhất: CUTOFF là tham số thay vì hằng số. `cutoff = 1` tương đương mergesort thuần (không insertion sort) và là mốc so sánh.
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
cutoff nào có p ≥ 0.05 được coi là *không khác biệt có ý nghĩa thống kê* với cutoff tốt nhất. Cùng cách đó được dùng để so 7 với 10.

## 3. Kết quả

### 3.1 Cutoff tốt nhất theo từng nhóm
| dataset   |         N |   cutoff tốt nhất |   best (ms) |   cutoff=1 (ms) |   tăng tốc so với cutoff=1 |   c=7 (ms) |   c=10 (ms) |   p (7 vs 10) | cutoff không khác best (p≥0.05)           |
|:----------|----------:|------------------:|------------:|----------------:|---------------------------:|-----------:|------------:|--------------:|:------------------------------------------|
| random    |    10,000 |                32 |       1.28  |           1.64  |                       1.28 |      1.45  |       1.42  |         0.594 | 16 32                                     |
| random    |   100,000 |                24 |      17.6   |          20.1   |                       1.15 |     18.8   |      18.6   |         0.628 | 12 14 16 20 24 32 48 64                   |
| random    | 1,000,000 |                24 |     248     |         279     |                       1.13 |    254     |     262     |         0.236 | 2 4 5 6 7 8 9 10 12 14 16 20 24 32 48 100 |
| sorted    |    10,000 |               100 |       0.322 |           0.669 |                       2.08 |      0.505 |       0.465 |         0     | 100                                       |
| sorted    |   100,000 |               100 |       5.12  |           9.11  |                       1.78 |      7.06  |       7.06  |         0.984 | 100                                       |
| sorted    | 1,000,000 |                64 |      65.9   |         101     |                       1.53 |     81     |      79.6   |         0.691 | 64 100                                    |
| reverse   |    10,000 |                 7 |       0.578 |           0.696 |                       1.2  |      0.578 |       0.606 |         0     | 5 6 7 8 9 12                              |
| reverse   |   100,000 |                 9 |       7.24  |           8.42  |                       1.16 |      7.47  |       7.47  |         0.978 | 7 8 9                                     |
| reverse   | 1,000,000 |                12 |      89.9   |         101     |                       1.12 |     92.2   |      93.1   |         0.9   | 2 3 4 5 6 7 8 9 10 12 14                  |
| nearly    |    10,000 |               100 |       0.493 |           0.892 |                       1.81 |      0.687 |       0.642 |         0     | 100                                       |
| nearly    |   100,000 |               100 |       6.43  |          10.3   |                       1.61 |      8.68  |       8.37  |         0.344 | 100                                       |
| nearly    | 1,000,000 |                64 |      81     |         119     |                       1.47 |    101     |      99.4   |         0.774 | 20 32 48 64 100                           |
| dups      |    10,000 |                10 |       1.01  |           1.27  |                       1.26 |      1.05  |       1.01  |         0.054 | 6 7 9 10 12 14 16 20 24 32 48 64          |
| dups      |   100,000 |                14 |      11.6   |          14.3   |                       1.23 |     12     |      12.2   |         0.17  | 14 16 20 24 48                            |
| dups      | 1,000,000 |                16 |     138     |         164     |                       1.19 |    152     |     147     |         0.283 | 4 6 9 10 12 16 20 24 48                   |

### 3.2 Dữ liệu random (kịch bản chính)

**N = 10 000**

|   cutoff |   số lần đo |   mean (ms) |   median (ms) |   std (ms) |   CI95 ±(ms) |   mean / mean(cutoff=1) |
|---------:|------------:|------------:|--------------:|-----------:|-------------:|------------------------:|
|    1.000 |     101.000 |       1.636 |         1.512 |      0.716 |        0.141 |                   1.000 |
|    5.000 |     101.000 |       1.495 |         1.336 |      0.932 |        0.184 |                   0.913 |
|    7.000 |     101.000 |       1.449 |         1.330 |      0.593 |        0.117 |                   0.885 |
|   10.000 |     101.000 |       1.418 |         1.304 |      0.571 |        0.113 |                   0.866 |
|   12.000 |     101.000 |       1.491 |         1.296 |      0.840 |        0.166 |                   0.911 |
|   16.000 |     101.000 |       1.350 |         1.290 |      0.476 |        0.094 |                   0.825 |
|   20.000 |     101.000 |       1.448 |         1.268 |      0.800 |        0.158 |                   0.885 |
|   24.000 |     101.000 |       1.423 |         1.265 |      0.748 |        0.148 |                   0.870 |
|   32.000 |     101.000 |       1.275 |         1.256 |      0.132 |        0.026 |                   0.779 |
|   64.000 |     101.000 |       1.514 |         1.302 |      0.853 |        0.168 |                   0.925 |
|  100.000 |     101.000 |       1.486 |         1.478 |      0.137 |        0.027 |                   0.908 |

**N = 100 000**

|   cutoff |   số lần đo |   mean (ms) |   median (ms) |   std (ms) |   CI95 ±(ms) |   mean / mean(cutoff=1) |
|---------:|------------:|------------:|--------------:|-----------:|-------------:|------------------------:|
|    1.000 |      41.000 |      20.115 |        19.856 |      2.731 |        0.862 |                   1.000 |
|    5.000 |      41.000 |      18.559 |        18.506 |      2.777 |        0.876 |                   0.923 |
|    7.000 |      41.000 |      18.769 |        18.275 |      3.022 |        0.954 |                   0.933 |
|   10.000 |      41.000 |      18.579 |        18.179 |      3.102 |        0.979 |                   0.924 |
|   12.000 |      41.000 |      18.151 |        17.858 |      3.202 |        1.011 |                   0.902 |
|   16.000 |      41.000 |      17.968 |        17.598 |      2.840 |        0.896 |                   0.893 |
|   20.000 |      41.000 |      17.672 |        17.637 |      2.500 |        0.789 |                   0.879 |
|   24.000 |      41.000 |      17.562 |        17.568 |      2.966 |        0.936 |                   0.873 |
|   32.000 |      41.000 |      17.774 |        17.494 |      2.991 |        0.944 |                   0.884 |
|   64.000 |      41.000 |      18.607 |        18.436 |      3.261 |        1.029 |                   0.925 |
|  100.000 |      41.000 |      21.422 |        20.799 |      3.805 |        1.201 |                   1.065 |

**N = 1 000 000**

|   cutoff |   số lần đo |   mean (ms) |   median (ms) |   std (ms) |   CI95 ±(ms) |   mean / mean(cutoff=1) |
|---------:|------------:|------------:|--------------:|-----------:|-------------:|------------------------:|
|    1.000 |      15.000 |     279.185 |       287.074 |     36.231 |       20.064 |                   1.000 |
|    5.000 |      15.000 |     268.056 |       271.862 |     36.148 |       20.018 |                   0.960 |
|    7.000 |      15.000 |     253.704 |       263.210 |     26.738 |       14.807 |                   0.909 |
|   10.000 |      15.000 |     261.598 |       265.847 |     28.062 |       15.540 |                   0.937 |
|   12.000 |      15.000 |     253.588 |       268.382 |     31.392 |       17.384 |                   0.908 |
|   16.000 |      15.000 |     255.524 |       263.787 |     31.462 |       17.423 |                   0.915 |
|   20.000 |      15.000 |     253.351 |       262.818 |     32.290 |       17.882 |                   0.907 |
|   24.000 |      15.000 |     248.020 |       260.362 |     30.074 |       16.654 |                   0.888 |
|   32.000 |      15.000 |     254.244 |       256.172 |     30.712 |       17.008 |                   0.911 |
|   64.000 |      15.000 |     276.158 |       277.336 |     38.147 |       21.125 |                   0.989 |
|  100.000 |      15.000 |     266.543 |       267.127 |     30.163 |       16.704 |                   0.955 |

### 3.3 Đồ thị

![Thời gian theo CUTOFF](../results/charts/time_vs_cutoff.png)

![Tỉ lệ so với cutoff=1](../results/charts/relative_to_pure.png)

![random, N lớn nhất](../results/charts/random_largest_zoom.png)

![Tổng hợp](../results/charts/aggregate_relative.png)

![Heatmap random](../results/charts/heatmap_random.png)

Độ chậm tương đối trung bình so với cutoff tốt nhất của từng nhóm (1.000 = tốt nhất), xem thêm `results/summary.md`:
với `random`, N ≥ 10⁵ thì cutoff 24 tốt nhất, 20 (+1.4%), 32 (+1.9%), 16 (+2.7%), 12 (+2.8%), 14 (+3.1%);
tính trên mọi nhóm dữ liệu thì cutoff 16 có độ chậm tương đối trung bình nhỏ nhất, kế đó là 14, 32, 20, 24.

## 4. Phân tích

1. **Cutoff có ích rõ rệt.** Trên dữ liệu random, so với mergesort thuần (cutoff=1) thời gian giảm khoảng 22% (N=10⁴, cutoff 32),
   13% (N=10⁵, cutoff 24) và 11% (N=10⁶, cutoff 24). Lý do: ở mức đệ quy thấp nhất mergesort phải gọi đệ quy, copy sang `aux` và trộn cho những mảng chỉ vài phần tử,
   trong khi insertion sort trên mảng ≤ vài chục phần tử gần như không có overhead.
2. **Đường cong có đáy phẳng và rộng (khoảng 12–32).** Chi phí của insertion sort tăng theo bình phương kích thước khối nên cutoff quá lớn
   (64, 100) làm thời gian tăng trở lại, nhưng trong vùng 12–32 chênh lệch giữa các giá trị nhỏ hơn nhiễu đo. Ở N=10⁶ hầu hết cutoff từ 2 đến 48 không khác best có ý nghĩa thống kê.
   Điều này cho thấy **không nên tin vào "một con số chính xác"**; kết luận đúng là một khoảng.
3. **7 và 10 gần như tương đương nhau** (paired t-test cho random: p = 0.59, 0.63, 0.24 với N = 10⁴, 10⁵, 10⁶; không khác biệt có ý nghĩa).
   Tuy nhiên với N=10⁵ cả hai đều chậm hơn cutoff 24 khoảng 6–7% và nằm ngoài nhóm "không khác best"; ở N=10⁶ chậm hơn 2–5% nhưng chưa đủ ý nghĩa thống kê do nhiễu lớn.
   Trên máy này giá trị lớn hơn (khoảng 16–24) cho kết quả nhỉnh hơn 7/10.
4. **Dữ liệu có cấu trúc cho đáp án khác nhau.**
   - `sorted`, `nearly`: cutoff lớn (64–100, biên của dải thử) thắng, vì insertion sort chạy tuyến tính trên dữ liệu gần có thứ tự trong khi mergesort bài giảng
     không có bước "stop if already sorted" nên luôn trộn đủ N lg N. Đây là lý do cutoff lớn trông "tốt" ở các nhóm này, không phải thông tin về dữ liệu ngẫu nhiên.
   - `reverse`: đúng trường hợp xấu nhất của insertion sort (bình phương), nên cutoff tốt nhất nhỏ (7–12) và cutoff 64–100 chậm rõ rệt
     (ví dụ N=10⁵: cutoff 100 → khoảng 19 ms so với khoảng 7.5 ms ở cutoff 7).
   - `dups`: cutoff tốt nhất 10–16.
   Vì vậy ta chọn cutoff theo `random` (trường hợp tổng quát) và dùng các nhóm còn lại để kiểm tra độ bền; giá trị khoảng 16 cho độ chậm tương đối nhỏ nhất khi gộp mọi nhóm và vẫn nằm trong nhóm "không khác best" ở cả ba N của `random`.
5. **Độ tin cậy của phép đo.** Ở N=10⁶ chỉ có 15 lần lặp và CI95 khoảng ±15–20 ms (~7% giá trị trung bình), nên khó phân biệt các cutoff gần nhau;
   khi N nhỏ hơn thì nhiễu tương đối của thời gian ngắn (≈1 ms) cũng lớn (ví dụ N=10⁴ có độ lệch chuẩn rất khác nhau giữa các cutoff).
   Thiết kế xen kẽ + paired test giúp giảm ảnh hưởng nhiễu, nhưng điểm cực tiểu chính xác (24 hay 32...) không nên diễn giải quá mức.

## 5. Kết luận

- Trên máy đo, với mergesort cài theo bài giảng và dữ liệu `random`, **CUTOFF tốt nhất theo trung bình là 24** (N=10⁵, 10⁶); vùng gần tối ưu rộng, khoảng **12–32**.
  Để chọn một giá trị cho mọi loại dữ liệu và kích thước, **CUTOFF ≈ 16** là lựa chọn an toàn (chậm hơn best khoảng 2–3% trên random với N ≥ 10⁵; ở N=10⁴ chênh ~6% nhưng nhiễu lớn; và có độ chậm tương đối nhỏ nhất khi gộp mọi nhóm).
- So với mergesort thuần, cutoff phù hợp giúp nhanh hơn khoảng 11–13% (N ≥ 10⁵) trên dữ liệu random.
- CUTOFF 7 và 10 của giáo trình không khác nhau có ý nghĩa thống kê và chậm hơn mức tối ưu của máy này một chút (~2–7% trên random); giá trị tối ưu phụ thuộc phần cứng/JVM nên cần đo lại trên từng máy.

## 6. Hạn chế
- Đo trên một máy (VM 1 vCPU), một JVM, nên nhiễu nền có thể lớn; chỉ có 15 lần lặp ở N=10⁶.
- Chỉ thử kiểu `Integer` (đối tượng đóng hộp, so sánh qua `compareTo`); kiểu khác (String, đối tượng lớn, `int[]`) có thể cho cutoff khác.
- Lưới cutoff thưa ở phía lớn (32, 48, 64, 100); có thể mịn hơn quanh 12–32 và tăng số lần lặp nếu cần phân biệt chính xác.
- Chưa so sánh với các cải tiến khác (stop-if-sorted, bỏ bước copy), vốn sẽ thay đổi kết quả trên dữ liệu có thứ tự.

## 7. Tái lập
Xem `README.md`: `bash scripts/run_all.sh` biên dịch, kiểm thử, sinh dữ liệu, đo, và vẽ đồ thị. Dữ liệu thô: `results/benchmark_results.csv`.
