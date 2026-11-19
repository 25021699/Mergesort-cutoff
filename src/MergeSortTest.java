import java.util.Arrays;
import java.util.Random;

/** Kiểm thử tính đúng đắn: so với Arrays.sort, mọi cutoff, nhiều kích thước, + kiểm tra ổn định. */
public class MergeSortTest {
    record Item(int key, int id) implements Comparable<Item> {
        public int compareTo(Item o) { return Integer.compare(key, o.key); }
    }

    public static void main(String[] args) {
        Random rnd = new Random(1);
        int checks = 0;
        int[] cutoffs = {1, 2, 3, 5, 7, 10, 16, 50, 1000};
        for (int cutoff : cutoffs)
            for (String type : DataGenerator.TYPES)
                for (int n : new int[]{0, 1, 2, 3, 7, 8, 9, 10, 11, 100, 1023, 1024, 1025, 5000}) {
                    Integer[] a = DataGenerator.generate(type, n);
                    Integer[] expected = a.clone();
                    Arrays.sort(expected);
                    MergeSort.sort(a, cutoff);
                    if (!Arrays.equals(a, expected))
                        throw new AssertionError("FAIL " + type + " n=" + n + " cutoff=" + cutoff);
                    checks++;
                }
        // ổn định: sắp theo key, các phần tử cùng key phải giữ nguyên thứ tự id tăng
        for (int cutoff : cutoffs) {
            Item[] items = new Item[3000];
            for (int i = 0; i < items.length; i++) items[i] = new Item(rnd.nextInt(20), i);
            MergeSort.sort(items, cutoff);
            for (int i = 1; i < items.length; i++) {
                if (items[i - 1].key() > items[i].key()) throw new AssertionError("not sorted");
                if (items[i - 1].key() == items[i].key() && items[i - 1].id() > items[i].id())
                    throw new AssertionError("NOT STABLE, cutoff=" + cutoff);
            }
            checks++;
        }
        System.out.println("All " + checks + " checks passed (correctness + stability).");
    }
}
