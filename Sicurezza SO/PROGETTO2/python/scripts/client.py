import requests
 
def send_numbers(a, b, server_url="http://localhost:5000/sum"):
    payload = {
        "A": a,
        "B": b
    }
 
    try:
        response = requests.post(server_url, json=payload)
        response.raise_for_status() 
        data = response.json()
 
        print(f"Risultato ricevuto dal server: {data['A']} + {data['B']} = {data['sum']}")
        return data["sum"]
 
    except requests.exceptions.RequestException as e:
        print(f"Errore nella comunicazione con il server: {e}")
    except ValueError:
        print("Errore nella decodifica della risposta JSON.")
 
if __name__ == "__main__":
    send_numbers(7, 4)