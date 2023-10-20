import oqs


kemalg = "Kyber512"
with oqs.KeyEncapsulation(kemalg) as client:
    client_public_key = client.generate_keypair()
    client_secret_key = client.export_secret_key()
    