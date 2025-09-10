import tkinter as tk
from tkinter import messagebox
import re

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def parse_time(tstr):
    """
    Parse time string in HH:MM format (24h) into float hours (e.g. '13:30' -> 13.5).
    Returns float or raises ValueError.
    """
    pattern = r'^([01]?\d|2[0-3]):([0-5]\d)$'
    match = re.match(pattern, tstr)
    if not match:
        raise ValueError("Time must be in HH:MM 24-hour format")
    hour = int(match.group(1))
    minute = int(match.group(2))
    return hour + minute / 60

def times_overlap(start1, end1, start2, end2):
    """Return True if two time intervals overlap."""
    return not (end1 <= start2 or end2 <= start1)

class ClassSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Scheduler")

        self.classes = []  # store classes as dicts: {name, start, end, days}

        # Input fields
        tk.Label(root, text="Class Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1, columnspan=3, sticky="we")

        tk.Label(root, text="Start Time (HH:MM 24h):").grid(row=1, column=0, sticky="w")
        self.start_entry = tk.Entry(root)
        self.start_entry.grid(row=1, column=1, sticky="we")

        tk.Label(root, text="End Time (HH:MM 24h):").grid(row=1, column=2, sticky="w")
        self.end_entry = tk.Entry(root)
        self.end_entry.grid(row=1, column=3, sticky="we")

        tk.Label(root, text="Days:").grid(row=2, column=0, sticky="w")
        self.day_vars = []
        for i, day in enumerate(DAYS):
            var = tk.IntVar()
            cb = tk.Checkbutton(root, text=day, variable=var)
            cb.grid(row=2, column=1+i)
            self.day_vars.append(var)

        self.add_button = tk.Button(root, text="Add Class", command=self.add_class)
        self.add_button.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")

        self.class_listbox = tk.Listbox(root, width=80)
        self.class_listbox.grid(row=4, column=0, columnspan=8, sticky="we", padx=5)

        self.select_button = tk.Button(root, text="Select Non-Overlapping Classes", command=self.select_classes)
        self.select_button.grid(row=5, column=0, columnspan=8, pady=5, sticky="we")

        self.result_text = tk.Text(root, height=10, width=80)
        self.result_text.grid(row=6, column=0, columnspan=8, sticky="we", padx=5)

        # Make columns resize nicely
        for i in range(8):
            root.grid_columnconfigure(i, weight=1)

    def add_class(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Invalid Input", "Class name cannot be empty.")
            return
        try:
            start = parse_time(self.start_entry.get().strip())
            end = parse_time(self.end_entry.get().strip())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        if start >= end:
            messagebox.showerror("Invalid Input", "Start time must be before end time.")
            return
        days = [DAYS[i] for i, var in enumerate(self.day_vars) if var.get() == 1]
        if not days:
            messagebox.showerror("Invalid Input", "Select at least one day.")
            return

        # Check for conflicts
        for existing in self.classes:
            shared_days = set(days).intersection(existing['days'])
            if shared_days and times_overlap(start, end, existing['start'], existing['end']):
                conflict_days = ", ".join(shared_days)
                messagebox.showwarning(
                    "Time Conflict",
                    f"Class conflicts with existing class '{existing['name']}' on {conflict_days}."
                )
                return

        # Add class
        self.classes.append({"name": name, "start": start, "end": end, "days": days})
        self.update_class_list()

        # Clear inputs
        self.name_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        for var in self.day_vars:
            var.set(0)

    def update_class_list(self):
        self.class_listbox.delete(0, tk.END)
        for c in self.classes:
            start_hr = int(c['start'])
            start_min = int((c['start'] - start_hr) * 60)
            end_hr = int(c['end'])
            end_min = int((c['end'] - end_hr) * 60)
            start_str = f"{start_hr:02d}:{start_min:02d}"
            end_str = f"{end_hr:02d}:{end_min:02d}"
            self.class_listbox.insert(tk.END, f"{c['name']}: {start_str} - {end_str} on {', '.join(c['days'])}")

    def select_classes(self):
        selected = []
        for day in DAYS:
            day_classes = [c for c in self.classes if day in c['days']]
            day_classes.sort(key=lambda x: x['end'])
            last_end = -1
            for c in day_classes:
                if c['start'] >= last_end:
                    selected.append((day, c))
                    last_end = c['end']

        selected.sort(key=lambda x: (DAYS.index(x[0]), x[1]['start']))

        self.result_text.delete(1.0, tk.END)
        if not selected:
            self.result_text.insert(tk.END, "No classes selected.")
            return
        current_day = None
        for day, c in selected:
            if day != current_day:
                self.result_text.insert(tk.END, f"\n{day}:\n")
                current_day = day
            start_hr = int(c['start'])
            start_min = int((c['start'] - start_hr) * 60)
            end_hr = int(c['end'])
            end_min = int((c['end'] - end_hr) * 60)
            start_str = f"{start_hr:02d}:{start_min:02d}"
            end_str = f"{end_hr:02d}:{end_min:02d}"
            self.result_text.insert(tk.END, f"  {c['name']}: {start_str} - {end_str}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassSchedulerApp(root)
    root.mainloop()