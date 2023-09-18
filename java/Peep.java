/*
https://youtu.be/B9kaCSay20Q
May 2023
*/

public class Peep {
    int id;
    Path.Node node;
    Peep next;
    Peep prev;
    Peep down;
    Peep up;

    public Peep() {}
    public Peep(int id) { this.id = id; }

    public static class Member extends Peep {
        String pref;

        public Member () {}
        public Member(int id, String pref) {
            super(id);
            this.pref = pref;
        }
    }

    public static class Driver extends Peep {
        int seats;
        int[] ppl;

        public Driver() {}
        public Driver(int id, int seats) {
            super(id);
            this.seats = seats;
            this.ppl = new int[seats];
            for (int i = 0; i < seats; i++) this.ppl[i] = -1;
        }
    }

    public static void conceive(Peep head, Peep now) {
        head.up.down = now;
        now.up = head.up;
        head.up = now;
    }

    public static void resolve(Peep head, Peep now) {
        if (now.down != null) {
            now.up.down = now.down;
            now.down.up = now.up;
        } else {
            head.up = now.up;
            now.up.down = null;
        }
    }

    public static void append(Peep head, Peep now) {
        head.prev.next = now;
        now.prev = head.prev;
        head.prev = now;
    }

    public static void remove(Peep head, Peep now) {
        if (now.next != null) {
            now.prev.next = now.next;
            now.next.prev = now.prev;
        } else {
            head.prev = now.prev;
            now.prev.next = null;
        }
    }

    public static void swap(Peep[] peeps, int i, int j) {
        Peep hold = peeps[i];
        peeps[i] = peeps[j];
        peeps[j] = hold;
    }

    public static int number(Peep peep) {
        int n = 0;
        while (peep.down != null) {
            n++;
            peep = peep.down;
        }
        return n;
    }

    public static Member copyMemberIDs(Path path) {
        Member head = new Member();
        head.up = head;
        Member member = (Member) path.members.down;
        while (member != null) {
            Member current = new Member(member.id, null);
            conceive(head, current);
            member = (Member) member.down;
        }
        return head;
    }

    public static Member[] copyMemberArray(Member[] members) {
        Member[] copies = new Member[members.length];
        for (int i = 0; i < copies.length; i++) copies[i] = new Member(members[i].id, members[i].pref);
        return copies;
    }
}
