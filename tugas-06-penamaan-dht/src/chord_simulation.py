
import hashlib

M_BITS = 8
RING_SIZE = 2 ** M_BITS


def hash_id(key: str) -> int:
    """Hash string (ID node atau ID kurir) ke ruang identifier 0..RING_SIZE-1."""
    digest = hashlib.sha1(key.encode()).digest()
    return int.from_bytes(digest, "big") % RING_SIZE


class ChordRing:
    def __init__(self):
        # node_id (hasil hash) -> alamat IP node tersebut
        self.nodes: dict[int, str] = {}
        # key kurir (hasil hash) -> IP kurir yang disimpan node yang bertanggung jawab
        self.data: dict[int, tuple[str, str]] = {}  # hash -> (kurir_id, ip_kurir)

    def join(self, node_name: str, node_ip: str):
        """Tambahkan node baru ke ring. Pindahkan data yang seharusnya
        menjadi tanggung jawab node baru ini dari successor lamanya."""
        node_id = hash_id(node_name)

        old_successor = None

        if self.nodes:
            old_successor = self.find_successor(node_id)

        self.nodes[node_id] = node_ip

        if old_successor is not None:
            for key_hash, (kurir_id, ip_kurir) in list(self.data.items()):
                if self.find_successor(key_hash) == node_id:
                    print(
                        f"[JOIN] Mapping {kurir_id} -> {ip_kurir} "
                        f"berpindah dari node {old_successor} ke node {node_id}"
                    )

        print(f"[JOIN] Node '{node_name}' (id={node_id}) bergabung, alamat {node_ip}")

    def leave(self, node_name: str):
        """Keluarkan sebuah node dari ring. Data yang dipegangnya harus
        berpindah ke successor-nya."""
        node_id = hash_id(node_name)

        if node_id not in self.nodes:
            print(f"[LEAVE] Node '{node_name}' tidak ditemukan")
            return

        old_data = [
            (key_hash, kurir_id, ip_kurir)
            for key_hash, (kurir_id, ip_kurir) in self.data.items()
            if self.find_successor(key_hash) == node_id
        ]

        del self.nodes[node_id]

        if self.nodes:
            for key_hash, kurir_id, ip_kurir in old_data:
                new_successor = self.find_successor(key_hash)
                print(
                    f"[LEAVE] Mapping {kurir_id} -> {ip_kurir} "
                    f"berpindah ke node {new_successor}"
                )
        else:
            print("[LEAVE] Ring kosong, tidak ada node penerima")

        print(f"[LEAVE] Node '{node_name}' (id={node_id}) keluar dari ring")

    def find_successor(self, key_hash: int) -> int:
        """Cari node_id dengan nilai hash TERKECIL yang >= key_hash
        (successor menurut aturan Chord). Jika tidak ada, wrap-around
        ke node dengan hash terkecil di ring (karena ring melingkar)."""
        if not self.nodes:
            raise ValueError("Ring belum memiliki node")

        sorted_nodes = sorted(self.nodes.keys())

        for node_id in sorted_nodes:
            if node_id >= key_hash:
                return node_id

        return sorted_nodes[0]

    def register_kurir(self, kurir_id: str, ip_kurir: str):
        """Simpan mapping ID Kurir -> IP di node yang bertanggung jawab."""
        key_hash = hash_id(kurir_id)

        responsible_node = self.find_successor(key_hash)
        self.data[key_hash] = (kurir_id, ip_kurir)

        print(
            f"[REGISTER] {kurir_id} -> {ip_kurir} "
            f"disimpan di node {responsible_node}"
        )

    def lookup(self, kurir_id: str) -> str | None:
        """Cari alamat IP terkini untuk sebuah ID Kurir."""
        key_hash = hash_id(kurir_id)

        self.find_successor(key_hash)

        if key_hash in self.data:
            stored_kurir_id, ip_kurir = self.data[key_hash]

            if stored_kurir_id == kurir_id:
                return ip_kurir

        return None


def main():
    ring = ChordRing()

    # Skenario awal: 4 node bergabung
    ring.join("node-jakarta-1", "10.0.0.1")
    ring.join("node-jakarta-2", "10.0.0.2")
    ring.join("node-bandung-1", "10.0.0.3")
    ring.join("node-surabaya-1", "10.0.0.4")

    # Daftarkan beberapa kurir
    ring.register_kurir("kurir-001", "192.168.1.10")
    ring.register_kurir("kurir-002", "192.168.1.11")
    ring.register_kurir("kurir-003", "192.168.1.12")
    ring.register_kurir("kurir-004", "192.168.1.13")
    ring.register_kurir("kurir-005", "192.168.1.14")
    ring.register_kurir("kurir-009", "192.168.1.15")

    print("\n--- Lookup sebelum perubahan topologi ---")
    print("kurir-001 ->", ring.lookup("kurir-001"))
    print("kurir-002 ->", ring.lookup("kurir-002"))
    print("kurir-005 ->", ring.lookup("kurir-005"))
    print("kurir-009 ->", ring.lookup("kurir-009"))

    print("\n--- Node baru bergabung ---")
    ring.join("node-medan-1", "10.0.0.5")

    print("\n--- Node Jakarta-1 keluar ---")
    ring.leave("node-jakarta-1")

    print("\n--- Lookup setelah node keluar ---")
    print("kurir-001 ->", ring.lookup("kurir-001"))
    print("kurir-002 ->", ring.lookup("kurir-002"))
    print("kurir-003 ->", ring.lookup("kurir-003"))
    print("kurir-004 ->", ring.lookup("kurir-004"))
    print("kurir-005 ->", ring.lookup("kurir-005"))
    print("kurir-009 ->", ring.lookup("kurir-009"))


if __name__ == "__main__":
    main()
