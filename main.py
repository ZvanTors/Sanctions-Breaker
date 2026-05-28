import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import threading
import sys
import ctypes

# ----------------------------------------------------------------------
# فعال‌سازی Dark Mode برای نوار عنوان ویندوز
# ----------------------------------------------------------------------
def set_dark_title_bar(window):
    """فعال کردن عنوان تیره در ویندوز ۱۰ نسخه 1809 به بالا"""
    try:
        window.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass  # اگر ویندوز قدیمی باشه بی‌صدا رد می‌شه

# ----------------------------------------------------------------------
# ساخت آیکون سپر در حافظه (PPM) - بدون فایل خارجی
# ----------------------------------------------------------------------
def create_shield_ppm():
    width, height = 32, 32
    shield = [(16, 0), (32, 8), (32, 24), (16, 32), (0, 24), (0, 8)]

    def point_in_polygon(x, y, poly):
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def in_lock_rect(x, y): return 12 <= x <= 20 and 14 <= y <= 24
    def in_keyhole(x, y): return (x - 16) ** 2 + (y - 12) ** 2 <= 3 ** 2

    BG = (0x2E, 0x2E, 0x2E)
    SHIELD = (30, 136, 229)
    LOCK = (255, 255, 255)

    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            if point_in_polygon(x, y, shield):
                if in_lock_rect(x, y) or in_keyhole(x, y):
                    r, g, b = LOCK
                else:
                    r, g, b = SHIELD
            else:
                r, g, b = BG
            pixels.extend([r, g, b])
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    return header + bytes(pixels)

# ----------------------------------------------------------------------
# لیست کامل DNSهای تحریم‌شکن ایرانی
# ----------------------------------------------------------------------
DNS_PROVIDERS = [
    ("Shecan",        "178.22.122.100", "185.51.200.2"),
    ("Begzar",        "185.55.226.26",  "185.55.225.25"),
    ("Electro",       "78.157.42.100",  "78.157.42.101"),
    ("403.online",    "10.202.10.202",  "10.202.10.102"),
    ("Radar",         "10.202.10.10",   "10.202.10.11"),
    ("Pishgaman",     "5.202.100.100",  "5.202.100.101"),
    ("Pezhvak",       "185.105.239.11", "178.22.122.100"),
    ("HostIran",      "172.29.0.100",   "172.29.0.101"),
]

# ----------------------------------------------------------------------
# پنجره اصلی
# ----------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sanctions Breaker")
        self.geometry("680x600")
        self.resizable(False, False)   # غیرفعال کردن Maximize و تغییر اندازه

        # آیکون
        ppm = create_shield_ppm()
        self.icon = tk.PhotoImage(data=ppm)
        self.iconphoto(True, self.icon)

        # فعال‌سازی عنوان تیره
        set_dark_title_bar(self)

        # ----- استایل تیره (ttk) -----
        style = ttk.Style()
        style.theme_use("clam")
        BG = "#2E2E2E"
        FG = "white"
        DARK_BG = "#3C3C3C"
        style.configure(".", background=BG, foreground=FG, fieldbackground=DARK_BG,
                        borderwidth=1, relief="flat")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton", background=DARK_BG, foreground=FG, borderwidth=0,
                        focusthickness=0, padding=6)
        style.map("TButton", background=[("active", "#4A4A4A")])
        style.configure("TCombobox", fieldbackground=DARK_BG, background=DARK_BG,
                        foreground=FG, arrowcolor="white")
        style.map("TCombobox", fieldbackground=[("readonly", DARK_BG)])
        self.option_add("*TCombobox*Listbox*Background", DARK_BG)
        self.option_add("*TCombobox*Listbox*Foreground", FG)
        style.configure("Treeview", background=DARK_BG, foreground=FG,
                        fieldbackground=DARK_BG, borderwidth=0)
        style.configure("Treeview.Heading", background="#555", foreground="white",
                        relief="flat")
        style.map("Treeview", background=[("selected", "#1E88E5")])

        self.configure(bg=BG)

        # متغیرها
        self.selected_adapter = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.is_connected = False

        # ----- رابط کاربری -----
        self._build_ui()
        self._refresh_adapters()

    # ---------- ساخت UI ----------
    def _build_ui(self):
        main = tk.Frame(self, bg="#2E2E2E")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # عنوان
        title = tk.Label(main, text="Sanctions Breaker", font=("Segoe UI Variable", 20, "bold"),
                         fg="#1E88E5", bg="#2E2E2E")
        title.pack(pady=(0, 5))
        sub = tk.Label(main, text="Set the fastest Iranian anti‑filter DNS on your network adapter",
                       font=("Segoe UI", 11), fg="#B0BEC5", bg="#2E2E2E")
        sub.pack(pady=(0, 20))

        # --- انتخاب آداپتور ---
        adapter_frame = tk.Frame(main, bg="#2E2E2E")
        adapter_frame.pack(fill="x", pady=(0, 15))
        tk.Label(adapter_frame, text="Network Adapter:", font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#2E2E2E").pack(side="left", padx=(0, 10))
        self.adapter_combo = ttk.Combobox(adapter_frame, textvariable=self.selected_adapter,
                                          state="readonly", width=35, font=("Segoe UI", 11))
        self.adapter_combo.pack(side="left", padx=(0, 10))
        ttk.Button(adapter_frame, text="Refresh", command=self._refresh_adapters).pack(side="left")

        # --- لیست DNS ---
        list_frame = tk.Frame(main, bg="#2E2E2E")
        list_frame.pack(fill="both", expand=True, pady=(10, 15))
        columns = ("provider", "primary", "secondary", "latency")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                 selectmode="none", height=10)
        self.tree.heading("provider", text="Provider")
        self.tree.heading("primary", text="Primary IP")
        self.tree.heading("secondary", text="Secondary IP")
        self.tree.heading("latency", text="Latency (ms)")
        self.tree.column("provider", anchor="center", width=100)
        self.tree.column("primary", anchor="center", width=160)
        self.tree.column("secondary", anchor="center", width=160)
        self.tree.column("latency", anchor="center", width=100)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # پر کردن ردیف‌ها
        for prov, prim, sec in DNS_PROVIDERS:
            self.tree.insert("", "end", values=(prov, prim, sec, "-"))

        # --- دکمه‌ها ---
        btn_frame = tk.Frame(main, bg="#2E2E2E")
        btn_frame.pack(pady=(0, 15))
        self.connect_btn = tk.Button(btn_frame, text="  Connect  ",
                                     font=("Segoe UI", 13, "bold"),
                                     bg="#2E7D32", fg="white", activebackground="#388E3C",
                                     activeforeground="white", bd=0, padx=20, pady=8,
                                     cursor="hand2", command=self._start_connect)
        self.connect_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(btn_frame, text="  Stop  ",
                                  font=("Segoe UI", 13, "bold"),
                                  bg="#C62828", fg="white", activebackground="#D32F2F",
                                  activeforeground="white", bd=0, padx=20, pady=8,
                                  cursor="hand2", state="disabled", command=self._stop)
        self.stop_btn.pack(side="left", padx=10)

        # --- نوار وضعیت ---
        status_frame = tk.Frame(self, bg="#1E1E1E", height=28)
        status_frame.pack(fill="x", side="bottom")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                                font=("Segoe UI", 10), fg="#CCCCCC", bg="#1E1E1E",
                                anchor="w", padx=15)
        status_label.pack(fill="x")

    # ---------- مدیریت آداپتورها ----------
    def _refresh_adapters(self):
        self.status_var.set("Scanning adapters...")
        try:
            out = subprocess.check_output("netsh interface show interface", shell=True,
                                          stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list adapters:\n{e}")
            self.status_var.set("Ready")
            return
        adapters = []
        for line in out.splitlines():
            if "Connected" in line:
                match = re.search(r"Connected\s+\S+\s+(.*)", line)
                if match:
                    adapters.append(match.group(1).strip())
        if not adapters:
            adapters = ["No connected adapter found"]
        self.adapter_combo["values"] = adapters
        if adapters[0] != "No connected adapter found":
            self.selected_adapter.set(adapters[0])
        else:
            self.selected_adapter.set("")
        self.status_var.set("Ready")

    # ---------- تنظیم و حذف DNS ----------
    def _set_dns(self, adapter, primary, secondary):
        try:
            subprocess.run(f'netsh interface ip set dns name="{adapter}" dhcp', shell=True,
                           check=False, capture_output=True)
            r1 = subprocess.run(f'netsh interface ip set dns name="{adapter}" static {primary}',
                                shell=True, capture_output=True, text=True)
            if r1.returncode != 0:
                raise RuntimeError(f"Failed primary DNS: {r1.stderr.strip()}")
            r2 = subprocess.run(f'netsh interface ip add dns name="{adapter}" {secondary} index=2',
                                shell=True, capture_output=True, text=True)
            if r2.returncode != 0:
                raise RuntimeError(f"Failed secondary DNS: {r2.stderr.strip()}")
            return True
        except Exception as e:
            messagebox.showerror("DNS Error", str(e))
            return False

    def _clear_dns(self, adapter):
        try:
            subprocess.run(f'netsh interface ip set dns name="{adapter}" dhcp', shell=True,
                           check=True, capture_output=True)
            subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # ---------- پینگ ----------
    def _ping_ip(self, ip):
        try:
            out = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                 capture_output=True, text=True, timeout=2)
            match = re.search(r"time=(\d+)ms", out.stdout)
            return int(match.group(1)) if match else None
        except:
            return None

    def _run_speed_test(self):
        ips = set()
        for _, prim, sec in DNS_PROVIDERS:
            ips.add(prim)
            ips.add(sec)
        results = {}
        for ip in ips:
            lat = self._ping_ip(ip)
            if lat is not None:
                results[ip] = lat
        return results

    # ---------- عملیات اتصال ----------
    def _start_connect(self):
        adapter = self.selected_adapter.get()
        if not adapter or adapter == "No connected adapter found":
            messagebox.showwarning("No Adapter", "Please select a connected network adapter.")
            return
        self.connect_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Testing DNS servers...")
        for child in self.tree.get_children():
            vals = self.tree.item(child)["values"]
            self.tree.item(child, values=(vals[0], vals[1], vals[2], "⏳"))

        def worker():
            results = self._run_speed_test()
            self.after(0, lambda: self._update_latencies(results))
            if not results:
                self.after(0, lambda: self._connect_fail("No DNS server responded."))
                return
            sorted_ips = sorted(results.items(), key=lambda x: x[1])
            primary, secondary = sorted_ips[0][0], sorted_ips[1][0] if len(sorted_ips) > 1 else sorted_ips[0][0]
            ok = self._set_dns(adapter, primary, secondary)
            self.after(0, lambda: self._connect_done(ok, primary, secondary))
        threading.Thread(target=worker, daemon=True).start()

    def _update_latencies(self, results):
        for child in self.tree.get_children():
            vals = self.tree.item(child)["values"]
            prim, sec = vals[1], vals[2]
            lat1 = results.get(prim)
            lat2 = results.get(sec)
            if lat1 is not None and lat2 is not None:
                display = f"{lat1} / {lat2}"
                self.tree.item(child, values=(vals[0], prim, sec, display),
                               tags=("good",))
            elif lat1 is not None:
                display = f"{lat1} / ✗"
                self.tree.item(child, values=(vals[0], prim, sec, display),
                               tags=("partial",))
            elif lat2 is not None:
                display = f"✗ / {lat2}"
                self.tree.item(child, values=(vals[0], prim, sec, display),
                               tags=("partial",))
            else:
                self.tree.item(child, values=(vals[0], prim, sec, "✗"),
                               tags=("fail",))
        self.tree.tag_configure("good", foreground="#66BB6A")
        self.tree.tag_configure("partial", foreground="#FFA726")
        self.tree.tag_configure("fail", foreground="#EF5350")

    def _connect_done(self, success, primary, secondary):
        self.connect_btn.config(state="normal" if not success else "disabled")
        self.stop_btn.config(state="normal" if success else "disabled")
        if success:
            self.status_var.set(f"Connected – DNS: {primary}, {secondary}")
            self.is_connected = True
        else:
            self.status_var.set("Connection failed")
            self.is_connected = False

    def _connect_fail(self, msg):
        self.connect_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set(msg)
        self.is_connected = False

    def _stop(self):
        adapter = self.selected_adapter.get()
        if not adapter:
            return
        if self._clear_dns(adapter):
            self.status_var.set("DNS cleared (DHCP).")
            self.is_connected = False
            self.connect_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            for child in self.tree.get_children():
                vals = self.tree.item(child)["values"]
                self.tree.item(child, values=(vals[0], vals[1], vals[2], "-"), tags=("",))
        else:
            messagebox.showerror("Error", "Failed to clear DNS. Run as Administrator.")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform != "win32":
        messagebox.showerror("Platform Error", "This application runs only on Windows.")
        sys.exit(1)
    app = App()
    app.mainloop()