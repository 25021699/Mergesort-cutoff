import java.io.*;
import java.util.Random;
import java.util.zip.GZIPOutputStream;

/**
 * Sinh bộ dữ liệu thí nghiệm (cố định seed => tái lập được).
 * 5 loại dữ liệu (kiểu Integer, đúng với kiểu Comparable dùng trong bài giảng):
 *   random   : số nguyên ngẫu nhiên đều
 *   sorted   : đã sắp tăng dần
 *   reverse  : sắp giảm dần
 *   nearly   : đã sắp, rồi hoán đổi ngẫu nhiên ~1% cặp phần tử (gần như có thứ tự)
 *   dups     : ngẫu nhiên nhưng chỉ có 100 giá trị khác nhau (nhiều khóa trùng)
 *
 * Chạy:  java -cp out DataGenerator data   -> ghi data/<type>_<N>.txt.gz (mỗi dòng 1 số)
 */
public class DataGenerator {
    public static final String[] TYPES = {"random", "sorted", "reverse", "nearly", "dups"};
    public static final long BASE_SEED = 20261119L;

    public static Integer[] generate(String type, int n) {
        Random rnd = new Random(BASE_SEED + 31L * type.hashCode() + n);
        Integer[] a = new Integer[n];
        switch (type) {
            case "random":
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt();
                break;
            case "sorted":
                for (int i = 0; i < n; i++) a[i] = i;
                break;
            case "reverse":
                for (int i = 0; i < n; i++) a[i] = n - i;
                break;
            case "nearly":
                for (int i = 0; i < n; i++) a[i] = i;
                for (int s = 0; s < n / 100; s++) {
                    int i = rnd.nextInt(n), j = rnd.nextInt(n);
                    Integer t = a[i]; a[i] = a[j]; a[j] = t;
                }
                break;
            case "dups":
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(100);
                break;
            default:
                throw new IllegalArgumentException("unknown type " + type);
        }
        return a;
    }

    public static void main(String[] args) throws IOException {
        String dir = args.length > 0 ? args[0] : "data";
        int[] sizes = {10_000, 100_000, 1_000_000};
        new File(dir).mkdirs();
        for (int n : sizes)
            for (String type : TYPES) {
                Integer[] a = generate(type, n);
                File f = new File(dir, type + "_" + n + ".txt.gz");
                try (PrintWriter out = new PrintWriter(new BufferedWriter(
                        new OutputStreamWriter(new GZIPOutputStream(new FileOutputStream(f)))))) {
                    for (Integer x : a) out.println(x);
                }
                System.out.println("wrote " + f + " (" + f.length() / 1024 + " KB)");
            }
    }
}
