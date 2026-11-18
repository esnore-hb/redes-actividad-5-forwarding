import socket
import sys


def parse_packet(IP_packet: bytes):
    if len(IP_packet) < 7:
        raise ValueError("El paquete debe contener al menos 7 bytes de header.")

    return {
        "ip": socket.inet_ntop(socket.AF_INET, IP_packet[:4]),
        "puerto": int.from_bytes(IP_packet[4:6], byteorder="big"),
        "ttl": IP_packet[6],
        "mensaje": IP_packet[7:],
    }


def create_packet(parsed_IP_packet):
    ip = socket.inet_pton(socket.AF_INET, parsed_IP_packet["ip"])
    puerto = parsed_IP_packet["puerto"].to_bytes(2, byteorder="big")
    ttl = parsed_IP_packet["ttl"].to_bytes(1, byteorder="big")
    return ip + puerto + ttl + parsed_IP_packet["mensaje"]


def ip_a_entero(ip: str) -> int:
    octetos = [int(numero) for numero in ip.split(".")]
    if len(octetos) != 4 or any(numero < 0 or numero > 255 for numero in octetos):
        raise ValueError("La dirección debe contener cuatro números entre 0 y 255.")
    return int.from_bytes(bytes(octetos), byteorder="big")


def check_routes(
    routes_file_name: str, destination_address: tuple[str, int], turnos: dict
) -> tuple[str, int] | None:
    ip_destino = ip_a_entero(destination_address[0])
    puerto_destino = destination_address[1]
    area_elegida = None
    opciones = []

    with open(routes_file_name, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue

            red, puerto_inicial, puerto_final, ip_siguiente, puerto_siguiente = linea.split()
            ip_red, prefijo = red.split("/")
            prefijo = int(prefijo)
            if not 0 <= prefijo <= 32:
                raise ValueError("El prefijo de red debe estar entre 0 y 32.")
            bits_host = 32 - prefijo
            # Quitamos los bits de host para comparar solo el prefijo de red.
            red = ip_a_entero(ip_red) >> bits_host
            area = (red, prefijo, int(puerto_inicial), int(puerto_final))
            if (
                ip_destino >> bits_host == red
                and area[2] <= puerto_destino <= area[3]
            ):
                if area_elegida is None:
                    area_elegida = area
                if area == area_elegida:
                    opciones.append((ip_siguiente, int(puerto_siguiente)))

    if not opciones:
        return None

    clave = (routes_file_name, area_elegida)
    turno = turnos.get(clave, 0) % len(opciones)
    turnos[clave] = (turno + 1) % len(opciones)
    return opciones[turno]


def main():
    if len(sys.argv) != 4:
        sys.exit("Uso: python router.py router_IP router_puerto router_rutas.txt")

    router_ip = sys.argv[1]
    try:
        router_puerto = int(sys.argv[2])
    except ValueError:
        sys.exit("El puerto debe ser un número entero.")

    rutas_archivo = sys.argv[3]
    turnos = {}

    print(f"IP del router: {router_ip}")
    print(f"Puerto del router: {router_puerto}")
    print(f"Archivo de rutas: {rutas_archivo}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as router_socket:
        router_socket.bind((router_ip, router_puerto))
        print(f"Esperando un paquete UDP en {router_ip}:{router_puerto}...", flush=True)
        while True:
            paquete, _ = router_socket.recvfrom(65535)
            campos = parse_packet(paquete)
            if campos["ttl"] == 0:
                print(f"Se recibió paquete {paquete!r} con TTL 0", flush=True)
                continue

            destino = (campos["ip"], campos["puerto"])
            direccion_actual = (router_ip, router_puerto)

            if destino == direccion_actual:
                print(campos["mensaje"].decode("utf-8"), flush=True)
                continue

            siguiente_salto = check_routes(rutas_archivo, destino, turnos)
            if siguiente_salto is None:
                print(f"No hay rutas hacia {destino} para paquete {paquete!r}", flush=True)
                continue

            campos["ttl"] -= 1
            paquete = create_packet(campos)
            router_socket.sendto(paquete, siguiente_salto)
            print(
                f"redirigiendo paquete {paquete!r} con destino final {destino} "
                f"desde {direccion_actual} hacia {siguiente_salto}",
                flush=True,
            )


if __name__ == "__main__":
    main()
