# Author: Jack lidster
# Date: 2023-11-10
# Description: GUI version using tkinter for the COSC-1100 combined programs.

import math
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- Utility ----------------

def safe_int(value, default=0):
    try:
        return int(value)
    except:
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

# ---------------- Frames ----------------

class DogGroomingFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.basic_var = tk.StringVar()
        self.full_var = tk.StringVar()
        self.deluxe_var = tk.StringVar()
        self.output = tk.Text(self, height=8, width=60)

        ttk.Label(self, text="Basic wash count").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.basic_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(self, text="Full groom count").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.full_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(self, text="Deluxe spa count").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.deluxe_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=8)
        self.output.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

    def calculate(self):
        TIME_PER_HOUR = 60
        BASIC_TIME, BASIC_COST = 30, 35
        FULL_TIME, FULL_COST = 60, 50
        DELUXE_TIME, DELUXE_COST = 90, 70

        basic_washes = safe_int(self.basic_var.get())
        full_washes = safe_int(self.full_var.get())
        deluxe_washes = safe_int(self.deluxe_var.get())

        total_hours_for_basic = (basic_washes * BASIC_TIME) / TIME_PER_HOUR
        total_cost_for_basic = basic_washes * BASIC_COST

        total_hours_for_full = (full_washes * FULL_TIME) / TIME_PER_HOUR
        total_cost_for_full = full_washes * FULL_COST

        total_time_for_deluxe = deluxe_washes * DELUXE_TIME
        total_hours_for_deluxe = total_time_for_deluxe / TIME_PER_HOUR
        total_cost_for_deluxe = deluxe_washes * DELUXE_COST

        total_hours = total_hours_for_basic + total_hours_for_full + total_hours_for_deluxe
        total_cost = total_cost_for_basic + total_cost_for_full + total_cost_for_deluxe

        self.output.delete("1.0", "end")
        self.output.insert("end", f"Basic: {total_hours_for_basic:.2f} hrs, ${total_cost_for_basic:.2f}\n")
        self.output.insert("end", f"Full: {total_hours_for_full:.2f} hrs, ${total_cost_for_full:.2f}\n")
        self.output.insert("end", f"Deluxe: {total_hours_for_deluxe:.2f} hrs, ${total_cost_for_deluxe:.2f}\n")
        self.output.insert("end", f"Total: {total_hours:.2f} hrs, Revenue ${total_cost:.2f}\n")


class HorseTrackFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.outer_radius = tk.StringVar()
        self.inner_radius = tk.StringVar()
        self.length = tk.StringVar()
        self.width = tk.StringVar()
        self.result = tk.StringVar()

        self._mk_row("Outer radius (m)", self.outer_radius, 0)
        self._mk_row("Inner radius (m)", self.inner_radius, 1)
        self._mk_row("Length straight (m)", self.length, 2)
        self._mk_row("Width (m)", self.width, 3)

        ttk.Button(self, text="Calculate area", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Label(self, textvariable=self.result).grid(row=5, column=0, columnspan=2, sticky="w")

    def _mk_row(self, label, var, r):
        ttk.Label(self, text=label).grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=var, width=12).grid(row=r, column=1, sticky="w")

    def calculate(self):
        PI = math.pi
        try:
            outer_radius = float(self.outer_radius.get())
            inner_radius = float(self.inner_radius.get())
            length = float(self.length.get())
            width = float(self.width.get())
        except:
            messagebox.showerror("Error", "Enter valid numbers.")
            return

        outer_circle_area = PI * (outer_radius ** 2)
        inner_circle_area = PI * (inner_radius ** 2)
        rectangle_area = length * width
        track_area = (outer_circle_area - inner_circle_area) + rectangle_area
        self.result.set(f"Track area: {track_area:.2f} m²")


class CalculatorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.expr = tk.StringVar()
        self.output = tk.StringVar()

        ttk.Label(self, text="One-digit equation (e.g., 2+3)").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.expr, width=20).grid(row=0, column=1, sticky="w")
        ttk.Button(self, text="Compute", command=self.compute).grid(row=1, column=0, columnspan=2, pady=8)
        ttk.Label(self, textvariable=self.output).grid(row=2, column=0, columnspan=2, sticky="w")

    def compute(self):
        not_valid_three_digit_number = "Enter a valid three-char equation (0-9 op 0-9)."
        not_valid_operator = "Enter a valid operator (+,-,*,/)."
        can_not_divide_by_zero = "You cannot divide by zero."
        valid_operators = ['+', '-', '*', '/']

        user_input = self.expr.get().strip()
        if user_input == "🐫/2":
            self.output.set("🐫 / 2 = 🐪")
            return

        if len(user_input) != 3 or (not user_input[0].isnumeric()) or (not user_input[2].isnumeric()):
            self.output.set(not_valid_three_digit_number)
            return
        if user_input[1] not in valid_operators:
            self.output.set(not_valid_operator)
            return

        first_digit = int(user_input[0])
        operator = user_input[1]
        second_digit = int(user_input[2])

        if operator == "+":
            self.output.set(f"{first_digit} + {second_digit} = {first_digit + second_digit}")
        elif operator == "-":
            self.output.set(f"{first_digit} - {second_digit} = {first_digit - second_digit}")
        elif operator == "*":
            self.output.set(f"{first_digit} * {second_digit} = {first_digit * second_digit}")
        elif operator == "/":
            if second_digit == 0:
                self.output.set(can_not_divide_by_zero)
            else:
                self.output.set(f"{first_digit} / {second_digit} = {first_digit / second_digit}")


class MilkshakesFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.chocolate = tk.StringVar()
        self.vanilla = tk.StringVar()
        self.strawberry = tk.StringVar()
        self.output = tk.Text(self, height=6, width=60)

        self._mk_row("Chocolate count", self.chocolate, 0)
        self._mk_row("Vanilla count", self.vanilla, 1)
        self._mk_row("Strawberry count", self.strawberry, 2)

        ttk.Button(self, text="Tally", command=self.tally).grid(row=3, column=0, columnspan=2, pady=8)
        self.output.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

    def _mk_row(self, label, var, r):
        ttk.Label(self, text=label).grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=var, width=12).grid(row=r, column=1, sticky="w")

    def tally(self):
        c = safe_int(self.chocolate.get())
        v = safe_int(self.vanilla.get())
        s = safe_int(self.strawberry.get())
        total = c + v + s

        self.output.delete("1.0", "end")
        if total == 0:
            self.output.insert("end", "No numbers entered yet.\n")
            return

        cp = (c / total) * 100
        vp = (v / total) * 100
        sp = (s / total) * 100
        self.output.insert("end", f"Total: {total}\n")
        self.output.insert("end", f"Chocolate: {c} ({cp:.1f}%)\n")
        self.output.insert("end", f"Vanilla: {v} ({vp:.1f}%)\n")
        self.output.insert("end", f"Strawberry: {s} ({sp:.1f}%)\n")


class PizzaCalculatorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.diameter = tk.StringVar()
        self.output = tk.Text(self, height=6, width=60)

        ttk.Label(self, text='Diameter (")').grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.diameter, width=12).grid(row=0, column=1, sticky="w")
        ttk.Button(self, text="Calculate slices", command=self.calculate).grid(row=1, column=0, columnspan=2, pady=8)
        self.output.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

    def calculate(self):
        MAX_DIAMETER = 24
        MIN_DIAMETER = 8
        SMALL_SLICE = 6
        SMALL_SIZE = 8
        MEDIUM_SLICE = 8
        MEDIUM_SIZE = 12
        LARGE_SLICE = 10
        LARGE_SIZE = 14
        EXTRA_LARGE_SLICE = 12
        EXTRA_LARGE_SIZE = 16
        EXTRA_EXTRA_LARGE_SLICE = 14
        EXTRA_EXTRA_LARGE_SIZE = 20
        MAX_SLICE = 16
        MAX_SIZE = 24

        self.output.delete("1.0", "end")
        try:
            d = float(self.diameter.get())
        except:
            self.output.insert("end", "Invalid input. Enter a number.\n")
            return

        if not (MIN_DIAMETER <= d <= MAX_DIAMETER):
            self.output.insert("end", f'Enter diameter in range {MIN_DIAMETER}" to {MAX_DIAMETER}"\n')
            return

        di = int(d)
        slices = []
        if SMALL_SIZE <= di < MEDIUM_SIZE:
            slices = [SMALL_SLICE]
        elif MEDIUM_SIZE <= di < LARGE_SIZE:
            slices = [SMALL_SLICE, MEDIUM_SLICE]
        elif LARGE_SIZE <= di < EXTRA_LARGE_SIZE:
            slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE]
        elif EXTRA_LARGE_SIZE <= di < EXTRA_EXTRA_LARGE_SIZE:
            slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE]
        elif EXTRA_EXTRA_LARGE_SIZE <= di <= MAX_SIZE:
            slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE, MAX_SLICE]

        if not slices:
            self.output.insert("end", "No slice configuration for this diameter.\n")
            return

        area = math.pi * (d / 2) ** 2
        for slice_count in slices:
            slice_area = area / slice_count
            self.output.insert(
                "end",
                f'Pizza diameter: {d:.0f}" — Total area: {area:.2f} in² — {slice_count} slices -> {slice_area:.2f} in² per slice\n'
            )

class ListFunctionsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.input_list = tk.StringVar()
        self.output = tk.Text(self, height=6, width=60)

        ttk.Label(self, text="Enter numbers separated by commas").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.input_list, width=40).grid(row=0, column=1, sticky="w")
        ttk.Button(self, text="Process", command=self.process).grid(row=1, column=0, columnspan=2, pady=8)
        self.output.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

    def is_list_numeric(self, input_list):
        for item in input_list:
            if not isinstance(item, (int, float)):
                return False
        return True

    def cap_list(self, list_to_cap, min_value, max_value):
        return [min(max(v, min_value), max_value) for v in list_to_cap]

    def drop_highest_and_lowest(self, input_list):
        if len(input_list) <= 2:
            return []
        s = sorted(input_list)
        return s[1:-1]

    def process(self):
        MIN_VALUE, MAX_VALUE = 0, 100
        self.output.delete("1.0", "end")

        try:
            items = [i.strip() for i in self.input_list.get().split(",") if i.strip() != ""]
            values = [float(i) if "." in i else int(i) for i in items]
        except:
            self.output.insert("end", "Enter a valid comma-separated list of numbers.\n")
            return

        if not self.is_list_numeric(values):
            self.output.insert("end", "List contains non-numeric values.\n")
            return

        capped = self.cap_list(values, MIN_VALUE, MAX_VALUE)
        result = self.drop_highest_and_lowest(capped)
        self.output.insert("end", f"Input: {values}\n")
        self.output.insert("end", f"Capped: {capped}\n")
        self.output.insert("end", f"Result (drop min/max): {result}\n")

# ---------------- Main App ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COSC-1100 Programs GUI")
        self.geometry("720x480")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ttk.Frame(container, padding=8)
        sidebar.pack(side="left", fill="y")

        self.content = ttk.Frame(container, padding=8)
        self.content.pack(side="right", fill="both", expand=True)

        # Frames dict
        self.frames = {
            "Dog Grooming": DogGroomingFrame(self.content),
            "Horse Track": HorseTrackFrame(self.content),
            "One-Digit Calculator": CalculatorFrame(self.content),
            "Milkshake Tracker": MilkshakesFrame(self.content),
            "Pizza Calculator": PizzaCalculatorFrame(self.content),
            "List Functions Test": ListFunctionsFrame(self.content),
        }

        # Buttons
        for i, (name, frame) in enumerate(self.frames.items()):
            ttk.Button(sidebar, text=name, command=lambda n=name: self.show(n)).pack(fill="x", pady=2)

        # Default
        self.current = None
        self.show("Dog Grooming")

    def show(self, name):
        if self.current:
            self.current.pack_forget()
        self.current = self.frames[name]
        self.current.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
