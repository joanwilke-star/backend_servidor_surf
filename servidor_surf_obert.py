import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import time
from datetime import datetime

# Base de dades de ubicacions
spots_db = {
    "Andalusia": [
        {"nom": "El Palmar", "lat": 36.236, "lon": -6.071},
        {"nom": "Tarifa", "lat": 36.013, "lon": -5.606},
        {"nom": "Yerbabuena", "lat": 36.183, "lon": -5.992},
        {"nom": "Cabopino", "lat": 36.488, "lon": -4.744},
        {"nom": "Punta Umbria", "lat": 37.178, "lon": -6.966},
        {"nom": "Los Bateles", "lat": 36.273, "lon": -6.089},
        {"nom": "Canos de Meca", "lat": 36.182, "lon": -6.011},
        {"nom": "Cortadura", "lat": 36.494, "lon": -6.265},
        {"nom": "Mazagon", "lat": 37.135, "lon": -6.822},
        {"nom": "Santa Amalia", "lat": 36.536, "lon": -4.618}
    ],
    "Asturies": [
        {"nom": "Salinas", "lat": 43.578, "lon": -5.955},
        {"nom": "Rodiles", "lat": 43.533, "lon": -5.383},
        {"nom": "Xago", "lat": 43.611, "lon": -5.918},
        {"nom": "San Lorenzo", "lat": 43.543, "lon": -5.654},
        {"nom": "Playa Espana", "lat": 43.545, "lon": -5.597},
        {"nom": "Tapia", "lat": 43.571, "lon": -6.945},
        {"nom": "Penarronda", "lat": 43.554, "lon": -6.992},
        {"nom": "San Antolin", "lat": 43.438, "lon": -4.869},
        {"nom": "Vega", "lat": 43.486, "lon": -5.143},
        {"nom": "Frejulfe", "lat": 43.559, "lon": -6.658}
    ],
    "Canaries": [
        {"nom": "Famara", "lat": 29.116, "lon": -13.556},
        {"nom": "Las Americas", "lat": 28.058, "lon": -16.732},
        {"nom": "El Quemao", "lat": 29.117, "lon": -13.633},
        {"nom": "Los Lobos", "lat": 28.749, "lon": -13.818},
        {"nom": "El Confital", "lat": 28.163, "lon": -15.441},
        {"nom": "La Santa", "lat": 29.109, "lon": -13.651},
        {"nom": "El Socorro", "lat": 28.396, "lon": -16.602},
        {"nom": "Punta Blanca", "lat": 28.212, "lon": -16.836},
        {"nom": "Igueste", "lat": 28.536, "lon": -16.152},
        {"nom": "Bajamar", "lat": 28.556, "lon": -16.345}
    ],
    "Cantabria": [
        {"nom": "Somo", "lat": 43.454, "lon": -3.765},
        {"nom": "Los Locos", "lat": 43.435, "lon": -4.045},
        {"nom": "Laredo", "lat": 43.415, "lon": -3.432},
        {"nom": "Berria", "lat": 43.458, "lon": -3.468},
        {"nom": "Liencres", "lat": 43.468, "lon": -3.938},
        {"nom": "Meron", "lat": 43.391, "lon": -4.385},
        {"nom": "Santa Marina", "lat": 43.453, "lon": -3.738},
        {"nom": "Langre", "lat": 43.477, "lon": -3.702},
        {"nom": "Galizano", "lat": 43.481, "lon": -3.674},
        {"nom": "Suances", "lat": 43.437, "lon": -4.038}
    ],
    "Catalunya": [
        {"nom": "Barceloneta", "lat": 41.378, "lon": 2.192},
        {"nom": "Sitges", "lat": 41.233, "lon": 1.804},
        {"nom": "Masnou", "lat": 41.478, "lon": 2.313},
        {"nom": "Montgat", "lat": 41.464, "lon": 2.279},
        {"nom": "Castelldefels", "lat": 41.264, "lon": 1.993},
        {"nom": "Premia de Mar", "lat": 41.491, "lon": 2.359},
        {"nom": "Bogatell", "lat": 41.393, "lon": 2.207},
        {"nom": "Garraf", "lat": 41.253, "lon": 1.901},
        {"nom": "Riu Besos", "lat": 41.417, "lon": 2.232},
        {"nom": "Blanes", "lat": 41.673, "lon": 2.795}
    ],
    "Galicia": [
        {"nom": "Razo", "lat": 43.292, "lon": -8.705},
        {"nom": "Pantin", "lat": 43.638, "lon": -8.109},
        {"nom": "Doninos", "lat": 43.498, "lon": -8.318},
        {"nom": "A Lanzada", "lat": 42.433, "lon": -8.878},
        {"nom": "Patos", "lat": 42.146, "lon": -8.824},
        {"nom": "Nemina", "lat": 43.013, "lon": -9.231},
        {"nom": "Sabon", "lat": 43.328, "lon": -8.504},
        {"nom": "Bastiagueiro", "lat": 43.344, "lon": -8.349},
        {"nom": "Soesto", "lat": 43.208, "lon": -9.022},
        {"nom": "Rio Sieira", "lat": 42.648, "lon": -9.034}
    ],
    "Pais_Basc": [
        {"nom": "Mundaka", "lat": 43.407, "lon": -2.697},
        {"nom": "Zarautz", "lat": 43.285, "lon": -2.164},
        {"nom": "Sopelana", "lat": 43.388, "lon": -2.996},
        {"nom": "Bakio", "lat": 43.428, "lon": -2.808},
        {"nom": "Zurriola", "lat": 43.326, "lon": -1.975},
        {"nom": "Menakoz", "lat": 43.395, "lon": -2.984},
        {"nom": "Laga", "lat": 43.411, "lon": -2.651},
        {"nom": "Karraspio", "lat": 43.366, "lon": -2.497},
        {"nom": "Orrua", "lat": 43.303, "lon": -2.224},
        {"nom": "Playa Gris", "lat": 43.305, "lon": -2.235}
    ]
}


def calcular_top_5_comunitat(comunitat):
    hora_actual = datetime.now().hour
    resultats = []
    
    llista_spots = spots_db.get(comunitat, spots_db["Cantabria"])
    
    print(f"\n[{comunitat}] Calculant el Top 5 per a les próximes 24h...")
    
    for spot in llista_spots:
        url = f"https://marine-api.open-meteo.com/v1/marine?latitude={spot['lat']}&longitude={spot['lon']}&hourly=wave_height,wave_period,sea_surface_temperature&forecast_days=2&timezone=Europe/Berlin"
        
        # Sistema per reintentar quan no funciona
        exito = False
        intents = 0
        
        while not exito and intents < 3:
            try:
                resposta = requests.get(url, timeout=5).json()
                millor_onada_spot = 0.0
                previsio_spot = []
                
                for i in range(hora_actual, hora_actual + 24):
                    onada = resposta["hourly"]["wave_height"][i]
                    if onada > millor_onada_spot:
                        millor_onada_spot = onada
                        
                    temps_treure_format_dia = resposta["hourly"]["time"][i]
                    dia = int(temps_treure_format_dia[8:10])
                    mes = int(temps_treure_format_dia[5:7])
                    
                    previsio_spot.append({
                        "data": f"{dia}/{mes}",
                        "hora": temps_treure_format_dia[11:16],
                        "onada": onada,
                        "periode": resposta["hourly"]["wave_period"][i],
                        "temp": resposta["hourly"]["sea_surface_temperature"][i]
                    })
                    
                resultats.append({
                    "nom": spot["nom"],
                    "max_onada": millor_onada_spot,
                    "previsio": previsio_spot
                })
                exito = True 
                
            except Exception as e:
                intents += 1
                print(f"  -> Error llegint {spot['nom']} (Intent {intents}/3). Reintentant...")
                time.sleep(1) 
                
        time.sleep(0.2)
        
    resultats.sort(key=lambda x: x["max_onada"], reverse=True)
    top_5 = resultats[:5]
    
    csv_final = ""
    for index, spot in enumerate(top_5):
        csv_final += f"{spot['nom']}\n"
        for p in spot['previsio']:
            csv_final += f"{p['data']},{p['hora']},{p['onada']},{p['periode']},{p['temp']}\n"
        if index < len(top_5) - 1:
            csv_final += "---\n" 
            
    print(f"Calculant el Top 5.")
    return csv_final


class Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        regio = query.get('regio', ['Cantabria'])[0] 
        
        print(f"\n--> Arduino ha sol·licitat dades de: {regio}")
        csv_data = calcular_top_5_comunitat(regio)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(csv_data.encode('utf-8'))
#Unic canvi del codi tancat al codi obert. eliminem la funcio Obtenir_ip que ja no es necesari 
if __name__ == '__main__':
    # Llegim el port de la variable d'entorn que assigna el servidor (per defecte 8080 si ho corres en local)
    puerto = int(os.environ.get('PORT', 8080))
    
    print("="*50)
    print(f"Servidor iniciat (Port dinàmic: {puerto})")
    print("="*50)
    
    servidor = HTTPServer(('0.0.0.0', puerto), Manejador)
    servidor.serve_forever()
