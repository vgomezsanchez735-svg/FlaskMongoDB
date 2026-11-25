# Importación de librerías necesarias
# render_template: para enviar datos a HTML
# request: para obtener datos de formularios
# redirect: para redirigir después de una acción
from flask import Flask, render_template, request, redirect
# MongoClient: permite conectarse a MongoDB desde Python
from pymongo import MongoClient
# ObjectId: permite trabajar con los IDs de MongoDB (_id)
from bson.objectid import ObjectId

# Se crea la aplicación Flask
app = Flask(__name__)

# Se establece la conexión con el servidor local de MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
# Se accede (o crea automáticamente) la base de datos llamada "streaming"
db = cliente["streaming"]
# Se accede (o crea automáticamente) la colección "peliculas"
coleccion = db["peliculas"]

# Esta ruta se ejecuta cuando el usuario entra a la página principal "/"
@app.route("/")
def index():
    # Se obtienen todos los documentos de la colección
    # find() devuelve un cursor, por eso se convierte a lista
    peliculas = list(coleccion.find())
    # Se envían los datos al archivo index.html
    return render_template("index.html", peliculas=peliculas)

# RUTA PARA AGREGAR DATOS
# Esta ruta solo acepta método POST (envío de formulario)
@app.route("/agregar", methods=["POST"])
def agregar():
    # Se obtienen los datos enviados desde el formulario HTML
    titulo = request.form["titulo"]
    genero = request.form["genero"]
    anio = request.form["anio"]
    # Se crea un diccionario (documento) con los datos
    nueva_pelicula = {
        "titulo": titulo,
        "genero": genero,
        "anio": anio
    }
    # Se inserta el documento en MongoDB
    coleccion.insert_one(nueva_pelicula)
    # Se redirige a la página principal después de insertar
    return redirect("/")

# RUTA PARA ELIMINAR DATOS
# Esta ruta debe colocarse DESPUÉS de la ruta "/agregar"
@app.route("/eliminar/<id>")
def eliminar(id):
    # Se utiliza ObjectId para convertir el id (que viene como texto desde la URL)
    # a un formato que MongoDB pueda reconocer correctamente
    coleccion.delete_one({"_id": ObjectId(id)})
    # Después de eliminar, se redirige a la página principal
    return redirect("/")


    # IMPORTANTE:
# Esta ruta debe colocarse después de la ruta "/eliminar"
# Mantener el orden lógico: index → agregar → eliminar → editar → actualizar
# Esta ruta NO modifica datos, solo muestra el formulario con información existente
@app.route("/editar/<id>")
def editar(id):
    # Se busca un documento en MongoDB usando su _id
    # IMPORTANTE: El id viene desde la URL como texto (string)
    # Por eso se convierte a ObjectId para que MongoDB lo reconozca
    pelicula = coleccion.find_one({"_id": ObjectId(id)})

    # Se envía la película encontrada al archivo editar.html
    # "pelicula" será usada en el formulario para mostrar los datos actuales
    return render_template("editar.html", pelicula=pelicula)



# Esta ruta debe colocarse después de la ruta "/editar"
# Aquí SÍ se modifican los datos en la base de datos
@app.route("/actualizar/<id>", methods=["POST"])
def actualizar(id):
    # Se reciben los datos del formulario enviado desde editar.html
    # request.form obtiene los valores de los inputs
    titulo = request.form["titulo"]
    genero = request.form["genero"]
    anio = request.form["anio"]

    # Se utiliza update_one para modificar un solo documento
    coleccion.update_one(
        # Filtro: se busca el documento por su _id
        {"_id": ObjectId(id)},
        # Operador $set:
        # Permite actualizar solo los campos indicados
        # No reemplaza todo el documento, solo modifica estos valores
        {"$set": {
            "titulo": titulo,
            "genero": genero,
            "anio": anio
        }}
    )
    # Después de actualizar, se redirige a la página principal
    return redirect("/")

# Esta condición verifica que el archivo se esté ejecutando directamente
if __name__ == "__main__":
    # Se ejecuta el servidor en modo desarrollo
    # debug=True permite ver errores en tiempo real
    app.run(debug=True)