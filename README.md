# 🛡️ Sanctions Breaker

**Set the fastest Iranian anti‑filter DNS on your Windows network adapter with one click.**

A modern, lightweight desktop application that helps users bypass internet censorship by automatically testing the latency of multiple Iranian DNS servers and applying the two fastest ones to your selected network interface. No external dependencies required – built entirely with Python's standard library.

---

## ✨ Features

- 🚀 **One‑click connection** – Automatically pings all DNS servers and picks the top two with the lowest latency.
- 🎨 **Modern dark UI** – Fully dark themed, with a professional Segoe UI font and a custom shield‑and‑lock icon.
- 📶 **Adapter selection** – Choose which network adapter to configure (Wi‑Fi, Ethernet, etc.).
- ⏹️ **Stop & restore** – Reverts DNS settings back to DHCP with one click.
- 🔒 **Admin elevation** – Asks for Administrator privileges via UAC when executed (only Windows).
- 📦 **Zero dependencies** – No need to install anything beyond Python 3 (standard library only).
- 🏗️ **Portable EXE** – Can be built into a standalone executable using PyInstaller.

---

## 📋 Supported DNS Providers

The following Iranian anti‑filter DNS servers are included (latency is tested for all):

| Provider   | Primary IP       | Secondary IP     |
|------------|------------------|------------------|
| Shecan     | 178.22.122.100   | 185.51.200.2     |
| Begzar     | 185.55.226.26    | 185.55.225.25    |
| Electro    | 78.157.42.100    | 78.157.42.101    |
| 403.online | 10.202.10.202    | 10.202.10.102    |
| Radar      | 10.202.10.10     | 10.202.10.11     |
| Pishgaman  | 5.202.100.100    | 5.202.100.101    |
| Pezhvak    | 185.105.239.11   | 178.22.122.100   |
| HostIran   | 172.29.0.100     | 172.29.0.101     |

---

## 🔧 Requirements

- **Windows 10/11** (Windows 7+ may work but the dark title bar feature requires Windows 10 1809+)
- **Python 3.6+** (if running from source)
- No extra pip packages needed – only `tkinter` (comes with Python) and standard libraries.

---

## 🚀 Usage (from source)

1. **Clone the repository**

   git clone https://github.com/ZvanTors/sanctions-breaker.git
   cd sanctions-breaker

2. **Run the script as Administrator**

Right‑click on main.py → Run as administrator

Or open an Admin Command Prompt and run:
bash

python main.py

Select your network adapter from the dropdown and click Connect.
The app will test all DNS servers, highlight the latencies, and apply the fastest ones.
Use the Stop button to revert back to DHCP.

⚠️ Note: Changing DNS settings requires Administrator privileges. If you don't run as admin, you'll see a "Failed primary DNS" error.

---

## 🤝 Contributing

Pull requests are welcome! If you'd like to add more DNS providers, improve the UI, or fix bugs, feel free to open an issue or PR.

---

## 📄 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## 🙏 Acknowledgments

DNS providers listed are publicly available services maintained by the Iranian tech community.

---

Made for freedom of access.
