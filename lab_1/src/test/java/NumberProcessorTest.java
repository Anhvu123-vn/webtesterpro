import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class NumberProcessorTest {

    // Path 1: n = 0 (không vào loop)
    @Test
    void testN0() {
        NumberProcessor np = new NumberProcessor();
        assertEquals(0, np.processNumbers(0));
    }

    // Path 2: n = 1 (chỉ có số lẻ)
    @Test
    void testN1() {
        NumberProcessor np = new NumberProcessor();
        assertEquals(-1, np.processNumbers(1));
    }

    // Path 3: n = 2 (có cả chẵn và lẻ)
    @Test
    void testN2() {
        NumberProcessor np = new NumberProcessor();
        assertEquals(1, np.processNumbers(2));
    }

    // Path 4: n = 5 (full mix case)
    @Test
    void testN5() {
        NumberProcessor np = new NumberProcessor();
        assertEquals(-3, np.processNumbers(5));
    }
}