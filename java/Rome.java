/*
https://youtu.be/3pCPQDxZzfY
June 2023
*/

import java.io.IOException;

public class Rome {
    Path path;
    Peep.Member[] members;
    Rome next;
    Rome prev;

    public Rome() {}
    public Rome(Path path, Peep.Member[] members) {
        this.members = members;
        this.path = Path.nick(path, members);
    }

    public static void append(Rome head, Rome now) {
        head.prev.next = now;
        now.prev = head.prev;
        head.prev = now;
    }

    public static void remove(Rome head, Rome now) {
        if (now.next != null) {
            now.prev.next = now.next;
            now.next.prev = now.prev;
        } else {
            head.prev = now.prev;
            now.prev.next = null;
        }
    }

    public static Path optimize(String file, int max) throws IOException, WrongInputFormatException {
        Path path = Path.set(file);
        Peep.Member[] members = Path.getMemberArray(path);
        int[][] combos = Rome.getMemberCombos(path, max);
        Rome head = new Rome();
        Rome worst = new Rome();
        worst.path = new Path();
        head.prev = head;
        append(head, worst);
        Rome.permute(path, head, combos, members, 0, combos[0].length);
        return (head.next.path);
    }

    public static int[][] getMemberCombos(Path path, int max) {
        Peep.Member head = Peep.copyMemberIDs(path);
        Peep.Driver[] all = new Peep.Driver[Peep.number(path.drivers)];
        for (int i = 0; i < all.length; i++) {
            all[i] = new Peep.Driver();
            all[i].up = all[i];
        }

        int k = 0;
        while (head.down != null) {
            Peep.Member member = (Peep.Member) head.down;
            Peep.Driver driver = (Peep.Driver) path.drivers.down;
            Peep.Driver closest = (Peep.Driver) path.drivers.down;
            int i = 0; int j = 0;
            while (driver != null) {
                if (Path.distance(closest.node, path.profiles[member.id].info.node) >
                        Path.distance(driver.node, path.profiles[member.id].info.node)) {
                    closest = driver;
                    j = i;
                }
                i++;
                driver = (Peep.Driver) driver.down;
            }
            Peep.conceive(all[j], new Peep.Member(k++, null));
            Peep.resolve(head, member);
        }

        int ii = 0;
        for (Peep.Driver driver : all) if (driver.down != null) ii++;
        int[][] combos = new int[ii][]; ii = 0;
        for (Peep.Driver driver : all) {
            if (driver.down != null) {
                int n = Peep.number(driver);
                if (n < max) combos[ii] = new int[n];
                else combos[ii] = new int[max];
                Peep peep = driver.down;
                for (int j = 0; j < combos[ii].length; j++) {
                    combos[ii][j] = peep.id;
                    peep = peep.down;
                }
                ii++;
            }
        }
        return combos;
    }

    public static void permute(Path path, Rome head, int[][] combos, Peep.Member[] members, int c, int m) throws WrongInputFormatException {
        if (m != 1) {
            permute(path, head, combos, members, c, m - 1);
            for (int i = 0; i < m - 1; i++) {
                if (m % 2 == 0) Peep.swap(members, combos[c][i], combos[c][m - 1]);
                else Peep.swap(members, combos[c][0], combos[c][m - 1]);
                permute(path, head, combos, members, c, m - 1);
            }
        } else {
            if (c < combos.length - 1) permute(path, head, combos, members, c + 1, combos[c + 1].length);
            else {
                append(head, new Rome(Path.copy(path), Peep.copyMemberArray(members)));
                if (head.next.path.weight > head.next.next.path.weight) remove(head, head.next);
                else remove(head, head.next.next);
            }
        }
    }
}
