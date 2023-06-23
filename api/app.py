from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://arturocs:iEZ9pcgZpUjAWJCP@cluster0.bclah5c.mongodb.net/TestWeb'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Configura el servidor de correo saliente
app.config['MAIL_PORT'] = 587  # Configura el puerto del servidor de correo
app.config['MAIL_USE_TLS'] = True  # Configura TLS para la seguridad del correo
app.config['MAIL_USERNAME'] = 'testvocacionalunt@gmail.com'  # Configura el correo electrónico del remitente
app.config['MAIL_PASSWORD'] = 'dgowglpmcrkohzcz'  # Configura la contraseña del correo electrónico del remitente

mongo = PyMongo(app)
CORS(app)  # Para que la comunicación entre backend y frontend sea estable

dbUser = mongo.db['Users']

import sys
import codecs

# Configura la codificación predeterminada como UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

encouraging_messages = {
    'REALISTA': 'Sigue cultivando tu enfoque práctico y tu habilidad para resolver problemas como una persona realista.',
    'INVESTIGADOR': 'Continúa explorando el mundo y desafiándote a ti mismo con nuevos conocimientos como una persona investigadora.',
    'ARTISTICO': 'Sigue desarrollando tu creatividad y encuentra formas de expresarte a través de diferentes medios artísticos como una persona artística.',
    'SOCIAL': 'Continúa siendo empático y ayudando a los demás en tu comunidad como una persona de personalidad social.',
    'EMPRENDEDOR': 'Sigue impulsando tus ideas y aprovechando tu espíritu emprendedor para lograr tus metas como una persona emprendedora.',
    'CONVENCIONAL': 'Continúa siendo organizado y estructurado en tu enfoque hacia el trabajo y las tareas como una persona convencional.'
}

def get_top_personalities(scores):
    sorted_personalities = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return sorted_personalities[:2]

def send_email(correo, nombres, apellidos, scores):
    remitente = 'testvocacionalunt@gmail.com'
    destinatario = correo

    top_personalities = get_top_personalities(scores)
    first_personality = top_personalities[0]
    encouraging_message = '<br>'.join([encouraging_messages[personality] for personality in top_personalities])

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = 'Resultados del test'

    cuerpo_mensaje = f"""
        <html>
            <body>
                <h1>¡Hola {nombres} {apellidos}!</h1>
                <p style="font-size: 15px;">Aquí están tus resultados del test:</p>
                <p style="font-size: 15px;">La personalidad con mayor puntaje es: <strong>{first_personality}</strong>.</p>
                <p style="font-size: 15px;">Y tu segunda personalidad es: <strong>{top_personalities[1]}</strong>.</p>
                <p style="font-size: 15px;">{encouraging_message}</p>
                <p>
                    <span style="font-size: 23px;">🎓📚🌟✨🎯💼🔧🔎📊</span>
                </p>
            </body>
        </html>
    """

    mensaje.attach(MIMEText(cuerpo_mensaje, 'html'))

    texto_mensaje = mensaje.as_string().encode('utf-8')

    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    servidor_smtp.starttls()

    servidor_smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    servidor_smtp.sendmail(remitente, destinatario, texto_mensaje)
    servidor_smtp.quit()




@app.route('/save-result', methods=['POST'])
def saveResults():
    ultimo_documento = dbUser.find_one(sort=[('_id', -1)])
    ultimo_id = ultimo_documento['_id'] if ultimo_documento else None
    nuevo_id = int(ultimo_id) + 1 if ultimo_id else 1

    result = dbUser.insert_one({
        '_id': nuevo_id,
        'correo': request.json.get('correo', ''),
        'nombres': request.json.get('nombres', ''),
        'apellidos': request.json.get('apellidos', ''),
        'resultado': {
            'realista': request.json.get('scores', {}).get('REALISTA', 0),
            'investigador': request.json.get('scores', {}).get('INVESTIGADOR', 0),
            'artistico': request.json.get('scores', {}).get('ARTISTICO', 0),
            'social': request.json.get('scores', {}).get('SOCIAL', 0),
            'emprendedor': request.json.get('scores', {}).get('EMPRENDEDOR', 0),
            'convencional': request.json.get('scores', {}).get('CONVENCIONAL', 0)
        }
    })

    send_email(
        request.json.get('correo', ''),
        request.json.get('nombres', ''),
        request.json.get('apellidos', ''),
        request.json.get('scores', {})
    )

    return jsonify(str(result.inserted_id))


@app.route('/users', methods=['GET'])
def getUsers():
    users = []
    collection = dbUser.find()
    for doc in collection:
        user = {
            '_id': doc['_id'],
            'correo': doc['correo'],
            'nombres': doc['nombres'],
            'apellidos': doc['apellidos'],
            'resultado': doc['resultado']
        }
        users.append(user)
    return jsonify(users)


@app.route('/user/<string:correo>', methods=['GET'])
def getUser(correo):
    user = dbUser.find_one({'correo': correo})

    return jsonify({
        '_id': user['_id'],
        'correo': user['correo'],
        'nombres': user['nombres'],
        'apellidos': user['apellidos'],
        'resultado': user['resultado']
    })


@app.route('/delete-user/<string:code>', methods=['DELETE'])
def deleteUser(code):
    dbUser.delete_one({'_id': code})
    return jsonify({'mensaje': 'Usuario eliminado satisfactoriamente'})


@app.route('/update-user/<int:code>', methods=['PUT'])
def updateUser(code):
    dbUser.update_one({'_id': code}, {'$set': {
        'correo': request.json['correo'],
        'password': request.json['password'],
        'nombres': request.json['nombres'],
        'apellidos': request.json['apellidos'],
        'resultado': request.json['resultado']
    }})
    
    return jsonify({'mensaje': 'Usuario actualizado de forma exitosa'})



if __name__=='__main__':
    app.run(debug=True)


