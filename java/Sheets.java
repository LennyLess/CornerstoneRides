/*
thanks to nick, chloe, and leonard
https://youtu.be/uvAvQvPJ_H4?t=450
June 2023
*/

import java.io.*;

public class Sheets {
    public static void main(String[] args) {
        try {
            if (args.length != 3) throw new WrongInputFormatException("Incorrect input format.\n");
            int p = Integer.parseInt(args[1]);
            if (p < 1) throw new NumberFormatException();

            File file = new File(args[2]);
            if (file.createNewFile()) {
                Path path = Rome.optimize(args[0], p);
                Test.ps(path);
                BufferedWriter bw = new BufferedWriter(new FileWriter(file));
                boolean[] checks = new boolean[path.profiles.length];
                int last = 0;

                for (int i = 0; i < path.profiles.length; i++) {
                    if (isDriver(path.profiles[i])) {
                        checks[i] = true; last = i;
                        bw.write(path.profiles[i].name);
                        Peep.Driver driver = (Peep.Driver) path.profiles[i].info;
                        for (int j = driver.seats; j < driver.ppl.length; j++) bw.write(',');
                    }
                }

                bw.write('\n');
                for (int i = 0; i < path.profiles.length; i++) {
                    if (checks[i]) {
                        Peep.Driver driver = (Peep.Driver) path.profiles[i].info;
                        for (int j = driver.seats; j < driver.ppl.length; j++) {
                            bw.write(path.profiles[driver.ppl[j]].name);
                            if (i != last || j < driver.ppl.length - 1) bw.write(',');
                        }
                    }
                }

                bw.write('\n');
                for (int i = 0; i < path.profiles.length; i++) {
                    if (checks[i]) {
                        Peep.Driver driver = (Peep.Driver) path.profiles[i].info;
                        for (int j = driver.seats; j < driver.ppl.length; j++) {
                            bw.write(path.profiles[driver.ppl[j]].address);
                            if (i != last || j < driver.ppl.length - 1) bw.write(',');
                        }
                    }
                }

                bw.write('\n');
                for (int i = 0; i < path.profiles.length; i++) {
                    if (checks[i]) {
                        Peep.Driver driver = (Peep.Driver) path.profiles[i].info;
                        for (int j = driver.seats; j < driver.ppl.length; j++) {
                            bw.write(path.profiles[driver.ppl[j]].phone);
                            if (i != last || j < driver.ppl.length - 1) bw.write(',');
                        }
                    }
                }

                bw.close();
            } else System.out.print("File already exists!\n");

        } catch (WrongInputFormatException e) {
            System.out.print(e.getMessage());
        } catch (FileNotFoundException e) {
            System.out.print("File not found.\n");
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.print("Incorrect input command format.\n");
        } catch (NumberFormatException e) {
            System.out.print("Permutation number must be an integer greater than one.\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static boolean isDriver(Profile profile) {
        if (!profile.car) return false;
        Peep.Driver driver = (Peep.Driver) profile.info;
        return driver.seats != driver.ppl.length;
    }
}
