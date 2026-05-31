from flask import Flask, request, render_template_string
import requests
from tsync import Thread  # Control de hilos para el reloj secundario
import time
from datetime import datetime
import pytz

app = Flask(__name__)

# CONFIGURACIÓN DE WHATSAPP INTEGRADA OFICIAL
NUMERO_TELEFONO = "34641408180"  
API_KEY_WHATSAPP = "1076941"
URL_WEB_INTERNET = ""  # Se rellenará automáticamente al desplegar

PLANTILLA = [
    {'nombre': 'Héctor Moreno', 'rol': 'A', 'nivel': 100, 'foto': 'hector_moreno.jpg'},
    {'nombre': 'Alexander Garrido', 'rol': 'A', 'nivel': 100, 'foto': 'alexander_garrido.jpg'},
    {'nombre': 'Yoel Garrido', 'rol': 'A', 'nivel': 100, 'foto': 'yoel_garrido.jpg'},
    {'nombre': 'Misael Sanchez', 'rol': 'C', 'nivel': 100, 'foto': 'misael_sanchez.jpg'},
    {'nombre': 'Lizet Sanchez', 'rol': 'C', 'nivel': 100, 'foto': 'lizet_sanchez.jpg'},
    {'nombre': 'Ivette Soles', 'rol': 'C', 'nivel': 90, 'foto': 'ivette_soles.jpg'},
    {'nombre': 'Rosmeri Soria', 'rol': 'C', 'nivel': 85, 'foto': 'rosmeri_soria.jpg'},
    {'nombre': 'Milagros Rojas', 'rol': 'R', 'nivel': 85, 'foto': 'milagros_rojas.jpg'},
    {'nombre': 'Ronald Salazar', 'rol': 'A', 'nivel': 85, 'foto': 'ronald_salazar.jpg'},
    {'nombre': 'Cleo Herrera', 'rol': 'C', 'nivel': 100, 'foto': 'cleo_herrera.jpg'},
    {'nombre': 'Luz Maria', 'rol': 'R', 'nivel': 85, 'foto': 'luz_maria.jpg'},
    {'nombre': 'Juan Pablo', 'rol': 'C', 'nivel': 100, 'foto': 'juan_pablo.jpg'},
    {'nombre': 'Tiago Piñero', 'rol': 'A', 'nivel': 100, 'foto': 'tiago_pinero.jpg'},
    {'nombre': 'Yared (tato) Racero', 'rol': 'A', 'nivel': 100, 'foto': 'yared_racero.jpg'},
    {'nombre': 'Alicia Navarro', 'rol': 'R', 'nivel': 65, 'foto': 'alicia_navarro.jpg'},
    {'nombre': 'Pedro Cajavilca', 'rol': 'R', 'nivel': 90, 'foto': 'pedro_cajavilca.jpg'},
    {'nombre': 'Sebastián Herrera', 'rol': 'A', 'nivel': 90, 'foto': 'sebastian_herrera.jpg'},
    {'nombre': 'Adhara', 'rol': 'R', 'nivel': 95, 'foto': 'adhara.jpg'},
    {'nombre': 'DEO', 'rol': 'A', 'nivel': 85, 'foto': 'deo.jpg'},
    {'nombre': 'Yael Chumpitaz', 'rol': 'R', 'nivel': 90, 'foto': 'yael_chumpitaz.jpg'}
]

asistentes_confirmados = list(PLANTILLA)  
equipos_resultado = {}

def calcular_y_balancear():
    total = len(asistentes_confirmados)
    if total == 0: return {}
    num_equipos = 3 if total >= 14 else 2
    equipos = {f"Equipo {i+1}": [] for i in range(num_equipos)}
    colocadores = [j for j in asistentes_confirmados if j['rol'] == 'C']
    atacantes = [j for j in asistentes_confirmados if j['rol'] == 'A']
    receptores = [j for j in asistentes_confirmados if j['rol'] == 'R']
    colocadores.sort(key=lambda x: x['nivel'], reverse=True)
    atacantes.sort(key=lambda x: x['nivel'], reverse=True)
    receptores.sort(key=lambda x: x['nivel'], reverse=True)
    for group in [colocadores, atacantes, receptores]:
        for jugador in group:
            equipo_optimo = min(equipos.keys(), key=lambda k: (len(equipos[k]), sum(j['nivel'] for j in equipos[k])))
            equipos[equipo_optimo].append(jugador)
    return equipos

def enviar_mensaje_directo(texto):
    if not API_KEY_WHATSAPP: return
    url = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO_TELEFONO}&text={texto}&apikey={API_KEY_WHATSAPP}"
    try: requests.get(url)
    except: print("Error enviando WhatsApp.")

def enviar_a_whatsapp(equipos):
    if not equipos: return
    mensaje = "🏐 *VOLEY BINACED MARTES DE 8 A 10PM* 🏐\n\n"
    for eq, jugadores in equipos.items():
        mensaje += f"*{eq}*:\n"
        for j in jugadores:
            mensaje += f"- *{j['nombre']}* ({j['rol']})\n"
        mensaje += "\n"
    mensaje += "¡A calentar duro en la pista! 🔥"
    enviar_mensaje_directo(mensaje)

# RELOJ AUTOMÁTICO EN SEGUNDO PLANO
def reloj_programador():
    global equipos_resultado, asistentes_confirmados
    zona_es = pytz.timezone('Europe/Madrid')
    
    # Esperar a que Render asigne la URL si está vacío
    time.sleep(10)
    
    while True:
        ahora = datetime.now(zona_es)
        dia_semana = ahora.weekday() # 6 = Domingo, 1 = Martes
        hora = ahora.hour
        minuto = ahora.minute
        
        # Domingo 6:00 PM (18:00) -> Enviar Convocatoria
        if dia_semana == 6 and hora == 18 and minuto == 0:
            asistentes_confirmados = [] # Vaciar para nueva convocatoria
            equipos_resultado = {}
            enlace = URL_WEB_INTERNET if URL_WEB_INTERNET else "la web de voley"
            msg = f"🏐 *CONVOCATORIA VOLEY BINACED* 🏐\n\nYa está lista la convocatoria para el martes. Por favor, entren en el siguiente enlace para confirmar su asistencia:\n👉 {enlace}\n\n¡No se queden fuera! 🏐"
            enviar_mensaje_directo(msg)
            time.sleep(60) # Evitar re-envíos en el mismo minuto
            
        # Martes 7:30 PM (19:30) -> Balancear y Cerrar
        elif dia_semana == 1 and hora == 19 and minuto == 30:
            equipos_resultado = calcular_y_balancear()
            enviar_a_whatsapp(equipos_resultado)
            time.sleep(60)
            
        time.sleep(30)

def cargar_vista():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return render_template_string(html_content, plantilla=PLANTILLA, asistentes=asistentes_confirmados, resultados=equipos_resultado)

@app.route('/')
def inicio():
    global URL_WEB_INTERNET
    if not URL_WEB_INTERNET:
        URL_WEB_INTERNET = request.host_url
    return cargar_vista()

@app.route('/apuntar_nombre', methods=['POST'])
def apuntar_nombre():
    nombre_seleccionado = request.form.get('nombre_jugador')
    jugador_datos = next((j for j in PLANTILLA if j['nombre'] == nombre_seleccionado), None)
    if jugador_datos and jugador_datos not in asistentes_confirmados:
        asistentes_confirmados.append(jugador_datos)
    return cargar_vista()

@app.route('/generar_manual', methods=['POST'])
def generar_manual():
    global equipos_resultado
    equipos_resultado = calcular_y_balancear()
    enviar_a_whatsapp(equipos_resultado)
    return cargar_vista()

@app.route('/limpiar', methods=['POST'])
def limpiar():
    global asistentes_confirmados, equipos_resultado
    asistentes_confirmados = []
    equipos_resultado = {}
    return cargar_vista()

if __name__ == '__main__':
    # Arrancar el hilo del reloj automático
    t = Thread(target=reloj_programador)
    t.daemon = True
    t.start()
    app.run(debug=True, port=8080)