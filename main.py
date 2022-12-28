import tkinter
import customtkinter
import psycopg2
from psycopg2 import sql
from config import host, user, password, db_name
from tkinter import ttk, VERTICAL, END
import array

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app_width = 400
app_height = 400
app.geometry(f"{app_width}x{app_height}")
app.title("Пиццерия")

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
cursor = connection.cursor()
connection.autocommit = True

login_entry = None
password_entry = None
login_frame = None


def login(active):
    if active == 1:
        login_frame = customtkinter.CTkFrame(master=app,
                                             width=app_width,
                                             height=app_height,
                                             fg_color="transparent")
        label = customtkinter.CTkLabel(master=login_frame,
                                       text="Авторизация",
                                       font=("Times New Roman", 40),
                                       width=120,
                                       height=50,
                                       fg_color="transparent")
        label.pack(padx=20, pady=40, anchor=tkinter.CENTER)
        login_frame.pack(padx=20, pady=20)
        global login_entry
        login_entry = customtkinter.CTkEntry(master=login_frame, placeholder_text="логин")
        login_entry.pack(padx=20, pady=5, anchor=tkinter.CENTER)
        global password_entry
        password_entry = customtkinter.CTkEntry(master=login_frame, placeholder_text="пароль", show='*')
        password_entry.pack(padx=20, pady=5, anchor=tkinter.CENTER)
        submit_button = customtkinter.CTkButton(master=login_frame, text="Вход", command=entry_as_user)
        submit_button.pack(padx=20, pady=30, anchor=tkinter.CENTER)
        return login_frame


def main():
    global login_frame
    login_frame = login(1)


def entry_as_user():
    global login_entry
    global password_entry
    cursor.execute("""SET search_path TO main,public;""")
    cursor.execute("""select check_login_and_password(%s, %s);""", (str(login_entry.get()),
                                                                    str(password_entry.get())))
    isExist = cursor.fetchone()
    if str(isExist[0]) == 'True':
        cursor.execute("""select check_role(%s, %s);""", (str(login_entry.get()),
                                                          str(password_entry.get())))
        post = cursor.fetchone()
        if str(post[0]) == 'admin':
            print('Вход под админом')
            cursor.execute("""SET ROLE admin""")
            administrator_window()
        elif str(post[0]) == 'manager':
            print('Вход под менеджером')
            cursor.execute("""SET ROLE %s;""", (str(login_entry.get()),))
            manager_window()
        elif str(post[0]) == 'employee':
            print('Вход под сотрудником')
            cursor.execute("""SET ROLE %s;""", (str(login_entry.get()),))
            employee_window()

        cursor.execute("""select current_user, session_user;""")
        print(f"Роль сессии {cursor.fetchall()}")


def administrator_window():
    def table_employee():
        print("Таблица сотрудники")
        cursor.execute('SELECT * FROM employee;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'task_id', 'deadline', 'assignment_date', 'task_description', 'priority', 'status')
        tree = ttk.Treeview(tabview.tab("Сотрудники"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('task_id', text='employee_id')
        tree.heading('deadline', text='ФИО')
        tree.heading('assignment_date', text='логин')
        tree.heading('task_description', text='пароль')
        tree.heading('priority', text='должность')
        tree.heading('status', text='pizzeria_id')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def table_pizzerias():
        print("Таблица пиццерии")
        cursor.execute('SELECT * FROM pizzerias;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'task_id', 'deadline', 'assignment_date', 'task_description', 'priority', 'status')
        tree = ttk.Treeview(tabview.tab("Пиццерии"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="nsew")
        # определяем заголовки
        tree.heading('task_id', text='ID')
        tree.heading('deadline', text='адрес')
        tree.heading('assignment_date', text='телефон')
        tree.heading('task_description', text='часы работы')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def refresh_tables():
        table_employee()
        table_pizzerias()

    login_frame.pack_forget()
    app.title("Администратор")
    width = 1200
    height = 700
    app.geometry("1200x700")
    administrator_frame = customtkinter.CTkFrame(master=app,
                                                 width=width,
                                                 height=height,
                                                 )
    administrator_frame.grid(row=0, column=0)
    create_employee_button = customtkinter.CTkButton(master=administrator_frame,
                                                     text="Добавить работника",
                                                     command=create_employee)
    create_employee_button.grid(row=0, column=0, pady=5, padx=10)
    create_pizzeria_button = customtkinter.CTkButton(master=administrator_frame,
                                                     text="Добавить пиццерию",
                                                     command=create_pizzeria)
    create_pizzeria_button.grid(row=1, column=0, sticky='we', pady=5, padx=10)
    refresh_tables_button = customtkinter.CTkButton(master=administrator_frame,
                                                    text='Обновить таблицы',
                                                    command=refresh_tables)
    refresh_tables_button.grid(row=2, column=0, sticky='we', pady=5, padx=10)

    tabview = customtkinter.CTkTabview(app)
    tabview.grid(row=0, column=1, padx=20, pady=20)

    tabview.add("Сотрудники")  # add tab at the end
    tabview.add("Пиццерии")  # add tab at the end
    tabview.set("Сотрудники")  # set currently visible tab

    table_employee()
    table_pizzerias()


def manager_window():
    def table_clients():
        print("Таблица клиентов")
        cursor.execute(
            'select * from client_info')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Клиенты"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='имя')
        tree.heading('phone_number', text='телефон')
        tree.heading('birthday', text='день рождения')
        tree.heading('email', text='email')
        tree.heading('scores', text='бонусные баллы')
        tree.heading('city', text='город')
        tree.heading('street', text='улица')
        tree.heading('house', text='дом')
        tree.heading('apartment', text='квартира')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def table_client_payments():
        print("Таблица cпособы оплаты")
        cursor.execute('select * from client_payments;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Способы оплаты"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='номер карты')
        tree.heading('phone_number', text='срок действия')
        tree.heading('birthday', text='cvv')
        tree.heading('email', text='client_id')
        tree.heading('scores', text='payment_id')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def table_menu():
        print("Таблица меню")
        cursor.execute('select * from menu;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Меню"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='pizza_id')
        tree.heading('phone_number', text='название')
        tree.heading('birthday', text='ингредиенты')
        tree.heading('email', text='цена')
        tree.heading('scores', text='наличие')
        tree.heading('city', text='pizzeria_id')
        tree.heading('street', text='weight')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def table_toppings():
        print("Таблица добавок")
        cursor.execute('select * from toppings;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Добавки"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='topping_id')
        tree.heading('phone_number', text='название')
        tree.heading('birthday', text='цена')
        tree.heading('email', text='вес')
        tree.heading('scores', text='product_id')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def refresh_tables():
        table_clients()
        table_client_payments()
        table_menu()
        table_toppings()
        orders_table()
        pizzerias_table()

    def orders_table():
        print("Таблица заказов")
        cursor.execute('select order_id,content,topping_content,creation_time,status,pizzeria_id from orders')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Заказы"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='order_id')
        tree.heading('phone_number', text='пицца')
        tree.heading('birthday', text='наполнители')
        tree.heading('email', text='creation_time')
        tree.heading('scores', text='status')
        tree.heading('city', text='pizzeria_id')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    def pizzerias_table():
        print("Таблица пиццерий")
        cursor.execute('select * from pizzerias;')
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'name', 'phone_number', 'birthday', 'email', 'scores', 'city', 'street', 'house', 'apartment')
        tree = ttk.Treeview(tabview.tab("Пиццерии"), columns=columns, show='headings')
        tree.grid(row=1, column=1, sticky="ns")
        # определяем заголовки
        tree.heading('name', text='pizzeria_id')
        tree.heading('phone_number', text='адрес')
        tree.heading('birthday', text='телефон')
        tree.heading('email', text='часы работы')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    login_frame.pack_forget()
    app.title("Менеджер")
    app.geometry("1480x700")

    tabview = customtkinter.CTkTabview(app)
    tabview.grid(row=0, column=0, padx=10, pady=10)

    tabview.add("Клиенты")
    tabview.add("Способы оплаты")
    tabview.add("Меню")
    tabview.add("Добавки")
    tabview.add("Заказы")
    tabview.add("Пиццерии")
    tabview.set("Клиенты")

    table_clients()
    table_client_payments()
    table_menu()
    table_toppings()
    orders_table()
    pizzerias_table()

    add_pizza_button = customtkinter.CTkButton(master=app, text='+Пицца', command=add_pizza)
    add_pizza_button.grid(row=1, column=0, sticky='w', pady=1, padx=3)
    add_topping_button = customtkinter.CTkButton(master=app, text='+Добавка', command=add_topping)
    add_topping_button.grid(row=2, column=0, sticky='w', pady=1, padx=3)
    add_client_button = customtkinter.CTkButton(master=app, text='+Клиент', command=add_client)
    add_client_button.grid(row=3, column=0, sticky='w', pady=1, padx=3)
    add_order_button = customtkinter.CTkButton(master=app, text='+Заказ', command=add_order)
    add_order_button.grid(row=4, column=0, sticky='w', pady=1, padx=3)
    refresh_tables_button = customtkinter.CTkButton(master=app, text='Обновить таблицы', command=refresh_tables)
    refresh_tables_button.grid(row=5, column=0, sticky='w', pady=1, padx=3)


def employee_window():
    def table_orders():
        cursor.execute(
            """select order_id,content,topping_content,creation_time,status,pizzeria_id from orders;""",
            (str(login_entry.get()),
             str(password_entry.get())
             ))
        tasks = cursor.fetchall()

        # определяем столбцы
        columns = (
            'task_id', 'deadline', 'assignment_date', 'task_description', 'priority', 'status')
        tree = ttk.Treeview(app, columns=columns, show='headings')
        tree.grid(row=0, column=0, sticky="wns")
        # определяем заголовки
        tree.heading('task_id', text='ID заказа')
        tree.heading('deadline', text='пицца')
        tree.heading('assignment_date', text='топпинги')
        tree.heading('task_description', text='время создания заказа')
        tree.heading('priority', text='статус')
        tree.heading('status', text='pizzeria_id')

        # добавляем данные
        for task in tasks:
            tree.insert("", END, values=task)

    login_frame.pack_forget()
    app.title("Сотрудник")
    app.geometry("1200x700")
    global login_entry
    global password_entry
    print(login_entry.get(), password_entry.get())
    print("Таблица сотрудника")

    table_orders()

    refresh_table_button = customtkinter.CTkButton(master=app, text='Обновить таблицу', command=table_orders)
    refresh_table_button.grid(row=1, column=0, padx=5, pady=10)


def create_employee():
    def submit():
        cursor.execute(f"""call register(%s, %s, %s, %s, %s);""", (str(full_name_entry.get()),
                                                                   str(employee_login_entry.get()),
                                                                   str(employee_password_entry.get()),
                                                                   int(pizzeria_id.get()),
                                                                   str(employee_post.get())
                                                                   ))

    create_employee_window = customtkinter.CTkToplevel()
    create_employee_window.geometry('400x400')
    create_employee_window.title('Добавление работника')
    full_name_entry = customtkinter.CTkEntry(master=create_employee_window, placeholder_text="ФИО")
    full_name_entry.grid(row=0, column=0, padx=5, pady=5)
    employee_login_entry = customtkinter.CTkEntry(master=create_employee_window, placeholder_text="логин")
    employee_login_entry.grid(row=1, column=0, padx=5, pady=5)
    employee_password_entry = customtkinter.CTkEntry(master=create_employee_window, placeholder_text="пароль")
    employee_password_entry.grid(row=2, column=0, padx=5, pady=5)

    employee_post = customtkinter.StringVar(value="manager")
    combobox_employee = customtkinter.CTkComboBox(master=create_employee_window,
                                                  values=["manager", "employee", "admin"],
                                                  variable=employee_post)
    combobox_employee.grid(row=0, column=1, padx=5, pady=5)

    cursor.execute("""select count(*) from pizzerias""")
    amount_of_pizzerias = int(cursor.fetchone()[0])
    print(f"количество пиццерий {amount_of_pizzerias}")
    cursor.execute("""select pizzeria_id from pizzerias""")
    pizzerias_id = cursor.fetchall()
    my_values = []
    for row in pizzerias_id:
        my_values.append(str(row[0]))
    print(f" массив {my_values}")

    def combobox_callback(choice):
        print("combobox dropdown clicked:", choice)
        print("get() clicked:", employee_post.get())

    pizzeria_id = customtkinter.IntVar(value=1)
    combobox_pizzeria = customtkinter.CTkComboBox(master=create_employee_window,
                                                  values=my_values,
                                                  variable=pizzeria_id,
                                                  command=combobox_callback)
    combobox_pizzeria.grid(row=1, column=1, padx=5, pady=5)
    submit_button = customtkinter.CTkButton(master=create_employee_window,
                                            text='Добавить',
                                            command=submit)
    submit_button.grid(row=3, column=0, columnspan=2, sticky='we')


def create_pizzeria():
    def submit():
        cursor.execute("""call create_pizzeria(%s, %s, %s);""", (str(pizzerias_address_entry.get()),
                                                                 str(phone_number_entry.get()),
                                                                 str(opening_hours_entry.get())))

    create_pizzeria_window = customtkinter.CTkToplevel()
    create_pizzeria_window.geometry('400x400')
    create_pizzeria_window.title('Добавление пиццерии')
    pizzerias_address_entry = customtkinter.CTkEntry(master=create_pizzeria_window,
                                                     placeholder_text="адрес пиццерии",
                                                     width=200)
    pizzerias_address_entry.grid(row=0, column=0, padx=5, pady=5)
    phone_number_entry = customtkinter.CTkEntry(master=create_pizzeria_window,
                                                placeholder_text="телефон",
                                                width=200,
                                                )
    phone_number_entry.grid(row=1, column=0, padx=5, pady=5)
    opening_hours_entry = customtkinter.CTkEntry(master=create_pizzeria_window,
                                                 placeholder_text="часы работы (00:00-12:00)",
                                                 width=200,
                                                 )
    opening_hours_entry.grid(row=2, column=0, padx=5, pady=5)
    submit_button = customtkinter.CTkButton(master=create_pizzeria_window,
                                            text='Добавить',
                                            command=submit)
    submit_button.grid(row=3, column=0, columnspan=2, sticky='we')


def add_pizza():
    def submit():
        cursor.execute(
            f"""call add_pizza(%s::varchar, %s::varchar, %s::smallint, %s, %s::smallint);""",
            (str(name_entry.get()),
             str(ingredients_entry.get()),
             int(cost_entry.get()),
             int(pizzeria_id.get()),
             int(weight_entry.get())
             ))

    add_pizza_window = customtkinter.CTkToplevel()
    add_pizza_window.geometry('400x400')
    add_pizza_window.title('Добавить в меню')
    name_entry = customtkinter.CTkEntry(master=add_pizza_window, placeholder_text="название")
    name_entry.grid(row=0, column=0, padx=5, pady=5)
    ingredients_entry = customtkinter.CTkEntry(master=add_pizza_window, placeholder_text="ингредиенты")
    ingredients_entry.grid(row=1, column=0, padx=5, pady=5)
    cost_entry = customtkinter.CTkEntry(master=add_pizza_window, placeholder_text="стоимость")
    cost_entry.grid(row=2, column=0, padx=5, pady=5)
    weight_entry = customtkinter.CTkEntry(master=add_pizza_window, placeholder_text="граммовка")
    weight_entry.grid(row=3, column=0, padx=5, pady=5)

    cursor.execute("""select count(*) from pizzerias""")
    amount_of_pizzerias = int(cursor.fetchone()[0])
    print(f"количество пиццерий {amount_of_pizzerias}")
    cursor.execute("""select pizzeria_id from pizzerias""")
    pizzerias_id = cursor.fetchall()
    my_values = []
    for row in pizzerias_id:
        my_values.append(str(row[0]))
    print(f" массив {my_values}")

    def combobox_callback(choice):
        print("combobox dropdown clicked:", choice)

    pizzeria_id = customtkinter.IntVar(value=1)
    combobox_pizzeria = customtkinter.CTkComboBox(master=add_pizza_window,
                                                  values=my_values,
                                                  variable=pizzeria_id,
                                                  command=combobox_callback)
    combobox_pizzeria.grid(row=0, column=1, padx=5, pady=5)
    submit_button = customtkinter.CTkButton(master=add_pizza_window,
                                            text='Добавить',
                                            command=submit
                                            )
    submit_button.grid(row=4, column=0, columnspan=2, sticky='we')


def add_topping():
    def submit():
        cursor.execute(f"""call add_topping(%s::varchar,%s::smallint,%s::smallint,%s);""",
                       (str(name_entry.get()),
                        int(cost_entry.get()),
                        int(weight_entry.get()),
                        int(pizzeria_id.get())
                        ))

    add_topping_window = customtkinter.CTkToplevel()
    add_topping_window.geometry('400x400')
    add_topping_window.title('Добавить топпинг')
    name_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="название")
    name_entry.grid(row=0, column=0, padx=5, pady=5)
    cost_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="стоимость")
    cost_entry.grid(row=2, column=0, padx=5, pady=5)
    weight_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="граммовка")
    weight_entry.grid(row=3, column=0, padx=5, pady=5)

    cursor.execute("""select count(*) from menu""")
    amount_of_pizzerias = int(cursor.fetchone()[0])
    print(f"количество пицц {amount_of_pizzerias}")
    cursor.execute("""select pizzeria_id from pizzerias""")
    pizzerias_id = cursor.fetchall()
    my_values = []
    for row in pizzerias_id:
        my_values.append(str(row[0]))
    print(f" массив {my_values}")

    def combobox_callback(choice):
        print("combobox dropdown clicked:", choice)

    pizzeria_id = customtkinter.IntVar(value=1)
    combobox_pizzeria = customtkinter.CTkComboBox(master=add_topping_window,
                                                  values=my_values,
                                                  variable=pizzeria_id,
                                                  command=combobox_callback)
    combobox_pizzeria.grid(row=0, column=1, padx=5, pady=5)
    submit_button = customtkinter.CTkButton(master=add_topping_window,
                                            text='Добавить',
                                            command=submit
                                            )
    submit_button.grid(row=4, column=0, columnspan=2, sticky='we')


def add_client():
    def submit():
        cursor.execute("""call create_client(%s,%s,%s,%s);""",
                       (str(name_entry.get()),
                        str(phone_number_entry.get()),
                        str(birthday_entry.get()),
                        str(email_entry.get())
                        ))
        cursor.execute("""select id from clients where name = %s;""", (
            str(name_entry.get()),
        ))
        client_id = cursor.fetchone()
        cursor.execute("""call add_client_address(%s::varchar, %s::varchar, %s::varchar, %s::smallint, %s::integer)""",
                       (
                           str(city_entry.get()),
                           str(street_entry.get()),
                           str(house_entry.get()),
                           int(apartment_entry.get()),
                           int(client_id[0])
                       ))

    add_topping_window = customtkinter.CTkToplevel()
    add_topping_window.geometry('400x400')
    add_topping_window.title('Добавить клиента')
    name_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="имя")
    name_entry.grid(row=0, column=0, padx=5, pady=5)
    phone_number_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="телефон")
    phone_number_entry.grid(row=1, column=0, padx=5, pady=5)
    birthday_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="день рождения")
    birthday_entry.grid(row=2, column=0, padx=5, pady=5)
    email_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="email")
    email_entry.grid(row=3, column=0, padx=5, pady=5)
    city_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="город")
    city_entry.grid(row=4, column=0, padx=5, pady=5)
    street_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="улица")
    street_entry.grid(row=0, column=1, padx=5, pady=5)
    house_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="дом")
    house_entry.grid(row=1, column=1, padx=5, pady=5)
    apartment_entry = customtkinter.CTkEntry(master=add_topping_window, placeholder_text="квартира")
    apartment_entry.grid(row=2, column=1, padx=5, pady=5)

    submit_button = customtkinter.CTkButton(master=add_topping_window,
                                            text='Добавить',
                                            command=submit
                                            )
    submit_button.grid(row=10, column=0, columnspan=2, sticky='we')


def add_order():
    def submit():
        role()
        result_content = [int(item) for item in content_entry.get().split()]
        result_topping_content = [int(item2) for item2 in topping_content_entry.get().split()]
        print(f"пиццы {result_content}")
        print(f"добавки {result_topping_content}")
        cursor.execute(
            """call create_order(%s,%s,%s,%s,%s,%s);""", (int(client_id_entry.get()),
                                                          int(address_id_entry.get()),
                                                          int(payment_id_entry.get()),
                                                          result_content,
                                                          result_topping_content,
                                                          int(pizzeria_id.get())))
        cursor.execute("""SET ROLE %s;""", (str(login_entry.get()),))

    add_order_window = customtkinter.CTkToplevel()
    add_order_window.geometry('400x400')
    add_order_window.title('Добавить заказ')
    client_id_entry = customtkinter.CTkEntry(master=add_order_window, placeholder_text="client_id")
    client_id_entry.grid(row=0, column=0, padx=5, pady=5)
    address_id_entry = customtkinter.CTkEntry(master=add_order_window, placeholder_text="address_id")
    address_id_entry.grid(row=1, column=0, padx=5, pady=5)
    payment_id_entry = customtkinter.CTkEntry(master=add_order_window, placeholder_text="payment_id")
    payment_id_entry.grid(row=2, column=0, padx=5, pady=5)
    content_entry = customtkinter.CTkEntry(master=add_order_window, placeholder_text="content")
    content_entry.grid(row=3, column=0, padx=5, pady=5)
    topping_content_entry = customtkinter.CTkEntry(master=add_order_window, placeholder_text="topping_content")
    topping_content_entry.grid(row=4, column=0, padx=5, pady=5)

    submit_button = customtkinter.CTkButton(master=add_order_window,
                                            text='Добавить',
                                            command=submit
                                            )
    submit_button.grid(row=10, column=0, columnspan=2, sticky='we')

    cursor.execute("""select pizzeria_id from pizzerias""")
    pizzerias_id = cursor.fetchall()
    my_values = []
    for row in pizzerias_id:
        my_values.append(str(row[0]))
    print(f" массив {my_values}")

    def combobox_callback(choice):
        print("combobox dropdown clicked:", choice)

    pizzeria_id = customtkinter.IntVar(value=1)
    combobox_pizzeria = customtkinter.CTkComboBox(master=add_order_window,
                                                  values=my_values,
                                                  variable=pizzeria_id,
                                                  command=combobox_callback)
    combobox_pizzeria.grid(row=0, column=1, padx=5, pady=5)


def role():
    cursor.execute("""SET ROLE %s;""", ('postgres',))


main()
app.mainloop()
