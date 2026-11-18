import socket
import sys

from router import create_packet


def main():
    if len(sys.argv) != 7:
        sys.exit(
            'Uso: python enviar.py IP_final puerto_final "mensaje" IP_envio puerto_envio TTL'
        )

    ip_final = sys.argv[1]
    try:
        puerto_final = int(sys.argv[2])
        puerto_envio = int(sys.argv[5])
        ttl = int(sys.argv[6])
    except ValueError:
        sys.exit("Los puertos y el TTL deben ser números enteros.")

    if not 1 <= ttl <= 255:
        sys.exit("El TTL inicial debe estar entre 1 y 255.")

    mensaje = sys.argv[3].encode("utf-8")
    ip_envio = sys.argv[4]
    paquete = create_packet({
        "ip": ip_final,
        "puerto": puerto_final,
        "ttl": ttl,
        "mensaje": mensaje,
    })

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as emisor:
        emisor.sendto(paquete, (ip_envio, puerto_envio))

    print(f"Paquete enviado a {ip_envio}:{puerto_envio} con destino final {ip_final}:{puerto_final}")


if __name__ == "__main__":
    main()
