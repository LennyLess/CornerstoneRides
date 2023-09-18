/*
https://youtu.be/A4IxJj4eHWM
June 2023
*/

import java.io.IOException;

public class Path {
    Profile[] profiles;
    Peep.Member members;
    Peep.Driver drivers;
    Node nodes;
    double weight;

    public Path() {
        this.members = new Peep.Member();
        this.drivers = new Peep.Driver();
        this.nodes = new Node();
        this.weight = Double.POSITIVE_INFINITY;
        this.members.prev = this.members;
        this.members.up = this.members;
        this.drivers.prev = this.drivers;
        this.drivers.up = this.drivers;
        this.nodes.prev = this.nodes;
    }

    public static Path copy(Path path) throws WrongInputFormatException {
        Path copy = new Path();
        copy.weight = path.weight;
        copy.profiles = new Profile[path.profiles.length];
        try {
            for (int i = 0; i < path.profiles.length; i++) copy.profiles[i] = new Profile(path.profiles[i].name,
                        path.profiles[i].address, path.profiles[i].phone, path.profiles[i].car);
        } catch (NullPointerException e) {
            throw new WrongInputFormatException("INPUT FILE ERROR (line 1) --> Given number of members is incorrect.");
        }

        Peep.Member member = (Peep.Member) path.members.down;
        while (member != null) {
            Peep.Member current = new Peep.Member(member.id, member.pref);
            copy.profiles[current.id].info = current;
            Peep.conceive(copy.members, current);
            member = (Peep.Member) member.down;
        }

        Peep.Driver driver = (Peep.Driver) path.drivers.down;
        while (driver != null) {
            Peep.Driver current = new Peep.Driver(driver.id, driver.ppl.length);
            System.arraycopy(driver.ppl, 0, current.ppl, 0, driver.ppl.length);
            current.seats = driver.seats;
            copy.profiles[current.id].info = current;
            Peep.conceive(copy.drivers, current);
            driver = (Peep.Driver) driver.down;
        }

        copy.nodes.pos = path.nodes.pos;
        Node node = path.nodes.next;
        while (node != null) {
            Node now = new Node(node.pos);
            member = (Peep.Member) node.members.next;
            while (member != null) {
                Peep.Member current = (Peep.Member) copy.profiles[member.id].info;
                Peep.append(now.members, current);
                current.node = now;
                member = (Peep.Member) member.next;
            }

            driver = (Peep.Driver) node.drivers.next;
            while (driver != null) {
                Peep.Driver current = (Peep.Driver) copy.profiles[driver.id].info;
                Peep.append(now.drivers, current);
                current.node = now;
                driver = (Peep.Driver) driver.next;
            }
            append(copy.nodes, now);
            node = node.next;
        }

        for (int i = 0; i < copy.profiles.length; i++) {
            if (copy.profiles[i].info == null && copy.profiles[i].car) {
                driver = (Peep.Driver) path.profiles[i].info;
                Peep.Driver now = new Peep.Driver(driver.id, driver.ppl.length);
                System.arraycopy(driver.ppl, 0, now.ppl, 0, driver.ppl.length);
                now.seats = driver.seats;
                copy.profiles[i].info = now;
            } else if (copy.profiles[i].info == null) {
                member = (Peep.Member) path.profiles[i].info;
                copy.profiles[i].info = new Peep.Member(member.id, member.pref);
            }
            if (copy.profiles[i].info.node == null) copy.profiles[i].info.node = new Node(path.profiles[i].info.node.pos);
        }
        return copy;
    }

    public static Path set(String file) throws IOException, WrongInputFormatException {
        Path path = new Path();
        Profile.set(file, path);
        chloe(path);
        leonard(path);
        return path;
    }

    public static class Node {
        int[] pos;
        Node prev;
        Node next;
        Peep.Member members;
        Peep.Driver drivers;

        public Node() {}
        public Node(int[] pos) {
            this.pos = pos;
            this.members = new Peep.Member();
            this.drivers = new Peep.Driver();
            this.members.prev = this.members;
            this.drivers.prev = this.drivers;
        }
    }

    public static void append(Node head, Node now) {
        head.prev.next = now;
        now.prev = head.prev;
        head.prev = now;
    }

    public static void remove(Node head, Node now) {
        if (now.next != null) {
            now.prev.next = now.next;
            now.next.prev = now.prev;
        } else {
            head.prev = now.prev;
            now.prev.next = null;
        }
    }

    public static double distance(Node a, Node b) {
        return (Math.sqrt(Math.pow(a.pos[0] - b.pos[0], 2) + Math.pow(a.pos[1] - b.pos[1], 2)));
    }

    public static Peep.Member[] getMemberArray(Path path) {
        Peep.Member[] members = new Peep.Member[Peep.number(path.members)];
        Peep.Member member = (Peep.Member) path.members.down;
        for (int i = 0; i < members.length; i++) {
            members[i] = member;
            member = (Peep.Member) member.down;
        }

        Node church = new Node(new int[] {0, 0});
        for (int i = 0; i < members.length - 1; i++) {
            int big = i;
            for (int j = i + 1; j < members.length; j++) {
                if (distance(members[big].node, church) < distance(members[j].node, church)) big = j;
            }
            Peep.swap(members, i, big);
        }
        return members;
    }

    public static Peep.Driver getNearestDriver(Path path, Peep.Member member) {
        Peep.Driver driver = (Peep.Driver) path.drivers.down;
        Peep.Driver nearest = driver;
        double distance = Double.POSITIVE_INFINITY;
        double current;
        while (driver != null) {
            if ((current = distance(member.node, driver.node)) < distance) {
                distance = current;
                nearest = driver;
            }
            driver = (Peep.Driver) driver.down;
        }
        return nearest;
    }

    public static void chloe(Path path) {
        Peep.Member member = (Peep.Member) path.members.down;
        while (member != null) {
            if (!member.pref.equals("")) {
                Peep.Driver driver = (Peep.Driver) path.drivers.down;
                while (driver != null) {
                    if (member.pref.equals(path.profiles[driver.id].phone)) {
                        driver.ppl[--driver.seats] = member.id;
                        Peep.resolve(path.members, member);
                        Peep.remove(member.node.members, member);
                        if (driver.seats == 0) {
                            Peep.resolve(path.drivers, driver);
                            Peep.remove(driver.node.drivers, driver);
                        }
                        break;
                    }
                    driver = (Peep.Driver) driver.down;
                }
            }
            member = (Peep.Member) member.down;
        }
    }

    public static void leonard(Path path) {
        Node node = path.nodes.next;
        while (node != null) {
            if (node.drivers.next == null && node.members.next == null) {
                node = node.prev;
                remove(path.nodes, node.next);
            }
            node = node.next;
        }
    }

    public static Path nick(Path path, Peep.Member[] members) {
        path.weight = 0;
        for (Peep.Member peep : members) {
            Peep.Member member = (Peep.Member) path.profiles[peep.id].info;
            Peep.Driver driver = getNearestDriver(path, member);
            Node near = driver.node;
            Node here = member.node;
            path.weight += distance(near, here);
            driver.ppl[--driver.seats] = member.id;
            Peep.resolve(path.members, member);
            Peep.remove(member.node.members, member);
            if (driver.seats > 0) {
                Peep.remove(driver.node.drivers, driver);
                Peep.append(here.drivers, driver);
                driver.node = here;
            } else {
                path.weight += distance(here, path.nodes);
                Peep.remove(driver.node.drivers, driver);
                Peep.resolve(path.drivers, driver);
            }
        }

        Peep.Driver driver = (Peep.Driver) path.drivers.down;
        while (driver != null) {
            path.weight += distance(path.nodes, driver.node);
            driver = (Peep.Driver) driver.down;
        }
        return path;
    }
}
