import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import time
from datetime import datetime

# --- SÚPER BASE DE DATOS DE SURF POR COMUNIDADES ---
spots_db = {
    "Andalucia": [
        {"nombre": "El Palmar", "lat": 36.236, "lon": -6.071},
        {"nombre": "Tarifa", "lat": 36.013, "lon": -5.606},
        {"nombre": "Yerbabuena", "lat": 36.183, "lon": -5.992},
        {"nombre": "Cabopino", "lat": 36.488, "lon": -4.744},
        {"nombre": "Punta Umbria", "lat": 37.178, "lon": -6.966},
        {"nombre": "Los Bateles", "lat": 36.273, "lon": -6.089},
        {"nombre": "Canos de Meca", "lat": 36.182, "lon": -6.011},
        {"nombre": "Cortadura", "lat": 36.494, "lon": -6.265},
        {"nombre": "Mazagon", "lat": 37.135, "lon": -6.822},
        {"nombre": "Santa Amalia", "lat": 36.536, "lon": -4.618}
    ],
    "Asturias": [
        {"nombre": "Salinas", "lat": 43.578, "lon": -5.955},
        {"nombre": "Rodiles", "lat": 43.533, "lon": -5.383},
        {"nombre": "Xago", "lat": 43.611, "lon": -5.918},
        {"nombre": "San Lorenzo", "lat": 43.543, "lon": -5.654},
        {"nombre": "Playa Espana", "lat": 43.545, "lon": -5.597},
        {"nombre": "Tapia", "lat": 43.571, "lon": -6.945},
        {"nombre": "Penarronda", "lat": 43.554, "lon": -6.992},
        {"nombre": "San Antolin", "lat": 43.438, "lon": -4.869},
        {"nombre": "Vega", "lat": 43.486, "lon": -5.143},
        {"nombre": "Frejulfe", "lat": 43.559, "lon": -6.658}
    ],
    "Canarias": [
        {"nombre": "Famara", "lat": 29.116, "lon": -13.556},
        {"nombre": "Las Americas", "lat": 28.058, "lon": -16.732},
        {"nombre": "El Quemao", "lat": 29.117, "lon": -13.633},
        {"nombre": "Los Lobos", "lat": 28.749, "lon": -13.818},
        {"nombre": "El Confital", "lat": 28.163, "lon": -15.441},
        {"nombre": "La Santa", "lat": 29.109, "lon": -13.651},
        {"nombre": "El Socorro", "lat": 28.396, "lon": -16.602},
        {"nombre": "Punta Blanca", "lat": 28.212, "lon": -16.836},
        {"nombre": "Igueste", "lat": 28.536, "lon": -16.152},
        {"nombre": "Bajamar", "lat": 28.556, "lon": -16.345}
    ],
    "Cantabria": [
        {"nombre": "Somo", "lat": 43.454, "lon": -3.765},
        {"nombre": "Los Locos", "lat": 43.435, "lon": -4.045},
        {"nombre": "Laredo", "lat": 43.415, "lon": -3.432},
        {"nombre": "Berria", "lat": 43.458, "lon": -3.468},
        {"nombre": "Liencres", "lat": 43.468, "lon": -3.938},
        {"nombre": "Meron", "lat": 43.391, "lon": -4.385},
        {"nombre": "Santa Marina", "lat": 43.453, "lon": -3.738},
        {"nombre": "Langre", "lat": 43.477, "lon": -3.702},
        {"nombre": "Galizano", "lat": 43.481, "lon": -3.674},
        {"nombre": "Suances", "lat": 43.437, "lon": -4.038}
    ],
    "Cataluna": [
        {"nombre": "Barceloneta", "lat": 41.378, "lon": 2.192},
        {"nombre": "Sitges", "lat": 41.233, "lon": 1.804},
        {"nombre": "Masnou", "lat": 41.478, "lon": 2.313},
        {"nombre": "Montgat", "lat": 41.464, "lon": 2.279},
        {"nombre": "Castelldefels", "lat": 41.264, "lon": 1.993},
        {"nombre": "Premia de Mar", "lat": 41.491, "lon": 2.359},
        {"nombre": "Bogatell", "lat": 41.393, "lon": 2.207},
        {"nombre": "Garraf", "lat": 41.253, "lon": 1.901},
        {"nombre": "Rio Besos", "lat": 41.417, "lon": 2.232},
        {"nombre": "Blanes", "lat": 41.673, "lon": 2.795}
    ],
    "Galicia": [
        {"nombre": "Razo", "lat": 43.292, "lon": -8.705},
        {"nombre": "Pantin", "lat": 43.638, "lon": -8.109},
        {"nombre": "Doninos", "lat": 43.498, "lon": -8.318},
        {"nombre": "A Lanzada", "lat": 42.433, "lon": -8.878},
        {"nombre": "Patos", "lat": 42.146, "lon": -8.824},
        {"nombre": "Nemina", "lat": 43.013, "lon": -9.231},
        {"nombre": "Sabon", "lat": 43.328, "lon": -8.504},
        {"nombre": "Bastiagueiro", "lat": 43.344, "lon": -8.349},
        {"nombre": "Soesto", "lat": 43.208, "lon": -9.022},
        {"nombre": "Rio Sieira", "lat": 42.648, "lon": -9.034}
    ],
    "Pais_Vasco": [
        {"nombre": "Mundaka", "lat": 43.407, "lon": -2.697},
        {"nombre": "Zarautz", "lat": 43.285, "lon": -2.164},
        {"nombre": "Sopelana", "lat": 43.388, "lon": -2.996},
        {"nombre": "Bakio", "lat": 43.428, "lon": -2.808},
        {"nombre": "Zurriola", "lat": 43.326, "lon": -1.975},
        {"nombre": "Menakoz", "lat": 43.395, "lon": -2.984},
        {"nombre": "Laga", "lat": 43.411, "lon": -2.651},
        {"nombre": "Karraspio", "lat": 43.366, "lon": -2.497},
        {"nombre": "Orrua", "lat": 43.303, "lon": -2.224},
        {"nombre": "Playa Gris", "lat": 43.305, "lon": -2.235}
    ]
}

def grados_a_rosa(grados):
    if grados is None: return "--"
    direcciones = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]
    idx = int(round(grados / 22.5)) % 16
    return direcciones[idx]

def calcular_top_5_comunidad(comunidad):
    hora_actual = datetime.now().hour
    resultados = []
    lista_spots = spots_db.get(comunidad, spots_db["Cantabria"])
    
    print(f"\n[{comunidad}] Calculando el Top 5...")
    
    for spot in lista_spots:
        # URL 1: Intentamos conseguir absolutamente todo (Mareas incluidas)
        url_completa = f"https://marine-api.open-meteo.com/v1/marine?latitude={spot['lat']}&longitude={spot['lon']}&hourly=wave_height,wave_period,sea_surface_temperature,wave_direction,sea_level&forecast_days=2&timezone=Europe/Berlin"
        
        # URL 2: El Plan B por si esta playa no tiene boyas de marea
        url_segura = f"https://marine-api.open-meteo.com/v1/marine?latitude={spot['lat']}&longitude={spot['lon']}&hourly=wave_height,wave_period,sea_surface_temperature,wave_direction&forecast_days=2&timezone=Europe/Berlin"
        
        try:
            # Pedimos los datos y cruzamos los dedos
            req = requests.get(url_completa, timeout=3)
            respuesta_json = {}
            
            # ¡Si Open-Meteo se enfada por la marea, activamos el Plan B!
            if req.status_code != 200:
                print(f"⚠️ Playa {spot['nombre']} sin datos de marea. Usando Plan B...")
                req_b = requests.get(url_segura, timeout=3)
                if req_b.status_code == 200:
                    respuesta_json = req_b.json()
                else:
                    continue # Si falla hasta el Plan B, saltamos a la siguiente playa
            else:
                respuesta_json = req.json()

            # --- PROCESAMOS LOS DATOS ---
            mejor_ola_spot = 0.0
            prevision_spot = []
            
            for i in range(hora_actual, hora_actual + 24):
                ola = respuesta_json["hourly"]["wave_height"][i]
                if ola is None: ola = 0.0 # Por si la API devuelve un vacío
                if ola > mejor_ola_spot:
                    mejor_ola_spot = ola
                    
                tiempo_crudo = respuesta_json["hourly"]["time"][i]
                dia = int(tiempo_crudo[8:10])
                mes = int(tiempo_crudo[5:7])
                
                # Leemos la dirección con seguridad
                dir_grados = respuesta_json["hourly"]["wave_direction"][i]
                dir_texto = grados_a_rosa(dir_grados)
                
                # Leemos la marea (o ponemos "--" si tuvimos que usar el Plan B)
                marea = "--"
                if "sea_level" in respuesta_json["hourly"]:
                    dato_marea = respuesta_json["hourly"]["sea_level"][i]
                    if dato_marea is not None:
                        marea = f"{dato_marea:.2f}"
                
                prevision_spot.append({
                    "fecha": f"{dia}/{mes}",
                    "hora": tiempo_crudo[11:16],
                    "ola": ola,
                    "periodo": respuesta_json["hourly"]["wave_period"][i],
                    "temp": respuesta_json["hourly"]["sea_surface_temperature"][i],
                    "direccion": dir_texto,
                    "marea": marea
                })
                
            resultados.append({
                "nombre": spot["nombre"],
                "max_ola": mejor_ola_spot,
                "prevision": prevision_spot
            })
            
        except Exception as e:
            print(f"  -> Timeout en {spot['nombre']}. Saltando.")
            
    # Ordenar y coger el Top 5
    resultados.sort(key=lambda x: x["max_ola"], reverse=True)
    top_5 = resultados[:5]
    
    csv_final = ""
    for index, spot in enumerate(top_5):
        csv_final += f"{spot['nombre']}\n"
        for p in spot['prevision']:
            csv_final += f"{p['fecha']},{p['hora']},{p['ola']},{p['periodo']},{p['temp']},{p['direccion']},{p['marea']}\n"
        if index < len(top_5) - 1:
            csv_final += "---\n" 
            
    print(f"✅ Top 5 calculado con éxito.")
    return csv_final

class Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        region = query.get('region', ['Cantabria'])[0] 
        
        print(f"\n--> Petición recibida: {region}")
        csv_data = calcular_top_5_comunidad(region)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(csv_data.encode('utf-8'))

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8080))
    print("="*50)
    print(f"🌍 SERVIDOR ANTI-BALAS INICIADO EN PUERTO {puerto}")
    print("="*50)
    servidor = HTTPServer(('0.0.0.0', puerto), Manejador)
    servidor.serve_forever()
