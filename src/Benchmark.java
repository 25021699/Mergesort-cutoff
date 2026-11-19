import java.io.*;
import java.util.*;


public class Benchmark {
    static final int[] CUTOFFS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 24, 32, 48, 64, 100};
    static final int[] SIZES = {10_000, 100_000, 1_000_000};

    public static void main(String[] args) throws Exception {
        String out = args.length > 0 ? args[0] : "results/benchmark_results.csv";
        int[] reps = {101, 41, 15};
        if (args.length >= 4) for (int i = 0; i < 3; i++) reps[i] = Integer.parseInt(args[i + 1]);

        File outFile = new File(out).getAbsoluteFile();
        outFile.getParentFile().mkdirs();
        writeMachineInfo(outFile.getParentFile());

        // --- warm-up toàn cục: để JIT biên dịch merge/insertion/sort ---
        System.out.println("Warm-up...");
        Integer[] w = DataGenerator.generate("random", 200_000);
        for (int r = 0; r < 6; r++)
            for (int c : CUTOFFS) MergeSort.sort(w.clone(), c);

        try (PrintWriter csv = new PrintWriter(new BufferedWriter(new FileWriter(outFile)))) {
            csv.println("dataset,n,cutoff,rep,time_ms");
            for (int si = 0; si < SIZES.length; si++) {
                int n = SIZES[si];
                for (String type : DataGenerator.TYPES) {
                    Integer[] data = DataGenerator.generate(type, n);
                    for (int c : CUTOFFS) MergeSort.sort(data.clone(), c);   // warm-up cục bộ (không ghi)
                    System.gc();
                    for (int rep = 0; rep < reps[si]; rep++) {
                        for (int k = 0; k < CUTOFFS.length; k++) {
                            int cutoff = CUTOFFS[(k + rep) % CUTOFFS.length];   // xoay thứ tự
                            Integer[] copy = data.clone();                      // không tính vào thời gian
                            long t0 = System.nanoTime();
                            MergeSort.sort(copy, cutoff);
                            long t1 = System.nanoTime();
                            if (rep == 0 && !MergeSort.isSorted(copy))
                                throw new IllegalStateException("not sorted!");
                            csv.printf(Locale.ROOT, "%s,%d,%d,%d,%.4f%n", type, n, cutoff, rep, (t1 - t0) / 1e6);
                        }
                    }
                    csv.flush();
                    System.out.println("done " + type + " N=" + n);
                }
            }
        }
        System.out.println("Wrote " + out);
    }

    static void writeMachineInfo(File dir) throws IOException {
        try (PrintWriter p = new PrintWriter(new File(dir, "machine_info.txt"))) {
            p.println("os=" + System.getProperty("os.name") + " " + System.getProperty("os.version") + " " + System.getProperty("os.arch"));
            p.println("java=" + System.getProperty("java.vm.name") + " " + System.getProperty("java.version"));
            p.println("cores=" + Runtime.getRuntime().availableProcessors());
            p.println("max_heap_mb=" + Runtime.getRuntime().maxMemory() / (1024 * 1024));
            try (BufferedReader r = new BufferedReader(new FileReader("/proc/cpuinfo"))) {
                String line;
                while ((line = r.readLine()) != null)
                    if (line.startsWith("model name")) { p.println("cpu=" + line.split(":", 2)[1].trim()); break; }
            } catch (IOException ignored) { }
        }
    }
}
