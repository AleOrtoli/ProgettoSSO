import requests
import base64
 
# URL server tuo
SERVER_URL = "http://localhost:5000"
# URL endpoint attestation service (sostituisci con quello reale)
ATTESTATION_SERVICE_URL = "https://attestationserver.neu.attest.azure.net/attest/SgxEnclave?api-version=2020-10-01"
 
def verify_quote(quote_b64):
    """
    Invia la quote al servizio di attestazione di Azure e ritorna True se è valida.
    """
    try:
        payload = {"quote": quote_b64}
        headers = {"Content-Type": "application/json"}
 
        response = requests.post(ATTESTATION_SERVICE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
 
        # ATTENZIONE: Azure non restituisce "is_valid". Analizza il JWT nella risposta se serve.
        print("Risposta dell'attestation service:", data)
 
        # Per ora, considera che se non c'è errore HTTP, la quote è accettata
        print("Quote verificata con successo.")
        return True
 
    except requests.exceptions.HTTPError as e:
        print(f"Errore HTTP: {e} - Risposta: {e.response.text}")
        return False
    except Exception as e:
        print(f"Errore nella verifica della quote: {e}")
        return False
 
def get_quote():
    """
    Richiede la quote dal server.
    """
    try:
        response = requests.post(f"{SERVER_URL}/quote")
        response.raise_for_status()
        data = response.json()
        quote_b64 = data.get("quote_base64")
        if not quote_b64:
            print("Quote mancante nella risposta.")
            return None
        return quote_b64
    except Exception as e:
        print(f"Errore nel recuperare la quote dal server: {e}")
        return None
 
def send_numbers(a, b):
    """
    Manda la richiesta di somma al server.
    """
    payload = {"A": a, "B": b}
    try:
        response = requests.post(f"{SERVER_URL}/sum", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Risultato ricevuto dal server: {data['A']} + {data['B']} = {data['sum']}")
        return data["sum"]
    except Exception as e:
        print(f"Errore nella comunicazione con il server: {e}")
        return None
 
if __name__ == "__main__":
    quote = get_quote()
    if quote is None:
        print("Non posso procedere senza la quote.")
        exit(1)
 
    if verify_quote(quote):
        send_numbers(7, 4)
    else:
        print("Verifica della quote fallita, abortisco.")