import socket
import sys

from router import create_packet


def main():
    if len(sys.argv) not in (4, 5):
        sys.exit(
            'Uso: python prueba_router.py "IP_final;puerto_final;TTL" '
            'IP_router_inicial puerto_router_inicial [archivo]'
        )

    try:
        ip_final, puerto_final, ttl = sys.argv[1].split(";")
        puerto_final = int(puerto_final)
        ttl = int(ttl)
        puerto_inicial = int(sys.argv[3])
    except ValueError:
        sys.exit("Headers esperados: IP;puerto;TTL, con puerto y TTL enteros.")

    if not 1 <= ttl <= 255:
        sys.exit("El TTL inicial debe estar entre 1 y 255.")

    archivo = sys.argv[4] if len(sys.argv) == 5 else "mensajes.txt"
    cantidad = 0
    with open(archivo, encoding="utf-8") as lineas:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as emisor:
            for linea in lineas:
                paquete = create_packet({
                    "ip": ip_final,
                    "puerto": puerto_final,
                    "ttl": ttl,
                    "mensaje": linea.rstrip("\r\n").encode("utf-8"),
                })
                emisor.sendto(paquete, (sys.argv[2], puerto_inicial))
                cantidad += 1

    print(f"Se enviaron {cantidad} paquetes desde {archivo}.")


if __name__ == "__main__":
    main()
