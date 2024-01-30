from flask import Flask, request, jsonify
from std_msgs.msg import String
import rospy
from threading import Thread
import time

app = Flask(__name__)

# Definir los nombres de los tópicos ROS 1
input_topic = '/inputmsg'
output_topic = '/outputmsg'

# Variables para almacenar el último mensaje y el mensaje de bienvenida
last_message = None
welcome_messages = ['¡Bienvenido!', 'Hola desde Flask!', 'Saludos desde ROS 1!']

# Función para obtener el último mensaje del tópico ROS 1
def get_last_ros_message():
    # Esperar a que se reciba al menos un mensaje
    while last_message is None and not rospy.is_shutdown():
        rospy.sleep(0.1)

    # Devolver el último mensaje (o un mensaje de ejemplo si no se recibió ninguno)
    return last_message or "No se ha recibido ningún mensaje en el tópico"

# Función de devolución de llamada para manejar nuevos mensajes
def callback(msg):
    global last_message
    last_message = msg.data

# Función para publicar un mensaje en el tópico ROS 1
def publish_ros_message(message, topic):
    # Crear un nodo ROS 1 si no está inicializado
    if not rospy.core.is_initialized():
        rospy.init_node('flask_ros_bridge', anonymous=True)

    # Crear un publicador para el tópico especificado
    pub = rospy.Publisher(topic, String, queue_size=10)

    # Crear un mensaje ROS 1 del tipo String
    msg = String()
    msg.data = message

    # Publicar el mensaje en el tópico
    pub.publish(msg)

    # Esperar un breve momento para asegurarse de que el mensaje se haya publicado
    rospy.sleep(0.1)

# Función para publicar un mensaje de bienvenida cada 2 segundos
def welcome_message_thread():
    while not rospy.is_shutdown():
        for welcome_message in welcome_messages:
            publish_ros_message(welcome_message, output_topic)
            rospy.sleep(2)

# Endpoint GET para obtener el último mensaje del tópico ROS 1
@app.route('/get_last_message', methods=['GET'])
def get_last_message_endpoint():
    # Obtener el último mensaje del tópico ROS 1
    last_message = get_last_ros_message()
    return jsonify({'last_message': last_message})

# Endpoint POST para publicar un mensaje en el tópico ROS 1
@app.route('/publish_message', methods=['POST'])
def publish_message_endpoint():
    # Obtener el mensaje JSON del cuerpo de la solicitud
    data = request.get_json()

    # Verificar si la propiedad 'string' está presente en el JSON
    if 'string' not in data:
        return jsonify({'error': 'La propiedad "string" no se encuentra en el JSON'}), 400

    # Obtener el valor de la propiedad 'string'
    message_string = data['string']

    # Publicar el mensaje en el tópico ROS 1
    publish_ros_message(message_string, input_topic)

    return jsonify({'success': True})

if __name__ == '__main__':
    # Iniciar el hilo para publicar mensajes de bienvenida
    welcome_thread = Thread(target=welcome_message_thread)
    welcome_thread.start()

    # Ejecutar la aplicación Flask
    app.run(debug=True)
