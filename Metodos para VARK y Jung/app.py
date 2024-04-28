from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from models.model import Database, Perfil, Pregunta, OpcionRespuesta, RespuestaVark, ResultadoVark, Puesto
from models.model import PreguntasJung,PuntosTotalesSeccion,ComparacionSecciones,CategoriaPerfil
from sqlalchemy import func
app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Clave secreta para usar flash en Flask

# Obtener instancia de la base de datos
db = Database.get_instance()
session_db = db.get_session()

# Obtener preguntas y opciones de la base de datos
preguntas = session_db.query(Pregunta).all()

# Tabla VARK
tabla = [
    {"#": 1, "V": "b", "A": "a", "R": "c", "K": "d"},
    {"#": 2, "V": "b", "A": "a", "R": "a", "K": "b"},
    {"#": 3, "V": "c", "A": "d", "R": "c", "K": "a"},
    {"#": 4, "V": "c", "A": "a", "R": "b", "K": "a"},
    {"#": 5, "V": "d", "A": "c", "R": "b", "K": "a"},
    {"#": 6, "V": "b", "A": "d", "R": "c", "K": "a"},
    {"#": 7, "V": "d", "A": "b", "R": "c", "K": "c"},
    {"#": 8, "V": "d", "A": "d", "R": "a", "K": "c"},
    {"#": 9, "V": "a", "A": "b", "R": "d", "K": "c"},
    {"#": 10, "V": "b", "A": "b", "R": "c", "K": "d"},
    {"#": 11, "V": "d", "A": "c", "R": "b", "K": "a"},
    {"#": 12, "V": "c", "A": "a", "R": "b", "K": "d"},
    {"#": 13, "V": "d", "A": "c", "R": "b", "K": "a"},
    {"#": 14, "V": "c", "A": "d", "R": "b", "K": "a"},
    {"#": 15, "V": "d", "A": "c", "R": "a", "K": "b"},
    {"#": 16, "V": "d", "A": "c", "R": "a", "K": "b"}
]

pregunta_index = 0
id_persona = None

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/')
def index():
    return redirect(url_for('registrar_perfil'))

# Ruta para registrar un perfil
@app.route('/registrar_perfil', methods=['GET', 'POST'])
def registrar_perfil():
    global id_persona
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        telefono = request.form['telefono']
        correo = request.form['correo']
        id_puesto = int(request.form['id_puesto'])

        nuevo_perfil = Perfil(nombre=nombre, 
                              apellidoPaterno=apellido_paterno, 
                              apellidoMaterno=apellido_materno, 
                              telefono=telefono, 
                              correo_electronico=correo, 
                              id_puesto=id_puesto)
        session_db.add(nuevo_perfil)
        session_db.commit()
        
        # Capturar el id del nuevo perfil
        id_persona = nuevo_perfil.id_perfil
        
        flash('Perfil registrado correctamente', 'success')
        return redirect(url_for('menu_cuestionario', id_perfil=nuevo_perfil.id_perfil))
    else:
        puestos = session_db.query(Puesto).all()
        return render_template('registrar_perfil.html', puestos=puestos)


# Ruta para el menú de opciones del cuestionario
@app.route('/menu_cuestionario/<int:id_perfil>')
def menu_cuestionario(id_perfil):
    perfil = session_db.query(Perfil).filter_by(id_perfil=id_perfil).first()
    return render_template('menu_cuestionario.html', perfil=perfil)

@app.route('/mostrar_siguiente_pregunta')
def mostrar_siguiente_pregunta():
    global pregunta_index

    if pregunta_index < len(preguntas):
        pregunta = preguntas[pregunta_index]
        opciones_pregunta = [opcion for opcion in pregunta.opciones]
        pregunta_index += 1
        return render_template('pregunta.html', pregunta=pregunta, opciones=opciones_pregunta)
    else:
        return redirect(url_for('calcular_perfil'))

@app.route('/guardar_respuesta', methods=['POST'])
def guardar_respuesta():
    global pregunta_index, id_persona
    respuesta = request.form['opcion']
    guardar_respuesta_db(preguntas[pregunta_index - 1].id_pregunta, respuesta, id_persona)
    return redirect(url_for('mostrar_siguiente_pregunta'))

def guardar_respuesta_db(id_pregunta, respuesta, id_persona):
    try:
        respuesta = RespuestaVark(id_persona=id_persona, id_pregunta=id_pregunta, respuesta=respuesta)
        session_db.add(respuesta)
        session_db.commit()
    except Exception as e:
        flash(f"No se pudo guardar la respuesta: {e}", 'error')

@app.route('/calcular_perfil')
def calcular_perfil():
    global id_persona

    respuestas = session_db.query(RespuestaVark).filter_by(id_persona=id_persona).all()
    
    perfil = {"V": 0, "A": 0, "R": 0, "K": 0}
    for respuesta in respuestas:
        modo = obtener_modo_vark(respuesta.id_pregunta, respuesta.respuesta)
        if modo:
            perfil[modo] += 1
    
    # Insertar el perfil VARK en la tabla Resultado_VARK
    try:
        resultado_vark = ResultadoVark(id_persona=id_persona, V=perfil['V'], A=perfil['A'], R=perfil['R'], K=perfil['K'])
        session_db.add(resultado_vark)
        session_db.commit()
        flash("Perfil VARK calculado y guardado correctamente.", 'success')
        return redirect(url_for('mostrar_resultado'))
    except Exception as e:
        flash(f"No se pudo guardar el perfil VARK en la base de datos: {e}", 'error')
        return redirect(url_for('index'))

def obtener_modo_vark(id_pregunta, respuesta):
    for fila in tabla:
        if fila["#"] == id_pregunta:
            if respuesta == fila["V"]:
                return "V"
            elif respuesta == fila["A"]:
                return "A"
            elif respuesta == fila["R"]:
                return "R"
            elif respuesta == fila["K"]:
                return "K"
    return None

@app.route('/mostrar_resultado')
def mostrar_resultado():
    global id_persona

    try:
        perfil_vark = session_db.query(ResultadoVark).filter_by(id_persona=id_persona).first()
        return render_template('resultado.html', perfil_vark=perfil_vark)
    except Exception as e:
        flash(f"No se pudo obtener el perfil VARK: {e}", 'error')
        return redirect(url_for('index'))

##################jung##############################################################################################
# Función para obtener las preguntas de una sección específica
def get_preguntas(id_seccion):
    preguntas = db.session.query(PreguntasJung.pregunta).filter_by(id_seccion=id_seccion).all()
    return [pregunta[0] for pregunta in preguntas]

# Función para obtener el último id de perfil
def get_last_profile_id():
    id_perfil = session_db.query(func.max(Perfil.id_perfil)).scalar()
    return id_perfil or 0  # Devuelve 0 si no se encuentra ningún perfil


# Función para guardar los puntos totales de una sección
def save_points(id_perfil, id_seccion, puntos_totales):
    nuevo_puntos_totales = PuntosTotalesSeccion(id_perfil=id_perfil, id_seccion=id_seccion, puntos_totales=puntos_totales)
    session_db.add(nuevo_puntos_totales)
    session_db.commit()

# Función para comparar y guardar las secciones con mayor puntuación
def compare_and_save(id_perfil):
    for i in range(1, 8, 2):
        puntos_1 = get_section_points(id_perfil, i)
        puntos_2 = get_section_points(id_perfil, i + 1)
        mayor_seccion = f"Seccion {i}" if puntos_1 > puntos_2 else f"Seccion {i + 1}"
        puntos_seccion_mayor = max(puntos_1, puntos_2)
        save_comparison(id_perfil, mayor_seccion, puntos_seccion_mayor)

# Función para obtener los puntos totales de una sección
def get_section_points(id_perfil, id_seccion):
    puntos = session_db.query(PuntosTotalesSeccion.puntos_totales).filter_by(id_perfil=id_perfil, id_seccion=id_seccion).scalar()
    return puntos if puntos else 0

# Función para guardar la comparación de las secciones
def save_comparison(id_perfil, seccion_mayor, puntos_seccion_mayor):
    nueva_comparacion = ComparacionSecciones(id_perfil=id_perfil, seccion_mayor=seccion_mayor, puntos_seccion_mayor=puntos_seccion_mayor)
    session_db.add(nueva_comparacion)
    session_db.commit()

# Función para determinar y guardar la categoría del perfil
def determine_and_save_category(id_perfil):
    secciones = session_db.query(ComparacionSecciones.seccion_mayor).filter_by(id_perfil=id_perfil).all()
    secciones = [seccion[0] for seccion in secciones]
    categoria = None

    if 'Seccion 3' in secciones and 'Seccion 5' in secciones:
        categoria = 'tecnico analitico'
    elif 'Seccion 3' in secciones and 'Seccion 6' in secciones:
        categoria = 'apoyo'
    elif 'Seccion 4' in secciones and 'Seccion 5' in secciones:
        categoria = 'controlador'
    elif 'Seccion 4' in secciones and 'Seccion 3' in secciones:
        categoria = 'social'
    elif 'Seccion 5' in secciones and 'Seccion 3' in secciones:
        categoria = 'tecnico analitico'
    elif 'Seccion 5' in secciones and 'Seccion 4' in secciones:
        categoria = 'controlador'
    elif 'Seccion 6' in secciones and 'Seccion 3' in secciones:
        categoria = 'apoyo'
    elif 'Seccion 6' in secciones and 'Seccion 4' in secciones:
        categoria = 'social'
    else:
        categoria = 'Sin categoría definida'

    nueva_categoria = CategoriaPerfil(id_perfil=id_perfil, categoria=categoria)
    session_db.add(nueva_categoria)
    session_db.commit()

@app.route('/seccion1', methods=['GET', 'POST'])
def seccion1():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 1, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion2'))
    else:
        preguntas = get_preguntas(1)
        return render_template('seccion.html', seccion=1, preguntas=preguntas)


@app.route('/seccion2', methods=['GET', 'POST'])
def seccion2():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 2, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion3'))
    else:
        preguntas = get_preguntas(2)
        return render_template('seccion.html', seccion=2, preguntas=preguntas)


@app.route('/seccion3', methods=['GET', 'POST'])
def seccion3():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 3, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion4'))
    else:
        preguntas = get_preguntas(3)
        return render_template('seccion.html', seccion=3, preguntas=preguntas)


@app.route('/seccion4', methods=['GET', 'POST'])
def seccion4():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 4, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion5'))
    else:
        preguntas = get_preguntas(4)
        return render_template('seccion.html', seccion=4, preguntas=preguntas)


@app.route('/seccion5', methods=['GET', 'POST'])
def seccion5():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 5, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion6'))
    else:
        preguntas = get_preguntas(5)
        return render_template('seccion.html', seccion=5, preguntas=preguntas)


@app.route('/seccion6', methods=['GET', 'POST'])
def seccion6():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 6, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion7'))
    else:
        preguntas = get_preguntas(6)
        return render_template('seccion.html', seccion=6, preguntas=preguntas)


@app.route('/seccion7', methods=['GET', 'POST'])
def seccion7():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 7, puntos_totales)

        flash('Respuestas registradas correctamente')
        return redirect(url_for('seccion8'))
    else:
        preguntas = get_preguntas(7)
        return render_template('seccion.html', seccion=7, preguntas=preguntas)


@app.route('/seccion8', methods=['GET', 'POST'])
def seccion8():
    if request.method == 'POST':
        id_perfil = get_last_profile_id()
        puntos_totales = sum([int(request.form[f'respuesta_{i+1}']) if request.form[f'respuesta_{i+1}'] else 0 for i in range(9)])
        save_points(id_perfil, 8, puntos_totales)

        # Supongamos que esto realiza las comparaciones finales y las guarda
        compare_and_save(id_perfil)
        determine_and_save_category(id_perfil)

        categoria = session_db.query(CategoriaPerfil.categoria).filter_by(id_perfil=id_perfil).scalar()

        flash('Respuestas registradas correctamente')
        flash('Perfil clasificado correctamente')
        return redirect(url_for('result_jung', categoria=categoria))
    else:
        preguntas = get_preguntas(8)
        return render_template('seccion.html', seccion=8, preguntas=preguntas)

@app.route('/result_jung/<categoria>')
def result_jung(categoria):
    return render_template('result_jung.html', categoria=categoria)
#---------------------------Resultados-----------------------#
@app.route('/')
def bubu():
    return render_template('busqueda_p.html')

@app.route('/ver_perfil/<int:id_perfil>')
def ver_perfil(id_perfil):
    busqueda_perfil = session_db.query(Perfil).filter_by(id_perfil=id_perfil).first()
    if busqueda_perfil:
        resultado_vark = session_db.query(ResultadoVark).filter_by(id_persona=id_perfil).first()
        if resultado_vark:
            perfil_vark = {
                "Visual (V)": resultado_vark.V,
                "Auditivo (A)": resultado_vark.A,
                "Lector - Escritor (R)": resultado_vark.R,
                "Kinestésico (K)": resultado_vark.K
            }
            mayor_modo = max(perfil_vark, key=perfil_vark.get)
            categoria = session_db.query(CategoriaPerfil.categoria).filter_by(id_perfil=id_perfil).scalar()
            informacion_adicional = obtener_informacion_adicional(categoria)
            return render_template('busqueda_p.html', busqueda_perfil=busqueda_perfil, perfil_vark=perfil_vark, mayor_modo=mayor_modo, categoria=categoria, informacion_adicional=informacion_adicional)
        else:
            flash('No se encontraron resultados VARK para este perfil', 'error')
            return redirect(url_for('buscar_perfil'))
    else:
        flash('No se encontró ningún perfil con ese ID', 'error')
        return redirect(url_for('buscar_perfil'))

def obtener_informacion_adicional(categoria):
    informacion = ""
    if categoria == 'Tecnico analitico':
        informacion = "Pensadores y analistas lógicos. Interesados por las realidades y los hechos."
    elif categoria == 'Controlador':
        informacion = "Trazan estrategias y controlan sistemas. Necesitan información y apoyo empáticos y sinceros. Tratan de que todos estén contentos."
    elif categoria == 'Social':
        informacion = "Joviales, logran fácilmente ser el centro."
    else:
        informacion = "Sin información adicional disponible."
    return informacion



if __name__ == '__main__':
    app.run(debug=True)