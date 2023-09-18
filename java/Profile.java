/*
https://youtu.be/bMWqmn1CNvo
May 2023
*/

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class Profile {
    String name;
    String address;
    String phone;
    boolean car;
    Peep info;

    public Profile(String name, String address, String phone, boolean car) {
        this.name = name;
        this.address = address;
        this.phone = phone;
        this.car = car;
    }

    public static void set(String file, Path path) throws IOException, WrongInputFormatException {
        BufferedReader reader = new BufferedReader(new FileReader(file));
        String line = reader.readLine();
        String[] info = line.split(",", 3);
        int[] numbs = new int[info.length];
        try {
            for (int i = 0; i < info.length; i++) numbs[i] = Integer.parseInt(info[i]);
            if (numbs[0] < 1)
                throw new WrongInputFormatException("INPUT FILE ERROR (line 1) --> Given number of members is incorrect.");
        } catch (NumberFormatException e) {
            throw new WrongInputFormatException("INPUT FILE ERROR (line 1) --> Input must be comma-spaced integers.");
        }
        path.profiles = new Profile[numbs[0]];
        path.nodes.pos = new int[] {numbs[1], numbs[2]};
        Path.Node node; int i = 0;

        try {
            while ((line = reader.readLine()) != null) {
                info = line.split(",", 7);
                if (info.length != 7) throw new NumberFormatException();
                int seats = Integer.parseInt(info[3]);
                path.profiles[i] = new Profile(info[0], info[1], info[2], seats > 0);
                int[] pos = new int[]{Integer.parseInt(info[4]), Integer.parseInt(info[5])};
                if ((node = exists(path.nodes.next, pos)) == null) {
                    node = new Path.Node(pos);
                    Path.append(path.nodes, node);
                }

                if (seats > 0) {
                    path.profiles[i].info = new Peep.Driver(i, seats);
                    Peep.conceive(path.drivers, path.profiles[i].info);
                    Peep.append(node.drivers, path.profiles[i].info);
                } else {
                    path.profiles[i].info = new Peep.Member(i, info[6]);
                    Peep.conceive(path.members, path.profiles[i].info);
                    Peep.append(node.members, path.profiles[i].info);
                }
                path.profiles[i++].info.node = node;
            }
        } catch (NumberFormatException e) {
            throw new WrongInputFormatException("INPUT FILE ERROR (line " + (i + 2) +
                    ") --> Member info is incorrect.");
        } catch (ArrayIndexOutOfBoundsException e) {
            throw new WrongInputFormatException("INPUT FILE ERROR (line 1) --> Given number of members is incorrect.");
        }
    }

    public static Path.Node exists(Path.Node node, int[] pos) {
        while (node != null) {
            if (node.pos[0] == pos[0] && node.pos[1] == pos[1]) return node;
            node = node.next;
        }
        return null;
    }
}
