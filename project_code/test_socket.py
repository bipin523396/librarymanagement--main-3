import socket
import ssl

hosts = [
    "ac-gf56gfz-shard-00-00.3f7teqs.mongodb.net",
    "ac-gf56gfz-shard-00-01.3f7teqs.mongodb.net",
    "ac-gf56gfz-shard-00-02.3f7teqs.mongodb.net"
]
port = 27017

for host in hosts:
    print(f"Testing raw TCP connection to {host}:{port}...")
    try:
        s = socket.create_connection((host, port), timeout=5)
        print(f"✅ Raw TCP connection to {host}:{port} succeeded!")
        s.close()
    except Exception as e:
        print(f"❌ Raw TCP connection to {host}:{port} failed: {e}")

    print(f"Testing SSL connection to {host}:{port}...")
    try:
        context = ssl.create_default_context()
        # You can try disabling certificate verification to see if that's the issue
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        s = socket.create_connection((host, port), timeout=5)
        ssl_sock = context.wrap_socket(s, server_hostname=host)
        print(f"✅ SSL handshake with {host}:{port} succeeded (certs ignored)!")
        ssl_sock.close()
    except Exception as e:
        print(f"❌ SSL handshake with {host}:{port} failed (certs ignored): {e}")
