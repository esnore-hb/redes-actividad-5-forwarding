import ipaddress
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


def check_routes(
    routes_file_name: str, destination_address: tuple[str, int]
) -> tuple[str, int] | None:
    ip_destino = ipaddress.ip_address(destination_address[0])
    puerto_destino = destination_address[1]

    with open(routes_file_name, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue

            red, puerto_inicial, puerto_final, ip_siguiente, puerto_siguiente = linea.split()
            if (
                ip_destino in ipaddress.ip_network(red, strict=False)
                and int(puerto_inicial) <= puerto_destino <= int(puerto_final)
            ):
                return ip_siguiente, int(puerto_siguiente)

    return None


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
        while True:
            paquete, _ = router_socket.recvfrom(65535)
            campos = parse_packet(paquete)
            destino = (campos["ip"], campos["puerto"])
            direccion_actual = (router_ip, router_puerto)

            if destino == direccion_actual:
                print(campos["mensaje"].decode("utf-8"), flush=True)
                continue

            siguiente_salto = check_routes(rutas_archivo, destino)
            if siguiente_salto is None:
                print(f"No hay rutas hacia {destino} para paquete {paquete!r}", flush=True)
                continue

            router_socket.sendto(paquete, siguiente_salto)
            print(
                f"redirigiendo paquete {paquete!r} con destino final {destino} "
                f"desde {direccion_actual} hacia {siguiente_salto}",
                flush=True,
            )


if __name__ == "__main__":
    main()
