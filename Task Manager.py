import mysql.connector
import bcrypt
from tkinter import *
from tkinter import simpledialog, messagebox, ttk
from tkcalendar import DateEntry
import customtkinter


# Base class for database connection
class DBConnection:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2004',
            database='todo_app'
        )

    def close_connection(self):
        self.conn.close()

# User class with MySQL integration
class User(DBConnection):
    def __init__(self, username, password=None, password_hash=None):
        super().__init__()
        self.username = username
        if password:
            self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        else:
            self.password_hash = password_hash

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash)

# Task class remains unchanged
class Task:
    def __init__(self, name, priority, category, deadline):
        self.name = name
        self.priority = priority
        self.category = category
        self.deadline = deadline
        self.completed = False

    def __repr__(self):
        status = "Completed" if self.completed else "Pending"
        return f"Task: {self.name}, Priority: {self.priority}, Category: {self.category}, Deadline: {self.deadline}, Status: {status}"

# ToDoList class with MySQL integration
class ToDoList(DBConnection):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.tasks = self.load_tasks()

    def load_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, priority, category, deadline, completed FROM tasks WHERE username=%s', (self.username,))
        tasks = cursor.fetchall()
        task_list = []
        for row in tasks:
            task = Task(row[0], row[1], row[2], row[3])
            task.completed = row[4]
            task_list.append(task)
        return task_list

    def add_task(self, task):
        self.tasks.append(task)
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO tasks (name, priority, category, deadline, completed, username)
                          VALUES (%s, %s, %s, %s, %s, %s)''',
                       (task.name, task.priority, task.category, task.deadline, task.completed, self.username))
        self.conn.commit()

    def mark_task_as_complete(self, task_index):
        if 1 <= task_index <= len(self.tasks):
            task = self.tasks[task_index - 1]
            task.completed = True
            cursor = self.conn.cursor()
            cursor.execute('UPDATE tasks SET completed=1 WHERE name=%s AND username=%s', (task.name, self.username))
            self.conn.commit()
            return f"Task '{task.name}' marked as complete."
        else:
            return "Invalid task index."

    def show_tasks(self):
        if not self.tasks:
            return "No tasks in the list."
        else:
            return "\n".join([f"Task: {task.name}, Priority: {task.priority}, Category: {task.category}, Deadline: {task.deadline}, Status: {'Completed' if task.completed else 'Pending'}" for task in self.tasks])

# Function to read users from the database
def read_users_from_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='2004',
        database='todo_app'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT username, password_hash FROM users')
    users = cursor.fetchall()
    conn.close()
    return [User(row[0], password_hash=row[1]) for row in users]

# Function to write a user to the database
def write_user_to_db(user):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2004',
            database='todo_app'
        )
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)',
                       (user.username, user.password_hash))
        conn.commit()
        conn.close()
    except mysql.connector.errors.IntegrityError as e:
        print(f"Error: {e}")
        return False
    return True

# Function to initialize the database
def init_db():
    try:
        # Connect to MySQL server (no database specified)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2004'
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute('CREATE DATABASE IF NOT EXISTS todo_app')
        conn.commit()
        conn.close()

        # Connect to the 'todo_app' database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='2004',
            database='todo_app'
        )
        cursor = conn.cursor()

        # Create 'users' table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) NOT NULL UNIQUE,
                            password_hash BLOB NOT NULL)''')

        # Create 'tasks' table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            priority VARCHAR(50) NOT NULL,
                            category VARCHAR(50) NOT NULL,
                            deadline DATE NOT NULL,
                            completed BOOLEAN NOT NULL DEFAULT 0,
                            username VARCHAR(255) NOT NULL,
                            FOREIGN KEY (username) REFERENCES users (username))''')

        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

# GUI for the application using custom Tkinter
class ToDoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("ToDo Application")
        self.geometry("660x600")
        self.resizable(False, False)
        self.username = None
        self.db_connection = DBConnection()

        self.login_frame = self.create_login_frame()
        self.todo_frame = None

    def create_login_frame(self):
        frame = customtkinter.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = customtkinter.CTkLabel(frame, text="To-Do Task Manager", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)

        username_label = customtkinter.CTkLabel(frame, text="Username:")
        username_label.pack(pady=5)
        self.username_entry = customtkinter.CTkEntry(frame)
        self.username_entry.pack(pady=5)

        password_label = customtkinter.CTkLabel(frame, text="Password:\nMust 6 Charactar long\nOne Uppercase Letter & One Lowercase Letter\nOne Special Charactar(!,@,#,$,%,&,*S)")
        password_label.pack(pady=5)
        self.password_entry = customtkinter.CTkEntry(frame, show="*")
        self.password_entry.pack(pady=5)

        login_button = customtkinter.CTkButton(frame, text="Login", command=self.login)
        login_button.pack(pady=10)

        register_button = customtkinter.CTkButton(frame, text="Register", command=self.register)
        register_button.pack(pady=10)

        exit_button = customtkinter.CTkButton(frame, text="Exit", command=self.exit_app)
        exit_button.pack(pady=10)

        return frame

    def create_todo_frame(self):
        frame = customtkinter.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        label = customtkinter.CTkLabel(frame, text=f"Welcome, {self.username}", font=("Arial", 20))
        label.pack(pady=10)

        # Create a frame to contain the Treeview and the scrollbar
        tree_frame = Frame(frame)
        tree_frame.pack(pady=10, fill="both", expand=True)

        # Create Treeview widget
        self.task_treeview = ttk.Treeview(tree_frame, columns=("Name", "Priority", "Category", "Deadline", "Status"))
        self.task_treeview.heading("#0", text="ID")
        self.task_treeview.heading("Name", text="Name")
        self.task_treeview.heading("Priority", text="Priority")
        self.task_treeview.heading("Category", text="Category")
        self.task_treeview.heading("Deadline", text="Deadline")
        self.task_treeview.heading("Status", text="Status")
        self.task_treeview.pack(side="left", fill="both", expand=True)

        self.task_treeview.column("#0", width=35)
        self.task_treeview.column("Name", minwidth=100, width=100)
        self.task_treeview.column("Priority", minwidth=100, width=100)
        self.task_treeview.column("Category", minwidth=100, width=100)
        self.task_treeview.column("Deadline", minwidth=100, width=100)
        self.task_treeview.column("Status", minwidth=100, width=100)

        # Create a vertical scrollbar
        scrollbar = Scrollbar(tree_frame, orient="vertical", command=self.task_treeview.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Treeview to use the scrollbar
        self.task_treeview.configure(yscrollcommand=scrollbar.set)

        show_tasks_button = customtkinter.CTkButton(frame, text="Show Tasks", command=self.show_tasks)
        show_tasks_button.pack(pady=10)

        add_task_button = customtkinter.CTkButton(frame, text="Add Task", command=self.open_task_window)
        add_task_button.pack(pady=10)

        mark_complete_button = customtkinter.CTkButton(frame, text="Mark Complete", command=self.mark_task_complete)
        mark_complete_button.pack(pady=10)

        logout_button = customtkinter.CTkButton(frame, text="Logout", command=self.logout)
        logout_button.pack(pady=10)

        return frame


    def open_task_window(self):
        task_window = Toplevel(self)
        task_window.title("Add Task")
        task_window.geometry("300x450")

        # Task name entry
        task_name_label = Label(task_window, text="Task Name:")
        task_name_label.pack()
        self.task_name_entry = Entry(task_window)
        self.task_name_entry.pack()

        # Priority entry
        priority_label = Label(task_window, text="Priority:")
        priority_label.pack()
        self.priority = customtkinter.CTkComboBox(task_window, values=["High", "Normal", "Low"])
        self.priority.pack()

        # Category entry
        category_label = Label(task_window, text="Category:")
        category_label.pack()
        self.category = customtkinter.CTkComboBox(task_window, values=["Education", "Work", "Home"])
        self.category.pack()

        # Deadline entry
        deadline_label = Label(task_window, text="Deadline (YYYY-MM-DD):")
        deadline_label.pack()
        self.deadline_entry = DateEntry(task_window, date_pattern="yyyy-mm-dd")
        self.deadline_entry.pack()

        # Add Task button
        add_task_button = Button(task_window, text="Add Task", command=self.add_task_from_window)
        add_task_button.pack(pady=10)

    def add_task_from_window(self):
        name = self.task_name_entry.get()
        priority = self.priority.get()
        category = self.category.get()
        deadline = self.deadline_entry.get()

        if name and priority and category and deadline:
            task = Task(name, priority, category, deadline)
            todo_list = ToDoList(self.username)
            todo_list.add_task(task)
            self.update_task_listbox()
            messagebox.showinfo("Task Added", "Task added successfully!")
        else:
            messagebox.showerror("Error", "All fields are required to add a task")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        users = read_users_from_db()
        for user in users:
            if user.username == username and user.verify_password(password):
                self.username = username
                self.login_frame.pack_forget()
                self.todo_frame = self.create_todo_frame()
                self.todo_frame.pack(pady=20, padx=20, fill="both", expand=True)
                return
        messagebox.showerror("Login Failed", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Password requirements
        if len(password) < 6:
            messagebox.showerror("Registration Failed", "Password must be at least 6 characters long")
            return
        if not any(char.isupper() for char in password):
            messagebox.showerror("Registration Failed", "Password must contain at least one uppercase letter")
            return
        if not any(char.islower() for char in password):
            messagebox.showerror("Registration Failed", "Password must contain at least one lowercase letter")
            return
        if not any(char in "!@#$%^&*()-_+=~`[]{}|:;'<>,.?/" for char in password):
            messagebox.showerror("Registration Failed", "Password must contain at least one special character")
            return

        # Other registration checks
        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and password cannot be empty")
            return

        users = read_users_from_db()
        if any(user.username == username for user in users):
            messagebox.showerror("Registration Failed", "Username already exists")
            return

        new_user = User(username, password)
        if write_user_to_db(new_user):
            messagebox.showinfo("Registration Successful", "User registered successfully!")
        else:
            messagebox.showerror("Registration Failed", "Failed to register user")

    def add_task(self):
        name = simpledialog.askstring("Task Name", "Enter task name:")
        priority = simpledialog.askstring("Task Priority", "Enter priority:")
        category = simpledialog.askstring("Task Category", "Enter category:")
        deadline = simpledialog.askstring("Task Deadline", "Enter deadline:")

        if name and priority and category and deadline:
            task = Task(name, priority, category, deadline)
            todo_list = ToDoList(self.username)
            todo_list.add_task(task)
            self.update_task_listbox()
            messagebox.showinfo("Task Added", "Task added successfully!")
        else:
            messagebox.showerror("Error", "All fields are required to add a task")

    def mark_task_complete(self):
        selected_item = self.task_treeview.selection()
        if selected_item:
            task_index = self.task_treeview.index(selected_item[0])
            todo_list = ToDoList(self.username)
            message = todo_list.mark_task_as_complete(task_index + 1)
            self.update_task_listbox()
            messagebox.showinfo("Task Update", message)
        else:
            messagebox.showerror("Error", "No task selected")

    def logout(self):
        self.todo_frame.pack_forget()
        self.login_frame = self.create_login_frame()
        self.login_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.username = None

    def exit_app(self):
        self.db_connection.close_connection()
        self.quit()

    def update_task_listbox(self):
        self.task_treeview.delete(*self.task_treeview.get_children())
        todo_list = ToDoList(self.username)
        tasks = todo_list.tasks
        for index, task in enumerate(tasks, start=1):
            status = "Completed" if task.completed else "Pending"
            self.task_treeview.insert("", index, text=index, values=(task.name, task.priority, task.category, task.deadline, status))


    def show_tasks(self):
        self.update_task_listbox()

if __name__ == "__main__":
    init_db()
    customtkinter.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"
    app = ToDoApp()
    app.mainloop()
