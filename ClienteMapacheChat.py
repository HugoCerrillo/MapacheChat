import socket  # esta bilbioteca me sirve para manejar conexiones de red
import threading  # biblitoteca para crear hilos de ejecucion
import tkinter as tk  # biblioteca apra la interfaz grafia
from tkinter import simpledialog, scrolledtext

#apuntamos el cliente al servidor con su ip y el grupo (puerto)
DIRECCION_SERVIDOR = "192.168.106.84"
PUERTO_SERVIDOR = 12345

#conectamos al servidor con un socket apuntando hacia su ip y el puerto
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente_socket.connect((DIRECCION_SERVIDOR, PUERTO_SERVIDOR))

#pedimos el nombre de usuario al iniciar
ventana_nombre = tk.Tk()
ventana_nombre.withdraw()  #ocultamos la ventana principal
nombre_usuario = simpledialog.askstring("Nombre", "ingresa tu nombre de usuario:")

cliente_socket.sendall(nombre_usuario.encode())  #enviamsos el nombre al servidor

#esta funcion me sirve para enviar mensajes
def enviar_mensaje():
    mensaje = entrada_mensaje.get() #traemos el mensaje de la caja de texto
    if mensaje: #si hay mensaje
        cliente_socket.sendall(mensaje.encode()) #codificamos y enviamos el mensaje
        entrada_mensaje.delete(0, tk.END)

#esta funcion me sirve para recibir mensajes del servidor (difusion)
def recibir_mensajes():
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode() #recibimos y descodificamos el mensaje 
            if mensaje: #si hay mensaje 
                agregar_mensaje(mensaje) #agregamos el mensaje en al interfaz del usaurio
        except:
            break

#esta funcion nos sirve para agregar mensajes a la interfaz dek usuario
#recibe de paranetro el mensaje        
def agregar_mensaje(mensaje):
    caja_chat.config(state=tk.NORMAL)
    caja_chat.insert(tk.END, mensaje + "\n")
    caja_chat.config(state=tk.DISABLED)
    caja_chat.yview(tk.END)

#configuracmso la intefaz de usuario
ventana_cliente = tk.Tk()
ventana_cliente.title(f"Chat - {nombre_usuario}")

caja_chat = scrolledtext.ScrolledText(ventana_cliente, state=tk.DISABLED, width=50, height=20)
caja_chat.pack()

entrada_mensaje = tk.Entry(ventana_cliente, width=40)
entrada_mensaje.pack(side=tk.LEFT, padx=10)

boton_enviar = tk.Button(ventana_cliente, text="Enviar", command=enviar_mensaje)
boton_enviar.pack(side=tk.RIGHT)

threading.Thread(target=recibir_mensajes, daemon=True).start()

ventana_cliente.mainloop()
