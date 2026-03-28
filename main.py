from customtkinter import *
from socket import *
from threading import Thread

class MainWindow(CTk):
    def __init__(self, name, sock: socket):
        super().__init__()
        self.name = name
        self.socket = sock
        
        self.geometry('800x600')
        self.title('LogiTalk')
        
        # CTkOptionMenu, CTkButton (2 штуки), CTkScrollableFrame, CtkEntry
        self.btn_send = CTkButton(self, width=50, height=40, text='✈', command=self.send_message) # кнопка для відправки повідомлення, при натисканні викликає метод send_message
        
        self.btn_open = CTkButton(self, width=50, height=40, text='📁') # кнопка для відкриття файлів
        
        self.chat_field = CTkScrollableFrame(self) # прокручуваний фрейм для відображення повідомлень в чаті, всі повідомлення будуть додаватися в цей фрейм, якщо повідомлень багато, то з'явиться смуга прокрутки
        
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення') # поле для введення повідомлення, placeholder_text - це текст, який відображається в полі, коли воно порожнє, щоб підказати користувачу, що потрібно ввести повідомлення
        self.message_entry.bind('<Return>', self.send_message)
        
        self.theme_change = CTkOptionMenu(self, width=150, values=['Системна', 'Світла', 'Темна'], command=self.change_theme_colors)
        
        self.btn_send.place(x=0,y=0)
        self.btn_open.place(x=0,y=0)
        self.chat_field.place(x=0,y=0)
        self.message_entry.place(x=0,y=0)
        self.theme_change.place(x=0,y=0)

        self.adaptive_ui()
        try:
            hello = f'TEXT@{self.name}@Підключився до чату\n' # повідомлення для сервера про підключення нового користувача
            self.socket.sendall(hello.encode()) # відправка повідомлення на сервер про підключення нового користувача, якщо з'єднання є
            Thread(target=self.receive_message, daemon=True).start() # створення і запуск окремого потока для отримання повідомлень від сервера, daemon=True - це означає, що потік буде автоматично завершений при закритті головного потока програми
        except:
            pass

    def change_theme_colors(self, value):
        if value == 'Системна':
            set_appearance_mode('system')
        elif value == 'Світла':
            set_appearance_mode('light')
        elif value == 'Темна':
            set_appearance_mode('dark')
            
    
    def adaptive_ui(self):
        ww = self.winfo_width() # отримання поточної ширини вікна
        wh = self.winfo_height() # отримання поточної висоти вікна
        
        self.chat_field.configure(width=ww-20, height=wh-50) # налаштування розміру фрейму для повідомлень, щоб він займав всю ширину вікна за винятком 20 пікселів для відступів, і висоту вікна за винятком 50 пікселів для кнопок і поля введення повідомлення
        
        self.btn_send.place(x=ww-50,y=wh-40) # розміщення кнопки для відправки повідомлення в правому нижньому куті вікна, з відступом 50 пікселів від правого краю і 40 пікселів від нижнього краю
        self.btn_open.place(x=ww-105,y=wh-40) # розміщення кнопки для відкриття файлів зліва від кнопки для відправки повідомлення, з відступом 105 пікселів від правого краю і 40 пікселів від нижнього краю
        self.message_entry.configure(width=ww-110,height=40) # налаштування розміру поля для введення повідомлення, щоб він займав всю ширину вікна за винятком 110 пікселів для кнопок, і висоту 40 пікселів
        self.message_entry.place(x=0,y=wh-40) # розміщення поля для введення повідомлення в нижній частині вікна, з відступом 40 пікселів від нижнього краю
        
        self.after(100, self.adaptive_ui) # виклик методу adaptive_ui кожні 100 мілісекунд, щоб адаптувати інтерфейс до зміни розміру вікна, self.after - це метод для планування виклику функції через певний час, 100 - це час в мілісекундах, self.adaptive_ui - це функція, яка буде викликана через 100 мілісекунд

    def add_message(self, message, img=None, sender=0): # метод для додавання повідомлення в чат, sender=0 - від себе, sender=1 - від іншого користувача, сам метод може приймати текст, зображення і відправника
        message_frame = CTkFrame(self.chat_field) # створення фрейму для повідомлення
        if sender: # якщо повідомлення від іншого користувача, то прикріпити зліва і зробити сірим
            message_frame.pack(pady=5, padx=5, anchor='w')
            message_frame.configure(fg_color="#636363")
        else: # якщо від себе, то прикріпити праворуч і зробити синім
            message_frame.pack(pady=5, padx=5, anchor='e')
            message_frame.configure(fg_color="#2B2EE0")
        
        w_size = min(500, self.winfo_width()-20) # максимальна ширина повідомлення 500 або ширина вікна - 20
        
        if not img:
            # додавання тексту до повідомлення, з обмеженням ширини і переносом рядків
            CTkLabel(message_frame, text=message,text_color='#fff', justify='left', wraplength=w_size).pack(padx=10,pady=5)
        else:
            CTkLabel(message_frame, text=message,text_color='#fff', justify='left', wraplength=w_size, image=img, compound='top').pack(padx=10,pady=5)   

    def send_message(self, e=None): # метод для відправки повідомлення, який викликається при натисканні кнопки або клавіші Enter
        message = self.message_entry.get() # отримання тексту з поля введення
        if message and message != '': # якщо текст не порожній, то відправити його на сервер і додати в чат
            self.add_message(message) # додавання повідомлення в чат від себе
            data = f'TEXT@{self.name}@{message}\n' # TEXT@Dmytro@Привіт\n - формат повідомлення для сервера
            try: 
                self.socket.sendall(data.encode()) # відправка повідомлення на сервер, якщо з'єднання є
            except:
                pass
        self.message_entry.delete(0, 'end') # очищення поля введення після відправки повідомлення
        
    def receive_message(self): # метод для отримання повідомлень від сервера, який працює в окремому потоці
        buffer = '' # буфер для зберігання неповних повідомлень, які можуть прийти від сервера, оскільки TCP - це потік байтів і повідомлення можуть приходити частинами
        while True: # цикл для постійного отримання повідомлень від сервера
            try:
                message = self.socket.recv(32000) # отримання повідомлення від сервера, розмір буфера 32000 байт, якщо сервер відправив більше, то повідомлення прийде частинами і буде збережено в буфері
                buffer += message.decode('utf-8', errors='ignore') # додавання отриманого повідомлення до буфера, декодування байтів в рядок, ігнорування помилок декодування
                while '\n' in buffer: # якщо в буфері є символ нового рядка, то це означає, що прийшло повне повідомлення, яке можна обробити
                    line, buffer = buffer.split('\n', 1) # розділення буфера на перше повідомлення (до символу нового рядка) і остаток буфера (після символу нового рядка), line - це повне повідомлення, яке можна обробити, buffer - це неповне повідомлення, яке ще не прийшло повністю
                    self.handle_line(line.strip()) # обробка отриманого повідомлення, видалення пробілів з початку і кінця рядка
            except:
                break
        self.socket.close()
    
    def handle_line(self, line): # метод для обробки отриманого повідомлення, який розділяє повідомлення на частини за символом '@' і визначає тип повідомлення, а також відправника і текст повідомлення
        if not line: # якщо рядок порожній, то нічого не робити
            return
        parts = line.split('@',3) # TEXT@Dmytro@Привіт -> ['TEXT','Dmytro','Привіт'] # розділення рядка на частини за символом '@', максимум 3 частини, щоб текст повідомлення не розділявся, якщо в ньому є символ '@'
        ms_type = parts[0] # тип повідомлення 'TEXT' - це текстове повідомлення, 'IMAGE' - це зображення
        if ms_type == 'TEXT': # якщо тип повідомлення 'TEXT', то це текстове повідомлення
            if len(parts) >= 3: # якщо в повідомленні є хоча б 3 частини (тип, відправник, текст), то додати повідомлення в чат, інакше це некоректне повідомлення, яке можна проігнорувати
                self.add_message(f'{parts[1]}: {parts[2]}',sender=1) # додавання повідомлення в чат від іншого користувача, parts[1] - це відправник, parts[2] - це текст повідомлення
        

if __name__ == "__main__": # головна функція, яка запускає програму
    try: 
        client_socket = socket(AF_INET, SOCK_STREAM) # створення TCP сокета для підключення до сервера, AF_INET - це адрес IPv4, SOCK_STREAM - це тип сокета для TCP з'єднання
        client_socket.connect(('localhost', 22)) # підключення до сервера за адресою ...
        app = MainWindow("Dmytro", client_socket) # створення головного вікна програми, передача імені користувача і сокета для підключення до сервера
    except:
        print("Не вдалося підключитися до сервера") # виведення повідомлення про помилку підключення до сервера, якщо виникла помилка при створенні сокета або підключенні до сервера
        app = MainWindow("User", None)  # створення головного вікна програми без сокета, щоб можна було працювати з інтерфейсом, але не відправляти повідомлення на сервер

    app.mainloop() # запуск головного циклу програми