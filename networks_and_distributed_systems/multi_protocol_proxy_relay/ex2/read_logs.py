from sys import argv, exit
from base64 import b64decode
from ast import literal_eval

def read_log_file(filename):
    """Lire toutes les entrées de log depuis le fichier"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        print("Fichier non trouvé!")
        return []
    except Exception as e:
        print(f"Erreur de lecture: {e}")
        return []

def view_all_logs(entries):
    """Afficher tous les logs avec les données encodées en base64"""
    print(f"\n=== Tous les logs ({len(entries)} entrées) ===")
    for i, entry in enumerate(entries):
        try:
            log_data = literal_eval(entry)

            print(f"\n--- Entrée {i} ---")
            print(f"Timestamp: {log_data.get('timestamp', 'N/A')}")
            print(f"client: {log_data.get('client', 'N/A')}")
            print(f"URL serveur: {log_data.get('server url', 'N/A')}")
            print(f"Port serveur: {log_data.get('server port', 'N/A')}")
            print(f"URI: {log_data.get('uri', 'N/A')}")
            print(f"Données client (base64): {log_data.get('raw_base64_client', '')[:50]}...")
            if 'raw_base64_server' in log_data:
                print(f"Données serveur (base64): {log_data.get('raw_base64_server', '')[:50]}...")
        except Exception as e:
            print(f"\n--- Entrée {i} (format invalide: {e}) ---")
            print(entry[:100] + "...")


def search_server_url(entries):
    """Recherche par URL serveur"""
    terme = input("Entrez le terme de recherche pour l'URL serveur: ").strip()
    print(f"\n=== Recherche URL serveur: '{terme}' ===")
    found = False
    for i, entry in enumerate(entries):
        try:
            log_data = literal_eval(entry)
            server_url = log_data.get('server url', '')
            if terme.lower() in str(server_url).lower():
                print(f"\n--- Entrée {i} ---")
                print(f"URL serveur: {server_url}")
                print(f"URL client: {log_data.get('client url', 'N/A')}")
                print(f"Timestamp: {log_data.get('timestamp', 'N/A')}")
                found = True
        except:
            continue
    if not found:
        print("Aucun résultat trouvé.")

def search_uri(entries):
    """Recherche par URI"""
    terme = input("Entrez le terme de recherche pour l'URI: ").strip()
    print(f"\n=== Recherche URI: '{terme}' ===")
    found = False
    for i, entry in enumerate(entries):
        try:
            log_data = literal_eval(entry)
            uri = log_data.get('uri', '')
            if terme.lower() in uri.lower():
                print(f"\n--- Entrée {i} ---")
                print(f"URI: {uri}")
                print(f"URL client: {log_data.get('client url', 'N/A')}")
                print(f"URL serveur: {log_data.get('server url', 'N/A')}")
                found = True
        except:
            continue
    if not found:
        print("Aucun résultat trouvé.")

def decode_entry(entries):
    """Décoder une entrée spécifique par index"""
    try:
        index = int(input("Entrez l'index de l'entrée à décoder: ").strip())
        if index < 0 or index >= len(entries):
            print(f"Index invalide. Doit être entre 0 et {len(entries)-1}")
            return
        
        entry = entries[index]
        log_data = literal_eval(entry)
        
        print(f"\n=== Entrée {index} décodée ===")
        print(f"Timestamp: {log_data.get('timestamp', 'N/A')}")
        print(f"URL client: {log_data.get('client url', 'N/A')}")
        print(f"URL serveur: {log_data.get('server url', 'N/A')}")
        print(f"URI: {log_data.get('uri', 'N/A')}")
        
        # Doder les données client
        client_b64 = log_data.get('raw_base64_client', '')
        if client_b64:
            print(f"\n--- Données client décodées ---")
            try:
                client_data = b64decode(client_b64)
                print(client_data.decode('utf-8'))
            except Exception as e:
                print(f"Erreur décodage client: {e}")
        
        # Décoder les données serveur
        server_b64 = log_data.get('raw_base64_server', '')
        if server_b64:
            print(f"\n--- Données serveur décodées ---")
            try:
                server_data = b64decode(server_b64)
                print(server_data.decode('utf-8'))
            except Exception as e:
                print(f"Erreur décodage serveur: {e}")
                
    except ValueError:
        print("Veuillez entrer un nombre valide.")
    except Exception as e:
        print(f"Erreur lors du décodage: {e}")

def main():
    if len(argv) != 2:
        print("Usage: python3 read_logs.py <fichier_log>")
        exit(1)
    
    filename = argv[1]
    entries = read_log_file(filename)
    
    if not entries:
        print("Aucune entrée trouvée dans le fichier.")
        return
    
    while True:
        print("\n" + "="*50)
        print("Que voulez-vous faire ?")
        print("1. Afficher tous les logs (données encodées en base64)")
        print("2. Rechercher par URL serveur") 
        print("3. Rechercher par URI")
        print("4. Décoder une entrée spécifique")
        print("5. Quitter")
        
        choix = input("\nVotre choix (1-5): ").strip()
        
        if choix == '1':
            view_all_logs(entries)
        elif choix == '2':
            search_server_url(entries)
        elif choix == '3':
            search_uri(entries)
        elif choix == '4':
            decode_entry(entries)
        elif choix == '5':
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez choisir entre 1 et 5.")

if __name__ == "__main__":
    main()
