#!/usr/bin/env bash
#!/usr/bin/env python3

# Copyright (C) 2023 Gramine contributors
# SPDX-License-Identifier: BSD-3-Clause
set -e

if test -n "$SGX"
then
    GRAMINE=gramine-sgx
else
    GRAMINE=gramine-sgx
fi

# === Build e firma ===
echo "[+] Pulizia..."
make clean

echo "[+] Compilazione manifest..."
make

echo "[+] Firma manifest..."
gramine-sgx-sign -m python.manifest -o python.manifest.sgx

# === running server ===
echo -e "\n\nRunning Server.py:"
$GRAMINE ./python scripts/server.py > OUTPUT
grep -q "Server" OUTPUT && echo "[ Success 1/2 ]"


#
# === SGX quote ===
#if test -n "$SGX"
#then
 #   $GRAMINE ./python scripts/sgx-report.py > OUTPUT
  #  grep -q "Generated SGX report" OUTPUT && echo "[ Success SGX report ]"
   # rm OUTPUT

   # $GRAMINE ./python scripts/sgx-quote.py > OUTPUT
   # grep -q "Extracted SGX quote" OUTPUT && echo "[ Success SGX quote ]"
   # rm OUTPUT
#fi