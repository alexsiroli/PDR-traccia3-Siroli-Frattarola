import random
import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox
import socket
import packet_decoder as pd
import packet_type as pt
import threading

# FINESTRA DI GIOCO PRINCIPALE
window_main = tk.Tk()
window_main.title("Il Gioco delle Tabelline")

# client di rete
server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
players_data = []  # id, name, score
BUFFER_SIZE = 4096
your_name = ""
your_id = ""

top_welcome_frame = tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text="Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda: connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack()
top_message_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)
ranking_frame = tk.Frame(top_frame, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)
lbl_title_name = tk.Label(ranking_frame, text="---- Classifica attuale ----", font="Helvetica 13 bold")
lbl_title_name.pack()
ranking_frame.pack(padx=(10, 10))
tk.Label(top_frame, text="***********************************************************").pack()
tk.Label(top_frame, text="Scegli un emoji", font="Helvetica 13").pack()

top_frame.pack()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

button_frame = tk.Frame(window_main)

photo_one = PhotoImage(file=r"love.png")
photo_two = PhotoImage(file=r"thinky.png")
photo_three = PhotoImage(file=r"sassypng.png")

btn_one = tk.Button(button_frame, text="1", command=lambda: choice(1), state=tk.DISABLED, image=photo_one)
btn_two = tk.Button(button_frame, text="2", command=lambda: choice(2), state=tk.DISABLED, image=photo_two)
btn_three = tk.Button(button_frame, text="3", command=lambda: choice(3), state=tk.DISABLED, image=photo_three)
btn_one.grid(row=0, column=0)
btn_two.grid(row=0, column=1)
btn_three.grid(row=0, column=2)
button_frame.pack()

rules_frame = tk.Frame(middle_frame)
lbl_outcome = tk.Label(rules_frame, text="", font="Helvetica 13 bold")
lbl_outcome.pack()
lbl_rules = tk.Label(rules_frame, text="")
rules_frame.pack(side=tk.TOP)

form_frame = tk.Frame(middle_frame)
lbl_question = tk.Label(form_frame, text="")
lbl_question.pack(side=tk.LEFT)
lbl_question = tk.Label(form_frame, text="")
lbl_question.pack(side=tk.LEFT)
ent_answer = tk.Entry(form_frame)
ent_answer.pack(side=tk.LEFT)
ent_answer.config(state=tk.DISABLED)

btn_send = tk.Button(form_frame, text="Invia", command=lambda: send_answer())
btn_send.pack(side=tk.LEFT)
form_frame.pack(side=tk.TOP)
btn_send.config(state=tk.DISABLED)

final_frame = tk.Frame(middle_frame)
lbl_result = tk.Label(final_frame, text="", foreground="blue", font="Helvetica 14 bold")
lbl_result.pack()
tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text="", font="Helvetica 13 bold", foreground="blue")
lbl_final_result.pack()
tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack()


def on_closing():
    if server is not None:
        server.close()
    window_main.destroy()


window_main.protocol("WM_DELETE_WINDOW", on_closing)


def enable_disable_buttons(todo):
    if todo == "disable":
        btn_one.config(state=tk.DISABLED)
        btn_two.config(state=tk.DISABLED)
        btn_three.config(state=tk.DISABLED)
    else:
        btn_one.config(state=tk.NORMAL)
        btn_two.config(state=tk.NORMAL)
        btn_three.config(state=tk.NORMAL)


def send_answer():
    global server
    try:
        result = int(ent_answer.get())
        server.send(pd.encode({"p_id": 4, "answer": result}))
        ent_answer.delete(0, 'end')
        ent_answer.config(state=tk.DISABLED)
        btn_send.config(state=tk.DISABLED)
    except ValueError:
        tk.messagebox.showerror(title="Errore", message="Devi inserire un numero!")


def connect():
    global your_name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="Errore", message="Devi inserire il tuo nome!")
    else:
        your_name = ent_name.get()
        connect_to_server(your_name)


def connect_to_server(name):
    global server, HOST_PORT, HOST_ADDR
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST_ADDR, HOST_PORT))
        server.send(pd.encode({'p_id': pt.Packet.new_player_name.value, 'name': name}))  # Invia il nome al server dopo la connessione
        lbl_final_result["text"] = "LA PARTITA STA PER COMINCIARE..."

        # disable widgets
        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)

        # avvia un thread per continuare a ricevere messaggi dal server
        # non bloccare il thread principale :)
        threading._start_new_thread(manage_messages_from_server, (server, ""))
    except Exception as e:
        print(e)
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(
            HOST_PORT) + " Server may be Unavailable. Try again later")


def choice(arg):
    global server
    rnd = random.randint(1, 3)
    if arg != rnd:
        lbl_outcome["text"] = "Complimenti! :)"
        lbl_outcome.configure(foreground="green")
        server.send(pd.encode({"p_id": pt.Packet.new_question_request.value}))
        lbl_rules["text"] = "Rispondi alla seguente domanda:"
        lbl_rules.pack()
        enable_disable_buttons("disable")
    else:
        lbl_outcome["text"] = "Mi dispiace :("
        lbl_outcome.configure(foreground="red")
        lbl_final_result["text"] = "SEI STATO ELIMINATO"
        server.close()


def update_scores():
    for player in players_data:
        player["label"]["text"] = player["name"] + " -> " + str(player["score"])


def manage_messages_from_server(sck, m):
    global lbl_question, your_id

    while True:
        while True:
            data = sck.recv(BUFFER_SIZE)
            update_scores()
            if not data:
                break
            data = pd.decode(data)
            if int(data["p_id"]) == pt.Packet.start.value:
                enable_disable_buttons("active")
                lbl_final_result["text"] = "PARTITA IN CORSO..."
                break
            if data["name"] == your_name:
                your_id = data["id"]
            players_data.append({"name": data["name"], "id": data["id"], "score": 0})
            players_data[-1]["label"] = tk.Label(ranking_frame, text=players_data[-1]["name"] + " -> " + str(players_data[-1]["score"]))
            players_data[-1]["label"].pack()

        while True:  # finche non è finita la partita
            data = sck.recv(BUFFER_SIZE)
            if not data:
                break
            data = pd.decode(data)

            if int(data["p_id"]) == pt.Packet.new_question.value:  # mi arriva una domanda nuova
                enable_disable_buttons("disable")
                lbl_question["text"] = data["question"]
                ent_answer.config(state=tk.NORMAL)
                btn_send.config(state=tk.ACTIVE)
            elif int(data["p_id"]) == pt.Packet.player_score.value:  # mi arriva il punteggio di qualcuno
                if data["client"] == your_id:
                    your_score = 0
                    for player in players_data:
                        if player["id"] == your_id:
                            your_score = int(player["score"])
                            player["score"] = data["score"]
                    if int(data["score"]) > your_score:
                        lbl_result["text"] = "Giusto! +1"
                        lbl_result.configure(foreground="green")
                    else:
                        lbl_result["text"] = "Errato! -1"
                        lbl_result.configure(foreground="red")
                    update_scores()
                    server.send(pd.encode({"p_id": pt.Packet.new_question_request.value}))

                else:
                    for opp in players_data:
                        if opp["id"] == data["client"]:
                            opp["score"] = data["score"]
                    update_scores()
            elif int(data["p_id"]) == pt.Packet.player_left.value:  # uno è stato eliminato
                for opp in players_data:
                    if opp["id"] == data["client"]:
                        opp["score"] = "Eliminato"
                update_scores()
            elif int(data["p_id"]) == pt.Packet.game_over.value:  # se uno ha vinto
                for opp in players_data:
                    if opp["id"] == data["winner"]:
                        opp["score"] = "Vincitore"
                update_scores()
                break

        lbl_outcome["text"] = ""
        lbl_rules["text"] = ""
        lbl_result["text"] = ""
        lbl_question["text"] = ""
        lbl_final_result["text"] = "NUOVA PARTITA A BREVE..."
        for player in players_data:
            if player["score"] == "Eliminato":
                players_data.remove(player)
            else:
                player["score"] = 0


window_main.mainloop()
