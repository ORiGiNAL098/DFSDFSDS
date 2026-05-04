import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

DATA_FILE = "weather_data.json"


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")

        self.entries = []  # Список записей
        self.load_from_file()

        # === Поля ввода ===
        input_frame = ttk.LabelFrame(root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5)

        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=0, column=6, padx=5)

        add_btn = ttk.Button(input_frame, text="➕ Добавить запись", command=self.add_entry)
        add_btn.grid(row=0, column=7, padx=10)

        # === Фильтры ===
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Температура выше:").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)
        ttk.Label(filter_frame, text="°C").grid(row=0, column=4)

        filter_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=5, padx=10)

        reset_btn = ttk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter)
        reset_btn.grid(row=0, column=6)

        # === Таблица для отображения ===
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопка сохранения
        save_btn = ttk.Button(root, text="💾 Сохранить в JSON", command=self.save_to_file)
        save_btn.pack(pady=(0, 10))

        self.refresh_table(self.entries)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2025-04-01)")
            return
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        entry = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        self.entries.append(entry)
        self.refresh_table(self.entries)
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in data:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.entries[:]

        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
                return
            filtered = [e for e in filtered if e["date"] == filter_date]

        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [e for e in filtered if e["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр температуры должен быть числом")
                return

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table(self.entries)

    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.entries = []
        else:
            self.entries = []


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
