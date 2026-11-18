import socket
import sys


def parse_packet(IP_packet: bytes):
    if len(IP_packet) < 6:
        raise ValueError("El paquete debe contener al menos 6 bytes de header.")

    return {
        "ip": socket.inet_ntop(socket.AF_INET, IP_packet[:4]),
        "puerto": int.from_bytes(IP_packet[4:6], byteorder="big"),
        "mensaje": IP_packet[6:],
    }


def create_packet(parsed_IP_packet):
    ip = socket.inet_pton(socket.AF_INET, parsed_IP_packet["ip"])
    puerto = parsed_IP_packet["puerto"].to_bytes(2, byteorder="big")
    return ip + puerto + parsed_IP_packet["mensaje"]


def main():
    if len(sys.argv) != 4:
        sys.exit("Uso: python router.py router_IP router_puerto router_rutas.txt")

    router_ip = sys.argv[1]
    try:
        router_puerto = int(sys.argv[2])
    except ValueError:
        sys.exit("El puerto debe ser un número entero.")

    rutas_archivo = sys.argv[3]

    print(f"IP del router: {router_ip}")
    print(f"Puerto del router: {router_puerto}")
    print(f"Archivo de rutas: {rutas_archivo}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as router_socket:
        router_socket.bind((router_ip, router_puerto))
        print(f"Esperando un paquete UDP en {router_ip}:{router_puerto}...", flush=True)
        paquete, remitente = router_socket.recvfrom(65535)
        print(f"Paquete recibido de {remitente}: {paquete!r}")


if __name__ == "__main__":
    main()
