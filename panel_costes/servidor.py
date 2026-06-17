#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor local del panel de costes.
====================================

- Al ARRANCAR regenera los datos (ejecuta analizar.py) -> el panel sale fresco.
- Se AUTO-ACTUALIZA cada cierto intervalo en segundo plano (por defecto 5 min).
- Sirve el panel en una URL local. Abres http://localhost:8799/ en el navegador.
- La página detecta cuando hay datos nuevos y ofrece recargar (badge "🔄 en vivo").

Sigue siendo SOLO LECTURA sobre ~/.claude: analizar.py solo lee de ahí y escribe
únicamente dentro de panel_costes/.

Uso:
    python3 servidor.py                  # solo tu ordenador (127.0.0.1:8799)
    python3 servidor.py --compartir      # accesible en tu red local (0.0.0.0)
    python3 servidor.py --puerto 9000 --intervalo 120
"""

import os, sys, time, socket, argparse, subprocess, threading, functools, json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

OUT_DIR = os.path.dirname(os.path.realpath(__file__))
ANALIZAR = os.path.join(OUT_DIR, "analizar.py")
DATOS = os.path.join(OUT_DIR, "datos.json")
_stop = threading.Event()
_lock = threading.Lock()      # evita regeneraciones solapadas (botón + arranque)


def regenerar(motivo=""):
    """Ejecuta analizar.py (solo lectura sobre ~/.claude). Devuelve True si fue OK."""
    with _lock:
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, ANALIZAR], cwd=OUT_DIR,
                               capture_output=True, text=True, timeout=600)
        except Exception as e:
            print("  [!] No se pudo regenerar:", e)
            return False
        coste = next((ln for ln in r.stdout.splitlines() if "Coste total" in ln), "").strip()
        stamp = time.strftime("%H:%M:%S")
        if r.returncode == 0:
            print("  [%s] datos actualizados en %.1fs %s  %s"
                  % (stamp, time.time() - t0, ("· " + motivo) if motivo else "", coste))
            return True
        print("  [%s] ERROR al regenerar:\n%s" % (stamp, (r.stderr or "")[-800:]))
        return False


def leer_generado():
    try:
        with open(DATOS, encoding="utf-8") as fh:
            d = json.load(fh)
        return d.get("generado"), d.get("totales", {}).get("coste")
    except Exception:
        return None, None


def bucle_actualizacion(intervalo):
    while not _stop.wait(intervalo):
        regenerar("refresco automático")


def ips_lan():
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ips.add(s.getsockname()[0]); s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    return sorted(ips)


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")  # nunca cachear (datos en vivo)
        super().end_headers()

    def log_message(self, *a):
        pass  # silencioso

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta == "/version":                          # poll ligero del cliente (badge "datos nuevos")
            gen, coste = leer_generado()
            body = json.dumps({"generado": gen, "coste": coste}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if ruta == "/regenerar":                       # botón "Actualizar ahora"
            ok = regenerar("botón")
            gen, coste = leer_generado()
            body = json.dumps({"ok": ok, "generado": gen, "coste": coste}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if ruta in ("/", "", "/analisisClaude", "/analisisClaude/"):
            self.path = "/panel.html"
        return super().do_GET()

    def do_POST(self):
        ruta = self.path.split("?")[0]
        if ruta == "/guardar-precios":
            try:
                n = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(n)
                nuevo = json.loads(body)
                assert isinstance(nuevo.get("modelos"), dict), "falta modelos"
                assert isinstance(nuevo.get("suscripciones_usd_mes"), dict), "falta suscripciones"
                precios_path = os.path.join(OUT_DIR, "precios.json")
                with open(precios_path, "w", encoding="utf-8") as fh:
                    json.dump(nuevo, fh, ensure_ascii=False, indent=2)
                ok = regenerar("edición de precios")
                gen, coste = leer_generado()
                resp = json.dumps({"ok": ok, "generado": gen, "coste": coste}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                err = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return
        self.send_response(405)
        self.end_headers()


def main():
    ap = argparse.ArgumentParser(description="Servidor local del panel de costes de Claude Code")
    ap.add_argument("--puerto", type=int, default=8799)
    ap.add_argument("--intervalo", type=int, default=0,
                    help="segundos entre refrescos automáticos (0 = desactivado: solo al arrancar y con el botón)")
    ap.add_argument("--compartir", action="store_true",
                    help="escucha en 0.0.0.0 para que otros equipos de tu red local entren")
    ap.add_argument("--sin-regenerar", action="store_true", help="no regenerar al arrancar")
    args = ap.parse_args()

    host = "0.0.0.0" if args.compartir else "127.0.0.1"

    print("Panel de costes · servidor local")
    print("Regenerando datos al arrancar (solo lectura sobre ~/.claude)…")
    if not args.sin_regenerar:
        regenerar("arranque")

    if args.intervalo > 0:
        threading.Thread(target=bucle_actualizacion, args=(args.intervalo,), daemon=True).start()

    handler = functools.partial(Handler, directory=OUT_DIR)
    httpd = ThreadingHTTPServer((host, args.puerto), handler)

    print("\n  Local:    http://localhost:%d/analisisClaude" % args.puerto)
    if args.compartir:
        for ip in ips_lan():
            print("  Red:      http://%s:%d/analisisClaude   (compártelo en tu red local)" % (ip, args.puerto))
        print("  ⚠  El panel no tiene contraseña y contiene prompts de tus sesiones:")
        print("     compártelo solo en una red de confianza.")
    else:
        print("  (solo este ordenador · usa --compartir para abrirlo a tu red local)")
    if args.intervalo > 0:
        print("  Refresco: botón “Actualizar ahora” + temporizador cada %ds · Ctrl+C para parar\n" % args.intervalo)
    else:
        print("  Refresco: al arrancar + botón “Actualizar ahora” (sin temporizador) · Ctrl+C para parar\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nParando…")
    finally:
        _stop.set()
        httpd.shutdown()


if __name__ == "__main__":
    main()
