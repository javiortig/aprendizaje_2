################################################################################
# Javier Orti García. Chatbot para un restaurante ficticio llamado El Puntillo
# Este chatbot permite interactuar con los clientes de un restaurante y recopilar los pedidos de comida que realicen para entregar a domicilio o recoger en las instalaciones.
# El chatbot utiliza un LLM para generar respuestas a las preguntas de los usuarios, según las especificaciones del restaurante.
# Para terminar la conversacion, basta con decirle al bot que no necesitas más ayuda, o que has terminado de hacer el pedido. También puedes usar el botón de terminar chat.
################################################################################
from openai import OpenAI
import panel as pn
pn.extension()



class Chatbot:
    def __init__(self, client):
        """
        Inicializa el chatbot con un mensaje de bienvenida y una lista vacía de mensajes.
        El mensaje de bienvenida es el primer mensaje que se envía al usuario.
        La lista de mensajes se utiliza para almacenar el historial de la conversación.

        Parametros:
            client (OpenAI): El cliente de OpenAI para interactuar con la API.
        """
        self.client = client
        self.ending_message = "Gracias por confiar en nosotros."
        self.welcome_message = "Bienvenido al restaurante El Puntillo. ¿En que podemos ayudarte?"
        self.messages =  [
        {'role': 'system', 'content': f'Eres un ChatBot ChatBot que permite interactuar con los clientes de un restaurante y recopilar los pedidos de comida que realicen para entregar a domicilio o recoger en las instalaciones. Si consideras que el usuario ha terminado con la conversaci n, responde exactamente con "{self.ending_message}"'},
        {'role': 'assistant', 'content': self.welcome_message}
        ]


    def completion_call(self, newPrompt, temperature=1, top_p=1, frequency_penalty=0.0, model="gpt-4o-mini"):
        """
        Llama a la API de OpenAI para generar una respuesta a la pregunta dada.

        Parametros:
            newPrompt (str): La pregunta para generar una respuesta.
            temperature (float): La temperatura para la generación (por defecto es 1).
            top_p (float): El top_p para la generación (por defecto es 1).
            frequency_penalty (float): La penalización de frecuencia para la generación (por defecto es 0.0).
            model (str): El modelo para usar para la generación (por defecto es 'gpt-4o-mini').

        Devuelve:
            str: La respuesta generada.
        """
        # TODO: control de errores
        answer = self.client.chat.completions.create(
            model=model,
            messages=self.messages + [{"role": "user", "content": newPrompt}],
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty
        )
        self.messages.append({"role": "user", "content": newPrompt})
        self.messages.append({"role": "assistant", "content": answer.choices[0].message.content})
        return answer.choices[0].message.content
    
    def is_chat_ended(self):
        """
        Comprueba si el chat ha terminado buscando la cadena "gracias por confiar en nosotros" en la última respuesta del chatbot
        Devuelve:
            bool: True si el chat ha terminado, False si no
        """
        return self.ending_message.strip().lower() in self.messages[-1]["content"].strip().lower()
    
    def print_last_message(self):
        """
        Imprime la última respuesta del chatbot
        """
        # Print the last message sent by the chatbot
        print(self.messages[-1]["content"])

    
    def chat(self):
        """
        Chat alternativo para el terminal, sin GUI.
        """
        chat_is_ended = False
        print(self.welcome_message)
        while not chat_is_ended:
            user_input = input()
            self.completion_call(user_input)
            self.print_last_message()
            chat_is_ended = self.is_chat_ended()
            
    def print_messages(self):
        """
        Imprime todas las respuestas del chatbot y el usuario
        """
        for message in self.messages:
            print(message["role"] + ": " + message["content"])


class ChatbotGUI:
    def __init__(self, chatbot: Chatbot):
        """	
        Inicializa la interfaz de usuario del chatbot.
        
        Parametros:
            chatbot (Chatbot): Instancia de la clase chatbot que se va a utilizar.
        """
        self.chatbot = chatbot

        # Widgets
        self.inp = pn.widgets.TextInput(
            placeholder='Escribe tu mensaje...',
            sizing_mode='stretch_width'
        )
        self.button_conversation = pn.widgets.Button(
            name="📨",
            button_type="primary",
            width=60
        )
        self.button_end_chat = pn.widgets.Button(
            name="Terminar Chat",
            button_type="danger",
            width=150
        )
        self.chat_display = pn.pane.Markdown(
            self.chatbot.welcome_message,
            sizing_mode="stretch_both",
            height=400
        )

        # Eventos
        self.button_conversation.on_click(self.send_message)
        self.button_end_chat.on_click(self.end_chat)

        # Interfaz de mensajes
        input_row = pn.Row(
            self.inp,
            self.button_conversation,
            sizing_mode="stretch_width"
        )

        self.dashboard = pn.Column(
            self.chat_display,
            input_row,
            self.button_end_chat,
            sizing_mode="stretch_width"
        )

    def send_message(self, event=None):
        """
        Envía el mensaje del usuario al chatbot y actualiza la interfaz de usuario.
        Si el mensaje es vacío, no hace nada. Si el chat ha terminado, desactiva los botones.
        """
        user_input = self.inp.value
        if not user_input.strip():
            return

        response = self.chatbot.completion_call(user_input)
        self.update_chat_display()

        self.inp.value = ""

        if self.chatbot.is_chat_ended():
            self.disable_chat()
            self.chat_display.object += "\n\n---\n**Chat finalizado.**"

    def update_chat_display(self):
        """
        Actualiza el área de chat con el historial completo de la conversación.
        Recorre todos los mensajes y los formatea como Markdown.
        """
        full_conversation = ""
        for msg in self.chatbot.messages:
            if msg['role'] == 'user':
                full_conversation += f"**Usuario:** {msg['content']}\n\n"
            elif msg['role'] == 'assistant':
                full_conversation += f"**Bot:** {msg['content']}\n\n"
        self.chat_display.object = full_conversation

    def disable_chat(self):
        """
        Desactiva los elementos de entrada y el botón de conversación.
        """
        self.inp.disabled = True
        self.button_conversation.disabled = True
        self.button_end_chat.disabled = True

    def end_chat(self, event=None):
        """
        Termina el chat manualmente y actualiza la interfaz de usuario.
        Desactiva los botones y muestra un mensaje de finalización.
        """
        self.disable_chat()
        self.chat_display.object += "\n\n---\n**Has terminado el chat manualmente.**"

    def show(self):
        """
        Muestra la interfaz del chatbot.
        """
        return self.dashboard.servable()
    

# Cargar clave API
with open("./k.txt") as f:
    api_key = f.readline().strip()

client = OpenAI(api_key=api_key)
chatbot = Chatbot(client)

gui = ChatbotGUI(chatbot)
gui.show()