# Author: Jack Lidster
# Date: 2025-12-07
# Description: A simple subnet calculator GUI application using tkinter.
import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress

class SubnetCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Subnet Calculator")
        self.root.geometry("900x700")
        self.current_network = None
        
        # Input Frame
        input_frame = ttk.LabelFrame(root, text="Input", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ttk.Label(input_frame, text="CIDR Notation (e.g., 192.168.0.0/24):").pack(side="left", padx=5)
        self.cidr_entry = ttk.Entry(input_frame, width=25)
        self.cidr_entry.pack(side="left", padx=5)
        self.cidr_entry.insert(0, "192.168.0.0/24")
        
        ttk.Label(input_frame, text="New Prefix Length:").pack(side="left", padx=5)
        self.prefix_entry = ttk.Entry(input_frame, width=5)
        self.prefix_entry.pack(side="left", padx=5)
        self.prefix_entry.insert(0, "25")
        
        ttk.Button(input_frame, text="Calculate", command=self.calculate_subnets).pack(side="left", padx=5)
        
        # Networks Frame
        networks_label = ttk.LabelFrame(root, text="Subnets", padding="10")
        networks_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(networks_label)
        scrollbar.pack(side="right", fill="y")
        
        self.networks_listbox = tk.Listbox(networks_label, yscrollcommand=scrollbar.set, height=20, width=40)
        self.networks_listbox.pack(side="left", fill="both", expand=True)
        self.networks_listbox.bind('<<ListboxSelect>>', self.on_network_select)
        scrollbar.config(command=self.networks_listbox.yview)
        
        # Details Frame
        details_label = ttk.LabelFrame(root, text="Network Details", padding="10")
        details_label.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        
        self.details_text = tk.Text(details_label, width=40, height=20, font=("Courier", 10))
        self.details_text.pack(fill="both", expand=True)
        
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
    
    def calculate_subnets(self):
        try:
            network = ipaddress.ip_network(self.cidr_entry.get(), strict=False)
            new_prefix = int(self.prefix_entry.get())
            
            self.networks_listbox.delete(0, tk.END)
            self.details_text.delete(1.0, tk.END)
            self.current_network = network
            
            for subnet in network.subnets(new_prefix=new_prefix):
                self.networks_listbox.insert(tk.END, str(subnet))
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def on_network_select(self, event=None):
        selection = self.networks_listbox.curselection()
        if not selection:
            return
        
        subnet_str = self.networks_listbox.get(selection[0])
        subnet = ipaddress.ip_network(subnet_str, strict=False)
        
        self.details_text.delete(1.0, tk.END)
        
        info = f"Network: {subnet}\n"
        info += f"Subnet Mask: {subnet.netmask}\n"
        info += f"Network Address: {subnet.network_address}\n"
        info += f"Broadcast Address: {subnet.broadcast_address}\n"
        info += f"Usable Hosts: {max(0, subnet.num_addresses - 2)}\n"
        info += f"First Host: {subnet.network_address + 1}\n"
        info += f"Last Host: {subnet.broadcast_address - 1}\n"
        
        self.details_text.insert(1.0, info)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnetCalculator(root)
    root.mainloop()
