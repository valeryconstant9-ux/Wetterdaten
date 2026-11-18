"""Holt Flugzeuge weltweit (airplanes.live / adsb.lol, kostenlos, ohne Schluessel) und schreibt site/aircraft.json."""
import json, math, os, time, urllib.request
SRC = ["https://api.airplanes.live/v2/point/{la}/{lo}/250", "https://api.adsb.lol/v2/point/{la}/{lo}/250"]
BOX = [(15,72,-170,-50),(-56,13,-82,-34),(35,72,-12,45),(-35,35,-18,52),(5,70,45,145),(-45,-10,112,155),(30,65,-60,-12),(15,60,150,180),(15,60,-180,-120)]
pts = {}
for la0, la1, lo0, lo1 in BOX:
    la = la0
    while la <= la1:
        step = 5.4 / max(.25, math.cos(math.radians(min(abs(la), 75))))
        lo = lo0
        while lo <= lo1:
            pts[(round(la, 1), round(lo, 1))] = 1; lo += step
        la += 5.4
pts = list(pts)
print(len(pts), "Abfragen")
acs = {}; ok = 0; k = 0
for i, (la, lo) in enumerate(pts):
    for j in range(2):
        u = SRC[(i + j) % 2].format(la=la, lo=lo)
        try:
            rq = urllib.request.Request(u, headers={"User-Agent": "Projekt5-Radar/1.0", "Accept": "application/json"})
            js = json.load(urllib.request.urlopen(rq, timeout=20)); ok += 1
            for a in js.get("ac", []):
                if a.get("lat") is None or a.get("lon") is None or not a.get("hex"): continue
                acs[a["hex"]] = {x: a[x] for x in ("hex", "flight", "lat", "lon", "alt_baro", "alt_geom", "track", "gs", "t", "r", "seen_pos") if x in a}
            break
        except Exception as e:
            print("Fehler", u, e)
    time.sleep(0.55)
print(ok, "OK,", len(acs), "Flugzeuge")
os.makedirs("site", exist_ok=True)
if len(acs) > 50:
    json.dump({"now": int(time.time() * 1000), "ac": list(acs.values())}, open("site/aircraft.json", "w"), separators=(",", ":"))
else:
    raise SystemExit("zu wenig Daten, nichts geschrieben")
