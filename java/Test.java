import java.io.FileNotFoundException;
import java.io.IOException;

public class Test {
    public static void main(String[] args) {
        try {
            if (args.length > 2) throw new ArrayIndexOutOfBoundsException();
            int p = Integer.parseInt(args[1]);
            if (p < 1) throw new NumberFormatException();
            Path path = Rome.optimize(args[0], p);
            ps(path);
        } catch (FileNotFoundException e) {
            System.out.print("File not found.\n");
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.print("Incorrect input command format.\n");
        } catch (NumberFormatException e) {
            System.out.print("Permutation number must be an integer greater than one.\n");
        } catch (WrongInputFormatException e) {
            System.out.println(e.getMessage());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void ps(Path path) {
        System.out.printf("weight = %.2f\n", path.weight);
        for (int i = 0; i < path.profiles.length; i++) {
            if (path.profiles[i].car) {
                System.out.printf("%s --> [", path.profiles[i].name);
                Peep.Driver driver = (Peep.Driver) path.profiles[i].info;
                for (int j = driver.seats; j < driver.ppl.length; j++) {
                    System.out.printf("%s,", path.profiles[driver.ppl[j]].name);
                    if (j != driver.ppl.length - 1) System.out.print(" ");
                }
                System.out.print("]\n");
            }
        }
        System.out.print("\n");
    }
}
