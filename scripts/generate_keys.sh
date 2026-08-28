#!/usr/bin/env bash
set -euo pipefail

KEYS_DIR="keys"
PRIVATE_KEY="$KEYS_DIR/private.pem"
PUBLIC_KEY="$KEYS_DIR/public.pem"

mkdir -p "$KEYS_DIR"

if [[ -f "$PRIVATE_KEY" && -f "$PUBLIC_KEY" ]]; then
    echo "Keys already exist."
    exit 0
fi

if [[ -f "$PRIVATE_KEY" && ! -f "$PUBLIC_KEY" ]]; then
    echo "Generating missing public key..."
    openssl pkey -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"
    chmod 644 "$PUBLIC_KEY"
    exit 0
fi

if [[ ! -f "$PRIVATE_KEY" && -f "$PUBLIC_KEY" ]]; then
    echo "Public key exists but private key is missing."
    echo "Cannot recover the private key."
    exit 1
fi

echo "Generating new Ed25519 key pair..."
openssl genpkey -algorithm ed25519 -out "$PRIVATE_KEY"
openssl pkey -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"

chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"

echo "Done."