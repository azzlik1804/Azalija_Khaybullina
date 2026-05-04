import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import json
import os

# Константы
HISTORY_FILE = "tasks.json"
VALID_CATEGORIES = ["учёба", "спорт", "работа"]

# Начальный список задач
DEFAULT_TASKS = [
    {"task": "Прочитать статью", "category": "учёба"},
    {"task": "Сделать зарядку", "category": "спорт"},
    {"task": "Написать отчёт", "category": "работа"},
    {"task": "Выучить 10 слов", "category": "учёба"},
    {"task": "Пробежать 3 км", "category": "спорт"},
    {"task": "Разобрать почту", "category": "работа"},
]

# --- Работа с файлами (ИСПРАВЛЕНИЕ ОШИБОК) ---

def load_history():
    """Безопасная загрузка истории. Если файл пуст или битый — возвращает пустой список."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []  # Файл пуст
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return []  # Файл поврежден

def save_history(history):
    """Сохранение истории с обработкой ошибок."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
        return False

def init_file():
    """Создает файл истории, если его нет."""
    if not os.path.exists(HISTORY_FILE):
        save_history([])

# --- Логика приложения ---

def generate_task():
    """Генерирует случайную задачу с учетом фильтра."""
    category_filter = category_var.get()
    
    # Фильтрация
    if category_filter == "Все":
        pool = DEFAULT_TASKS
    else:
        pool = [t for t in DEFAULT_TASKS if t["category"] == category_filter]

    if not pool:
        messagebox.showwarning("Внимание", "Нет задач в выбранной категории!")
        return

    # Выбор случайной
    task = random.choice(pool)
    task_str = f"{task['task']} [{task['category']}]"
    
    # Обновление интерфейса
    current_task_label.config(text=task_str, fg="#2c3e50")
    
    # Сохранение в историю
    history = load_history()
    history.append(task_str)
    save_history(history)
    update_history_list()

def add_new_task():
    """Добавляет новую задачу с проверкой ввода."""
    # 1. Ввод названия
    new_task_name = simpledialog.askstring("Новая задача", "Введите текст задачи:")
    if not new_task_name or not new_task_name.strip():
        messagebox.showerror("Ошибка", "Задача не может быть пустой!")
        return

    # 2. Выбор категории (через диалоговое окно с выбором, чтобы избежать ошибок ввода)
    category_window = tk.Toplevel(root)
    category_window.title("Категория")
    category_window.geometry("300x150")
    category_window.transient(root)
    category_window.grab_set() # Блокируем основное окно

    tk.Label(category_window, text="Выберите категорию:").pack(pady=10)
    
    cat_var = tk.StringVar(value=VALID_CATEGORIES[0])
    combo = ttk.Combobox(category_window, textvariable=cat_var, values=VALID_CATEGORIES, state="readonly")
    combo.pack(pady=5)

    def confirm_add():
        selected_cat = cat_var.get()
        # Добавляем в общий список
        DEFAULT_TASKS.append({"task": new_task_name.strip(), "category": selected_cat})
        messagebox.showinfo("Успех", f"Задача '{new_task_name}' добавлена!")
        category_window.destroy()

    tk.Button(category_window, text="Добавить", command=confirm_add).pack(pady=10)

def update_history_list():
    """Обновляет Listbox с историей."""
    history_listbox.delete(0, tk.END)
    history = load_history()
    # Показываем сверху вниз (новые сверху)
    for item in reversed(history):
        history_listbox.insert(tk.END, item)

def clear_history():
    """Очищает историю."""
    if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
        save_history([])
        update_history_list()
        current_task_label.config(text="История очищена", fg="#7f8c8d")

# --- Интерфейс (GUI) ---

root = tk.Tk()
root.title("Random Task Generator")
root.geometry("600x500")
root.configure(bg="#f0f0f0")

# Инициализация файла при запуске
init_file()

# Заголовок
tk.Label(root, text="🎲 Генератор Задач", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

# Область текущей задачи
current_task_label = tk.Label(root, text="Нажмите кнопку ниже", font=("Arial", 14), bg="#f0f0f0", wraplength=500)
current_task_label.pack(pady=10)

# Панель управления
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(pady=5)

# Фильтр категорий
tk.Label(control_frame, text="Категория:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
category_var = tk.StringVar(value="Все")
category_combo = ttk.Combobox(control_frame, textvariable=category_var, values=["Все"] + VALID_CATEGORIES, state="readonly")
category_combo.pack(side=tk.LEFT, padx=5)

# Кнопки
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Сгенерировать", command=generate_task, bg="#3498db", fg="white", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Добавить задачу", command=add_new_task, bg="#2ecc71", fg="white", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Очистить историю", command=clear_history, bg="#e74c3c", fg="white", width=15).pack(side=tk.LEFT, padx=5)

# История
tk.Label(root, text="📜 История:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(10, 5))

history_listbox = tk.Listbox(root, width=60, height=10, font=("Arial", 10))
history_listbox.pack(pady=5)

# Загрузка истории при старте
update_history_list()

root.mainloop()
