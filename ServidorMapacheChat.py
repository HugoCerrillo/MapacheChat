import socket  # esta bilbioteca me sirve para manejar conexiones de red
import threading  # biblitoteca para crear hilos de ejecucion
import tkinter as tk  # biblioteca apra la interfaz grafia
from tkinter import scrolledtext  # biblioteca para la caja de chat con desplazamiento
from datetime import datetime

#Configuracion para los grupos de chat (Puertos)
PUERTOS = [12345, 12346]  # lista de grupos (puertos) de chat en los que el servidor escuchara conexiones
servidores = {}  # diccionario para almacenar los sockets de los servidores
clientes_por_puerto = {}  # diccionario para almacenar los clientes conectados a cada grupo (puerto)
lista_comandos = {"/ver_miembros", "/fecha_hora"}

#Aqui esta el método para ejecutar los comandos
def comandos(comando, puerto):
    if comando == "/ver_miembros":
        mensaje = "----Lista de miembros------\n"
        for nombre in clientes_por_puerto[puerto].values():  # Obtener solo los nombres
            mensaje += nombre + "\n"
        agregar_mensaje_servidor(mensaje)
        enviar_a_grupo(mensaje, puerto)
    elif comando == "/fecha_hora":
        ahora = datetime.now()
        mensaje = "Servidor: " + str(ahora)
        agregar_mensaje_servidor(mensaje)  #mostramos en la interfaz del servidor
        enviar_a_grupo(mensaje, puerto)  #enviamos el mensaje a los clientes del mismo grupo (puerto)
    #elif comando.startswith("/expulsar_@"):
        #nombre_a_expulsar = comando.replace("/expulsar_@", "").strip()

        # Buscar el socket del usuario a expulsar
        #socket_a_expulsar = None
        #for socket_cliente, nombre in clientes_por_puerto[puerto].items():
            #if nombre == nombre_a_expulsar:
                #socket_a_expulsar = socket_cliente
                #break
    
        #if socket_a_expulsar:
            #mensaje_expulsion = f"Servidor: {nombre_a_expulsar} ha sido expulsado del grupo."
            #agregar_mensaje_servidor(mensaje_expulsion)
            #enviar_a_grupo(mensaje_expulsion, puerto)

            # Cerrar la conexión y eliminar del diccionario
            #socket_a_expulsar.close()
            #del clientes_por_puerto[puerto][socket_a_expulsar]
        #else:
            #mensaje_error = f"Servidor: No se encontró a {nombre_a_expulsar} en el grupo."
            #agregar_mensaje_servidor(mensaje_error)
            #enviar_a_grupo(mensaje_error, puerto)
    else:
        mensaje = "Servidor: Ese comando esta mal chavo"
        agregar_mensaje_servidor(mensaje)  #mostramos en la interfaz del servidor
        enviar_a_grupo(mensaje, puerto)  #enviamos el mensaje a los clientes del mismo grupo (puerto)   
        
#esta funcion sirve para enviar mensajes a todos los clientes conectados a un puerto (grupo) específico
#recibe de parametro el mensaje y el grupo (puerto) al que s eva reenviar
def enviar_a_grupo(mensaje, puerto):
    for cliente in clientes_por_puerto[puerto]:  # por cada cliente onectado al puerto (grupo)
        try:
            cliente.sendall(mensaje.encode())  # enviamos el mensaje codificado a cada cliente
        except:
            cliente.close()  #cerrar la conexion si hay un error
            del clientes_por_puerto[puerto][cliente]  #eliminar cliente del diccionario si se desconecta

#esta funcion nos sirve para manejar un cliente individual en un hilo separado
#recibe de parametros la conexion, la direccion y el puerto (grupo)            
def manejar_cliente(conexion, direccion, puerto):
    try:
        nombre_usuario = conexion.recv(1024).decode()  #al conectarse, recibimos el nombre del usuario al conectarse
        clientes_por_puerto[puerto][conexion] = nombre_usuario  #agregar cliente al diccionario del puerto (grupo)
        mensaje_conexion = f"{nombre_usuario} se ha unido al grupo {puerto}."  # Notificar la conexión
        agregar_mensaje_servidor(mensaje_conexion)
        enviar_a_grupo(mensaje_conexion, puerto)  #hacemos una difusion para enviar el mensaje de conexion a todos los clientes del grupo
        
        while True:
            mensaje = conexion.recv(1024).decode()  #recibimos el mensaje del cliente
            if mensaje.startswith("/"): #Se revisa si el mensaje empieza "/" para sidentificar comandos
                comandos(mensaje, puerto) #Se llama la función
            else:
                if not mensaje: #si no hay mensaje
                    break  #salimos si el mensaje esta vacio
                mensaje_formateado = f"{nombre_usuario}: {mensaje}"  #damos un pequeño formato al mensaje con el nombre del usuario
                agregar_mensaje_servidor(mensaje_formateado)  #mostramos en la interfaz del servidor
                enviar_a_grupo(mensaje_formateado, puerto)  #enviamos el mensaje a los clientes del mismo grupo (puerto)        
    except:
        pass
    finally:
        del clientes_por_puerto[puerto][conexion]   #eliminamos cliente del diccionario al desconectarse
        mensaje_salida = f"{nombre_usuario} ha salido del grupo {puerto}."  #armamos un mensaje que indica la desconexion del usuario
        agregar_mensaje_servidor(mensaje_salida)
        enviar_a_grupo(mensaje_salida, puerto)  #enviamos el mensaje de salida a los clientes del grupo
        conexion.close()  #cerrar conexion con el cliente

#esta funcion sirve para iniciar un servidor en un puerto específico y en un hilito distinto
#recibe el parametro con el puerto        
def iniciar_servidor(puerto):
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #creamos el socket TCP
    servidor_socket.bind(("0.0.0.0", puerto))  #asociamos el socket a todas las interfaces de red y al puerto (grupo) especifico
    servidor_socket.listen(5)  #ponemos el servidor en modo escucha aceptando hasta 5 conexiones en espera
    servidores[puerto] = servidor_socket  #almacenar el socket del servidor en el diccionario
    clientes_por_puerto[puerto] = {}  #inicializar la lista de clientes para este puerto (grupo)
    agregar_mensaje_servidor(f"Servidor escuchando en el puerto {puerto}...") #mandamos un mensaje informativo a la interfaz del servidor
    
    while True:
        conexion, direccion = servidor_socket.accept()  #aceptamos una nueva conexión de cliente
        hilo = threading.Thread(target=manejar_cliente, args=(conexion, direccion, puerto), daemon=True)  #crear un hilito para manejar el cliente
        hilo.start()  #iniciamos el hilito

#esta funcion sirve para agregar mensajes en la interfaz del servidor
#recibe de parametro el mensaje
def agregar_mensaje_servidor(mensaje):
    caja_chat.config(state=tk.NORMAL)  #habilitamos la edicion en la caja de chat
    caja_chat.insert(tk.END, mensaje + "\n")  #insertamos el mensaje en la interfaz del servidor
    caja_chat.config(state=tk.DISABLED)  #volvemos a deshabilitar edicion para evitar cambios manualmente
    caja_chat.yview(tk.END)  #desplazar automaticamente al ultimo mensaje

#creamos la interfaz grafica del servidor
ventana_servidor = tk.Tk()
ventana_servidor.title("Servidor MapacheChat")  #titulo de la ventanita

caja_chat = scrolledtext.ScrolledText(ventana_servidor, state=tk.DISABLED, width=60, height=20)  #caja de chat con desplazamiento
caja_chat.pack()

#creamos hilito para cada puerto configurado
for puerto in PUERTOS:
    threading.Thread(target=iniciar_servidor, args=(puerto,), daemon=True).start()

ventana_servidor.mainloop()  #iniciamos el ciclo principal de la interfaz grafica
