# news-image-20261125 — acct3 (fansevanoo). 36 stories, classic 9-hero formula.
# Flat-vector PIL newspaper. Deterministic, no network. 1024x1024.
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1024, 1024
M = 22                      # page margin
NAVY = (23, 42, 72)
BRICK = (178, 58, 44)
CREAM = (247, 239, 222)
PAPER = (250, 244, 230)
INK = (32, 32, 32)
GREY = (110, 108, 100)
LANDB = (214, 186, 138)    # land fill (dark tan, high contrast)
SEA = (188, 214, 228)
SKY = (176, 208, 226)
GOLD = (214, 164, 62)
GREEN = (74, 120, 74)

FD = "/usr/share/fonts/truetype/dejavu/"
def F(path, size):
    return ImageFont.truetype(FD + path, size)
def serif(size, bold=True):
    return F("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size)
def sans(size, bold=False):
    return F("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)

def fit_font(draw, text, path, max_size, width, min_size=7):
    s = max_size
    while s > min_size:
        f = F(path, s)
        if draw.textlength(text, font=f) <= width:
            return f
        s -= 1
    return F(path, min_size)

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, text, path, max_size, width, max_lines):
    """Shrink font until text wraps into <= max_lines. Returns (font, lines)."""
    s = max_size
    while s >= 7:
        f = F(path, s)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
        s -= 1
    return F(path, 7), wrap(draw, text, F(path, 7), width)

def outline(d, box, color=NAVY, w=2):
    d.rectangle(box, outline=color, width=w)

def badge(d, cx, cy, num, r=9, fill=BRICK, fg=(255, 255, 255)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=NAVY, width=1)
    f = sans(11 if r >= 9 else 10, True)
    t = str(num)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 8 if r >= 9 else cy - 7),
           t, font=f, fill=fg)

# ---------------- continents (lon, lat) — simplified coastlines ----------------
NA = [(-168,66),(-158,58),(-150,60),(-140,60),(-135,58),(-130,54),(-125,49),
      (-124,42),(-120,34),(-114,29),(-110,24),(-105,20),(-97,16),(-92,15),
      (-87,13),(-83,9),(-80,8),(-77,7),(-79,9),(-81,13),(-83,15),(-86,16),
      (-88,18),(-90,21),(-87,21),(-90,21),(-91,19),(-94,18),(-97,16),
      (-97,26),(-93,30),(-89,30),(-84,30),(-81,26),(-80,32),(-76,35),
      (-74,39),(-70,42),(-68,45),(-65,44),(-60,46),(-65,50),(-60,52),
      (-64,58),(-68,58),(-78,62),(-85,66),(-92,66),(-95,69),(-110,68),
      (-125,70),(-140,70),(-155,71),(-165,68),(-168,66)]
SA = [(-77,7),(-75,10),(-72,12),(-64,11),(-60,8),(-55,6),(-52,4),(-50,0),
      (-44,-3),(-38,-5),(-35,-8),(-38,-13),(-40,-20),(-48,-27),(-52,-33),
      (-58,-38),(-62,-41),(-66,-45),(-68,-50),(-70,-54),(-74,-53),(-73,-44),
      (-73,-37),(-71,-30),(-70,-23),(-75,-15),(-79,-8),(-81,-4),(-80,1),
      (-77,4),(-77,7)]
GREENLAND = [(-58,64),(-52,60),(-44,60),(-40,64),(-32,68),(-22,70),(-20,74),
             (-25,76),(-32,80),(-45,81),(-58,80),(-62,76),(-58,70),(-58,64)]
EUROPE = [(-10,36),(-9,38),(-9,43),(-2,44),(-1,46),(-4,48),(-2,49),(0,50),
          (2,51),(4,53),(8,55),(8,57),(10,59),(6,58),(5,60),(10,62),(13,65),
          (18,69),(25,71),(30,70),(32,68),(35,66),(40,64),(42,60),(40,58),
          (38,55),(36,52),(33,48),(30,46),(28,44),(28,42),(26,40),(23,40),
          (22,38),(20,40),(18,40),(16,38),(15,40),(12,42),(10,44),(8,44),
          (6,43),(3,42),(0,40),(-2,37),(-6,36),(-9,37),(-10,36)]
AFRICA = [(-6,35),(-10,31),(-15,27),(-17,21),(-17,15),(-16,12),(-13,8),
          (-8,5),(-4,5),(0,6),(6,4),(9,4),(9,0),(12,-5),(13,-10),(12,-17),
          (14,-22),(16,-28),(19,-34),(26,-34),(32,-29),(36,-25),(40,-20),
          (40,-15),(40,-10),(42,-4),(46,-1),(51,2),(51,11),(44,11),(40,15),
          (38,18),(36,22),(34,27),(32,31),(30,32),(25,32),(20,32),(15,32),
          (11,34),(10,37),(5,37),(0,36),(-6,35)]
ASIA = [(68,68),(73,71),(80,73),(88,74),(96,76),(104,77),(112,74),(120,73),
        (128,72),(136,72),(144,71),(152,70),(158,69),(164,67),(170,66),(178,65),
        (178,62),(170,60),(162,58),(158,53),(156,51),(150,59),(142,54),(141,46),
        (135,43),(130,42),(127,39),(126,38),(122,38),(120,34),(121,28),(118,24),
        (110,20),(108,18),(105,9),(103,7),(100,6),(98,10),(97,15),(94,17),
        (92,21),(89,22),(86,20),(82,17),(80,13),(80,9),(77,8),(75,11),(73,16),
        (70,20),(66,25),(61,25),(57,25),(54,26),(52,27),(50,29),(48,30),(44,31),
        (41,33),(38,35),(36,36),(33,36),(30,36),(27,37),(26,38),(23,36),(22,37),
        (23,40),(26,40),(28,41),(30,41),(33,42),(35,43),(38,44),(40,45),(38,47),
        (36,48),(33,48),(31,46),(30,45),(32,46),(35,48),(38,50),(40,52),(42,54),
        (44,56),(46,58),(48,60),(50,62),(55,64),(60,66),(65,68)]
ARABIA = [(44,31),(42,33),(39,35),(36,36),(35,33),(34,31),(35,29),(37,27),
          (38,24),(39,21),(40,18),(41,15),(43,12),(45,13),(48,14),(52,15),
          (55,17),(58,20),(59,22),(58,23),(57,25),(56,27),(54,26),(52,26),
          (50,27),(49,29),(48,30),(46,30)]
AUSTRALIA = [(114,-22),(114,-30),(115,-33),(118,-35),(124,-33),(129,-32),
             (132,-32),(135,-35),(137,-35),(140,-38),(144,-38),(147,-39),
             (150,-37),(153,-32),(153,-27),(151,-24),(147,-19),(142,-15),
             (142,-11),(141,-13),(136,-12),(135,-15),(132,-12),(130,-13),
             (126,-14),(122,-17),(118,-20),(114,-22)]
MADAGASCAR = [(44,-16),(47,-15),(50,-16),(49,-20),(47,-24),(44,-25),(43,-21),(44,-16)]
HONSHU = [(130,31),(132,33),(134,34),(136,35),(138,35),(140,36),(141,39),
          (141,41),(140,40),(138,38),(136,37),(134,35),(132,34),(130,33),(130,31)]
HOKKAIDO = [(140,42),(142,42),(144,43),(145,44),(143,44),(141,44),(140,43),(140,42)]
SUMATRA = [(95,5),(98,3),(101,0),(104,-3),(106,-6),(104,-5),(101,-2),(98,2),(95,5)]
JAVA = [(106,-6),(109,-7),(112,-7),(114,-8),(114,-9),(111,-8),(108,-8),(106,-7),(106,-6)]
KALIMANTAN = [(109,0),(111,1),(114,2),(117,1),(118,-1),(117,-3),(115,-4),
              (112,-4),(110,-3),(109,-1),(109,0)]
NEWGUINEA = [(131,-1),(134,-2),(137,-3),(140,-4),(143,-6),(146,-7),(148,-9),
             (150,-10),(147,-8),(144,-7),(141,-6),(138,-5),(135,-3),(132,-2),(131,-1)]
NZ_N = [(173,-35),(175,-37),(177,-38),(178,-38),(176,-40),(174,-41),(173,-39),(173,-35)]
NZ_S = [(167,-45),(169,-43),(171,-42),(173,-41),(174,-42),(172,-44),(170,-46),
        (168,-47),(167,-45)]
SRILANKA = [(80,9),(81,8),(81,6),(80,6),(80,9)]
PHILIPPINES = [(120,18),(121,16),(122,14),(121,13),(122,11),(124,10),(126,8),
               (124,7),(122,8),(121,10),(120,13),(120,16),(120,18)]
UK = [(-5,50),(-3,53),(-5,56),(-3,58),(-1,57),(0,53),(1,51),(-2,50),(-5,50)]

# ---------------- 36 map dots (lon, lat) — from the stories file ----------------
DOTS = {
 1: (-75.5, 10.4), 2: (-76.4, 37.0), 3: (-91.3, 40.8), 4: (4.4, 50.9),
 5: (37.6, 55.8), 6: (127.0, 37.5), 7: (160.0, -9.4), 8: (55.3, 25.2),
 9: (4.3, 52.1), 10: (-74.0, 40.7), 11: (30.7, 36.9), 12: (34.5, 31.5),
 13: (12.5, 41.9), 14: (30.0, 1.7), 15: (125.7, 39.0), 16: (35.2, 32.0),
 17: (-2.2, 53.5), 18: (0.5, 52.8), 19: (-77.0, 38.9), 20: (-77.0, 38.9),
 21: (-3.7, 40.4), 22: (-17.4, 14.7), 23: (6.1, 46.2), 24: (51.4, 35.7),
 25: (90.4, 23.8), 26: (2.3, 48.9), 27: (151.2, -33.9), 28: (139.7, 35.7),
 29: (56.5, 26.5), 30: (34.8, 32.1), 31: (35.2, 31.8), 32: (88.4, 22.6),
 33: (74.1, 15.3), 34: (7.5, 51.5), 35: (31.7, 46.5), 36: (77.2, 28.6),
}
PLACE = {
 1: "Cartagena", 2: "Langley", 3: "Middletown", 4: "Brussels", 5: "Moscow",
 6: "Seoul", 7: "Honiara", 8: "Dubai", 9: "The Hague", 10: "Brooklyn",
 11: "Antalya", 12: "Gaza City", 13: "Rome", 14: "Akwe, Ituri", 15: "Pyongyang",
 16: "West Bank", 17: "Manchester", 18: "Sandringham", 19: "Washington DC",
 20: "Washington DC", 21: "Madrid", 22: "Dakar", 23: "Geneva", 24: "Tehran",
 25: "Dhaka", 26: "Paris", 27: "Sydney", 28: "Tokyo", 29: "Hormuz",
 30: "Tel Aviv", 31: "Jerusalem", 32: "Kolkata", 33: "Goa", 34: "Dortmund",
 35: "Kinburn Spit", 36: "New Delhi",
}
CONTINENTS = [NA, SA, GREENLAND, EUROPE, AFRICA, ASIA, ARABIA, AUSTRALIA,
              MADAGASCAR, HONSHU, HOKKAIDO, SUMATRA, JAVA, KALIMANTAN,
              NEWGUINEA, NZ_N, NZ_S, SRILANKA, PHILIPPINES, UK]

def draw_map(d, x0, y0, w, h, debug=False):
    """Draw world map in box (x0,y0,w,h). Returns (px dict, min badge distance)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    # graticule
    for lon in range(-150, 181, 30):
        px = x0 + (lon + 168) * (w / 360.0)
        d.line([(px, y0), (px, y0 + h)], fill=(255, 255, 255, 90), width=1)
    for lat in range(-60, 85, 30):
        py = y0 + (84 - lat) * (h / 142.0)
        d.line([(x0, py), (x0 + w, py)], fill=(255, 255, 255, 90), width=1)
    sx, sy = w / 360.0, h / 142.0
    s = min(sx, sy)
    ox = x0 + (w - 360 * s) / 2
    oy = y0 + (h - 142 * s) / 2
    def proj(lon, lat):
        return (ox + (lon + 168) * s, oy + (84 - lat) * s)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LANDB)
        d.line(pts + [pts[0]], fill=NAVY, width=2)
    px = {n: proj(lon, lat) for n, (lon, lat) in DOTS.items()}
    # badge positions: start on the dot, push apart until min distance 19px
    bx = {n: list(p) for n, p in px.items()}
    for _ in range(300):
        moved = False
        for a in range(1, 37):
            for b in range(a + 1, 37):
                dx = bx[b][0] - bx[a][0]
                dy = bx[b][1] - bx[a][1]
                dist = math.hypot(dx, dy)
                if dist < 19 and dist > 0.01:
                    push = (19 - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    bx[a][0] -= ux * push; bx[a][1] -= uy * push
                    bx[b][0] += ux * push; bx[b][1] += uy * push
                    moved = True
                elif dist <= 0.01:  # coincident dots (#19/#20): split vertically
                    bx[a][1] -= 9.5; bx[b][1] += 9.5
                    moved = True
        # clamp badges inside map box
        for n in bx:
            bx[n][0] = max(x0 + 10, min(x0 + w - 10, bx[n][0]))
            bx[n][1] = max(y0 + 10, min(y0 + h - 10, bx[n][1]))
        if not moved:
            break
    # leader lines, then dots, then badges
    for n in range(1, 37):
        dx, dy = px[n]
        cx, cy = bx[n]
        if math.hypot(cx - dx, cy - dy) > 4:
            d.line([(dx, dy), (cx, cy)], fill=NAVY, width=1)
    for n in range(1, 37):
        dx, dy = px[n]
        d.ellipse([dx - 3.5, dy - 3.5, dx + 3.5, dy + 3.5], fill=BRICK,
                  outline=(255, 255, 255), width=1)
    for n in range(1, 37):
        badge(d, bx[n][0], bx[n][1], n, r=9)
    mind = min(math.hypot(bx[a][0] - bx[b][0], bx[a][1] - bx[b][1])
               for a in range(1, 37) for b in range(a + 1, 37))
    close = [(a, b, round(math.hypot(bx[a][0]-bx[b][0], bx[a][1]-bx[b][1]), 1))
             for a in range(1, 37) for b in range(a + 1, 37)
             if math.hypot(bx[a][0]-bx[b][0], bx[a][1]-bx[b][1]) < 18]
    print("MAP px:", {n: (round(px[n][0], 1), round(px[n][1], 1)) for n in range(1, 37)})
    print("MAP min badge distance: %.1f px" % mind)
    if close:
        print("MAP close badge pairs (<18px):", close)
    return px, mind

# ---------------- flat-vector scene helpers ----------------
def layer(w, h, bg):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)

def person(d, x, y, s, shirt, pants, skin=(232, 190, 150)):
    """Simple standing figure, s = height px."""
    d.ellipse([x - 3 * s / 20, y, x + 3 * s / 20, y + s / 5], fill=skin)          # head
    d.rounded_rectangle([x - s / 5, y + s / 5, x + s / 5, y + s * 3 / 5],
                        radius=2, fill=shirt)                                    # torso
    d.rectangle([x - s / 5, y + s * 3 / 5, x - s / 20, y + s], fill=pants)       # leg L
    d.rectangle([x + s / 20, y + s * 3 / 5, x + s / 5, y + s], fill=pants)       # leg R
    d.rectangle([x - s / 4, y + s / 4, x - s / 5, y + s / 2], fill=shirt)        # arm L
    d.rectangle([x + s / 5, y + s / 4, x + s / 4, y + s / 2], fill=shirt)        # arm R

def sun(d, cx, cy, r, color=GOLD):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(200, 140, 40), width=2)
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + (r + 2) * math.cos(a), cy + (r + 2) * math.sin(a)),
                (cx + (r + 9) * math.cos(a), cy + (r + 9) * math.sin(a))],
               fill=color, width=3)

def cloud(d, x, y, s, color=(255, 255, 255)):
    d.ellipse([x, y, x + s, y + s * 0.6], fill=color)
    d.ellipse([x + s * 0.25, y - s * 0.25, x + s * 0.75, y + s * 0.35], fill=color)
    d.ellipse([x + s * 0.55, y, x + s * 1.05, y + s * 0.6], fill=color)

# ---------------- hero scenes (each returns an RGB image) ----------------
def scene_cartagena(w, h):
    im, d = layer(w, h, (246, 226, 190))
    sun(d, w - 42, 46, 20)
    # storefront: cream wall + red awning + EXITO sign
    d.rectangle([0, 34, w, h], fill=(250, 240, 214))
    d.rectangle([0, 34, w, 52], fill=BRICK)
    for x in range(0, w, 32):
        d.polygon([(x, 52), (x + 16, 52), (x + 8, 66)], fill=BRICK if (x // 32) % 2 == 0 else (255, 255, 255))
    d.rectangle([14, 58, w - 14, 76], fill=NAVY)
    f = sans(15, True)
    d.text((w / 2 - d.textlength("ÉXITO", font=f) / 2, 59), "ÉXITO", font=f, fill=(255, 255, 255))
    # shelves with goods
    for sy in (84, 102):
        d.rectangle([16, sy, w - 16, sy + 12], fill=(222, 200, 150))
        for gx in range(22, w - 22, 18):
            d.rectangle([gx, sy + 1, gx + 10, sy + 11],
                        fill=[(178, 58, 44), (74, 120, 74), (214, 164, 62), (23, 42, 72)][(gx // 18) % 4])
    # hostages + police line
    for i, x in enumerate([w * 0.18, w * 0.30, w * 0.42]):
        person(d, x, h - 46, 34, (120, 130, 160) if i % 2 else (200, 170, 120), (60, 60, 80))
    for i, x in enumerate([w * 0.58, w * 0.70]):
        person(d, x, h - 48, 36, (30, 60, 40), (30, 30, 30))
    # police armoured truck
    d.rectangle([w - 108, h - 34, w - 8, h - 8], fill=(40, 70, 50))
    d.rectangle([w - 108, h - 48, w - 58, h - 34], fill=(40, 70, 50))
    d.rectangle([w - 52, h - 46, w - 30, h - 36], fill=(176, 208, 226))
    d.ellipse([w - 96, h - 10, w - 82, h + 4], fill=(20, 20, 20))
    d.ellipse([w - 34, h - 10, w - 20, h + 4], fill=(20, 20, 20))
    f2 = sans(9, True)
    d.text((w - 104, h - 30), "POLICE", font=f2, fill=(255, 255, 255))
    return im

def scene_cia(w, h):
    im, d = layer(w, h, (16, 24, 48))
    for x, y in [(30, 20), (90, 12), (w - 70, 16), (w - 30, 30), (150, 26)]:
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
    # HQ building with columns
    d.rectangle([w * 0.30, 52, w * 0.72, h - 8], fill=(232, 228, 218))
    d.polygon([(w * 0.28, 52), (w * 0.51, 34), (w * 0.74, 52)], fill=(200, 60, 50))
    for i in range(4):
        cx = w * 0.34 + i * w * 0.11
        d.rectangle([cx, 58, cx + 8, h - 14], fill=(180, 176, 166))
    d.rectangle([w * 0.46, h - 34, w * 0.56, h - 8], fill=NAVY)
    # breach monitor (left)
    d.rectangle([8, 44, 88, 92], fill=(10, 14, 26), outline=BRICK, width=2)
    f = sans(8, True)
    d.text((12, 48), "ACCESS DENIED", font=f, fill=(255, 90, 70))
    d.text((12, 60), "CLASSIFIED", font=f, fill=(255, 190, 60))
    d.text((12, 72), "BREACH!", font=f, fill=(255, 90, 70))
    # server rack (right)
    d.rectangle([w - 78, 40, w - 8, h - 8], fill=(30, 34, 48), outline=(120, 120, 140), width=1)
    for sy in range(46, h - 12, 12):
        for gx in range(w - 72, w - 14, 12):
            d.ellipse([gx, sy, gx + 5, sy + 5],
                      fill=(90, 220, 120) if (gx + sy) % 24 == 0 else (220, 70, 60))
    # satellite dish
    d.arc([w * 0.74, 8, w * 0.74 + 40, 40], 200, 340, fill=(200, 200, 210), width=3)
    d.line([(w * 0.74 + 20, 40), (w * 0.74 + 20, 52)], fill=(200, 200, 210), width=3)
    return im

def scene_iowa(w, h):
    im, d = layer(w, h, (176, 208, 226))
    cloud(d, 16, 12, 34)
    cloud(d, w - 110, 8, 28)
    # ground
    d.rectangle([0, h - 34, w, h], fill=(120, 160, 90))
    # houses (left)
    for hx in (14, 62):
        d.rectangle([hx, h - 62, hx + 34, h - 34], fill=(240, 220, 190))
        d.polygon([(hx - 4, h - 62), (hx + 17, h - 76), (hx + 38, h - 62)], fill=BRICK)
        d.rectangle([hx + 13, h - 48, hx + 21, h - 34], fill=NAVY)
    # barrel stack (centre-left)
    for bx, by in [(w * 0.42, h - 58), (w * 0.42 + 22, h - 58), (w * 0.42 + 11, h - 80)]:
        d.rectangle([bx, by, bx + 20, by + 22], fill=(70, 90, 60), outline=(40, 60, 40), width=1)
        d.line([(bx, by + 7), (bx + 20, by + 7)], fill=(40, 60, 40), width=1)
        d.line([(bx, by + 15), (bx + 20, by + 15)], fill=(40, 60, 40), width=1)
    # big blast (right)
    cx, cy = w * 0.78, h * 0.42
    for r, c in [(46, (255, 120, 40)), (36, (255, 170, 60)), (26, (255, 220, 90))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    for k in range(10):
        a = k * math.pi / 5
        d.line([(cx + 40 * math.cos(a), cy + 40 * math.sin(a)),
                (cx + 54 * math.cos(a), cy + 54 * math.sin(a))], fill=(255, 120, 40), width=4)
    # smoke plume
    for i, (sx, sy, sr) in enumerate([(cx - 52, cy - 30, 12), (cx - 64, cy - 44, 15), (cx - 78, cy - 56, 10)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 200, 200))
    # 5-mile zone sign + FEMA tent (tent clear of the houses)
    d.rectangle([w - 62, h - 66, w - 8, h - 46], fill=(255, 255, 220), outline=NAVY, width=2)
    f = sans(8, True)
    d.text((w - 58, h - 64), "5 MILE", font=f, fill=NAVY)
    d.text((w - 58, h - 55), "ZONE", font=f, fill=NAVY)
    d.polygon([(100, h - 14), (112, h - 32), (124, h - 14)], fill=(255, 255, 255), outline=NAVY)
    return im

def scene_nato(w, h):
    im, d = layer(w, h, (12, 18, 44))
    for x, y in [(20, 14), (70, 26), (w - 40, 12), (w - 90, 30), (140, 10)]:
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
    # Earth arc (bottom)
    d.ellipse([-w * 0.25, h * 0.55, w * 1.25, h * 1.9], fill=(40, 110, 180), outline=(120, 200, 240), width=2)
    d.ellipse([w * 0.12, h * 0.72, w * 0.34, h * 1.05], fill=(74, 140, 80))
    d.ellipse([w * 0.62, h * 0.80, w * 0.86, h * 1.15], fill=(74, 140, 80))
    cloud(d, w * 0.40, h * 0.80, 40)
    # shield with star
    cx, cy = w * 0.50, h * 0.38
    d.polygon([(cx - 26, cy - 20), (cx + 26, cy - 20), (cx + 26, cy + 2), (cx, cy + 28), (cx - 26, cy + 2)],
              fill=GOLD, outline=(255, 255, 255), width=2)
    d.polygon([(cx, cy - 12), (cx + 4, cy - 2), (cx + 14, cy - 2), (cx + 6, cy + 5),
               (cx + 9, cy + 15), (cx, cy + 9), (cx - 9, cy + 15), (cx - 6, cy + 5),
               (cx - 14, cy - 2), (cx - 4, cy - 2)], fill=NAVY)
    # satellite + rocket
    d.rectangle([w * 0.78, 22, w * 0.78 + 26, 34], fill=(200, 200, 210), outline=NAVY, width=1)
    d.rectangle([w * 0.78 - 14, 24, w * 0.78, 32], fill=(80, 130, 200))
    d.rectangle([w * 0.78 + 26, 24, w * 0.78 + 40, 32], fill=(80, 130, 200))
    d.polygon([(w * 0.10, 30), (w * 0.10 + 12, 18), (w * 0.10 + 24, 30)], fill=(255, 255, 255))
    d.rectangle([w * 0.10 + 2, 30, w * 0.10 + 22, 44], fill=BRICK)
    return im

def scene_russia(w, h):
    im, d = layer(w, h, (176, 208, 226))
    cloud(d, 14, 8, 26)
    # sea
    d.rectangle([0, h * 0.55, w, h], fill=(60, 120, 170))
    for wy in range(int(h * 0.58), h, 12):
        d.line([(0, wy), (w, wy)], fill=(120, 180, 220), width=1)
    # cargo ship
    d.rectangle([w * 0.08, h * 0.42, w * 0.62, h * 0.58], fill=(40, 40, 60))
    for i, c in enumerate([(178, 58, 44), (214, 164, 62), (74, 120, 74)]):
        d.rectangle([w * 0.12 + i * w * 0.15, h * 0.28, w * 0.12 + (i + 1) * w * 0.15 - 4, h * 0.42], fill=c)
    d.rectangle([w * 0.56, h * 0.34, w * 0.62, h * 0.42], fill=(240, 240, 240))
    # drone + blast
    d.ellipse([w * 0.72, 14, w * 0.72 + 16, 24], fill=(30, 30, 30))
    d.line([(w * 0.72 - 6, 12), (w * 0.72 + 22, 12)], fill=(30, 30, 30), width=2)
    d.line([(w * 0.72 + 8, 24), (w * 0.60, h * 0.30)], fill=(255, 120, 40), width=2)
    d.ellipse([w * 0.56, h * 0.26, w * 0.56 + 18, h * 0.26 + 18], fill=(255, 170, 60))
    # Kremlin silhouette (right)
    for tx in (w * 0.78, w * 0.86, w * 0.94):
        d.rectangle([tx, h * 0.44, tx + 12, h * 0.62], fill=BRICK)
        d.polygon([(tx - 2, h * 0.44), (tx + 6, h * 0.34), (tx + 14, h * 0.44)], fill=(200, 60, 50))
    return im

def scene_korea(w, h):
    im, d = layer(w, h, (240, 232, 208))
    # classroom: board + desks + exam papers (people stand below the board text)
    d.rectangle([w * 0.10, 6, w * 0.90, 24], fill=(74, 120, 74), outline=NAVY, width=2)
    f = sans(10, True)
    d.text((w * 0.14, 10), "NATIONAL EXAM", font=f, fill=(255, 255, 255))
    d.text((w * 0.70, 10), "RESIGNS", font=f, fill=(255, 190, 60))
    for i, dx in enumerate([w * 0.12, w * 0.44, w * 0.76]):
        d.rectangle([dx, h - 26, dx + w * 0.20, h - 18], fill=(180, 140, 90))
        d.rectangle([dx + 4, h - 32, dx + w * 0.20 - 4, h - 26], fill=(255, 255, 255), outline=NAVY, width=1)
        d.line([(dx + 8, h - 29), (dx + w * 0.20 - 8, h - 29)], fill=(150, 150, 150), width=1)
        person(d, dx + w * 0.10, h - 42, 12, (120, 130, 160) if i % 2 else (200, 170, 120), (60, 60, 80))
    return im

def scene_vaibhav(w, h):
    im, d = layer(w, h, (140, 190, 110))
    # pitch + stumps
    d.rectangle([0, h * 0.55, w, h], fill=(90, 150, 80))
    d.rectangle([w * 0.30, h * 0.62, w * 0.70, h * 0.95], fill=(210, 180, 130))
    for sx in (w * 0.62, w * 0.64, w * 0.66):
        d.line([(sx, h * 0.66), (sx, h * 0.78)], fill=GOLD, width=3)
    # batsman mid-swing
    person(d, w * 0.46, h * 0.30, 34, (30, 90, 160), (255, 255, 255))
    d.line([(w * 0.46 + 8, h * 0.42), (w * 0.46 + 34, h * 0.22)], fill=(180, 140, 90), width=4)
    d.ellipse([w * 0.46 + 34, h * 0.20, w * 0.46 + 42, h * 0.28], fill=(255, 255, 255))
    # sixes flying
    for i, (bx, by) in enumerate([(w * 0.70, 16), (w * 0.80, 28), (w * 0.88, 12)]):
        d.ellipse([bx, by, bx + 7, by + 7], fill=(255, 255, 255), outline=BRICK, width=1)
    # scoreboard (clear of the top-left badge zone)
    d.rectangle([34, 8, 144, 34], fill=NAVY)
    f = sans(13, True)
    d.text((40, 12), "204  •  28 SIXES", font=f, fill=(255, 220, 90))
    return im

def scene_dutch(w, h):
    im, d = layer(w, h, (176, 208, 226))
    cloud(d, 10, 8, 26)
    # courthouse
    d.rectangle([w * 0.08, h * 0.42, w * 0.58, h], fill=(232, 228, 218))
    d.polygon([(w * 0.06, h * 0.42), (w * 0.33, h * 0.22), (w * 0.60, h * 0.42)], fill=NAVY)
    for i in range(4):
        cx = w * 0.12 + i * w * 0.11
        d.rectangle([cx, h * 0.46, cx + 8, h - 6], fill=(180, 176, 166))
    # gavel
    d.line([(w * 0.66, h * 0.60), (w * 0.86, h * 0.40)], fill=(120, 80, 40), width=5)
    d.rectangle([w * 0.80, h * 0.32, w * 0.94, h * 0.44], fill=(120, 80, 40))
    d.rectangle([w * 0.66, h * 0.62, w * 0.88, h * 0.70], fill=(180, 140, 90))
    # wind turbine
    d.line([(w * 0.70, h * 0.30), (w * 0.70, h * 0.75)], fill=(255, 255, 255), width=3)
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        d.line([(w * 0.70, h * 0.30),
                (w * 0.70 + 20 * math.cos(a), h * 0.30 + 20 * math.sin(a))],
               fill=(255, 255, 255), width=3)
    return im

def scene_huawei(w, h):
    im, d = layer(w, h, (222, 208, 186))
    # courtroom bench + judge
    d.rectangle([0, h * 0.55, w, h], fill=(120, 80, 40))
    d.rectangle([w * 0.30, h * 0.30, w * 0.70, h * 0.55], fill=(90, 60, 30))
    person(d, w * 0.50, h * 0.08, 26, (20, 20, 20), (20, 20, 20))
    # verdict sign (clear of the top-left badge zone)
    d.rectangle([34, 10, 158, 40], fill=(255, 255, 255), outline=BRICK, width=2)
    f = sans(11, True)
    d.text((39, 14), "10 OF 12", font=f, fill=BRICK)
    d.text((39, 26), "GUILTY", font=f, fill=BRICK)
    # gavel (right)
    d.line([(w * 0.80, h * 0.42), (w * 0.92, h * 0.30)], fill=(120, 80, 40), width=4)
    d.rectangle([w * 0.88, h * 0.24, w * 0.98, h * 0.34], fill=(120, 80, 40))
    # flags
    d.line([(w * 0.08, 12), (w * 0.08, h * 0.50)], fill=(60, 60, 60), width=2)
    d.rectangle([w * 0.08, 12, w * 0.08 + 22, 26], fill=BRICK)
    return im

# ---------------- hero panels ----------------
def hero_panel(d, x, y, w, h, num, scene_fn, headline, body, region, status,
               source, large, top_story=False):
    outline(d, (x, y, x + w, y + h))
    ill_h = 124 if large else 64
    scene = scene_fn(w - 4, ill_h)
    d._image.paste(scene, (x + 2, y + 2))
    badge(d, x + 16, y + 16, num, r=10)
    if top_story:
        d.rectangle([x + 2, y + 2, x + w - 2, y + 22], fill=BRICK)
        f = sans(11, True)
        t = "★  TOP STORY  ★"
        d.text((x + w / 2 - d.textlength(t, font=f) / 2, y + 5), t, font=f,
               fill=(255, 255, 255))
        badge(d, x + 16, y + 34, num, r=10)
    ty = y + ill_h + 8
    hf, hl = fit_lines(d, headline, "DejaVuSerif-Bold.ttf",
                       19 if large else 14, w - 16, 2 if large else 1)
    for ln in hl:
        d.text((x + 8, ty), ln, font=hf, fill=NAVY)
        ty += hf.size + 2
    bf, bl = fit_lines(d, body, "DejaVuSans.ttf", 11 if large else 10,
                       w - 16, 2)
    for ln in bl:
        d.text((x + 8, ty), ln, font=bf, fill=INK)
        ty += bf.size + 3
    tf = sans(9 if large else 8, True)
    tag = f"{region}  •  {status}"
    d.text((x + 8, y + h - 16), tag, font=tf, fill=BRICK)
    tw = d.textlength(tag, font=tf)
    sf_size = 8
    sf = sans(sf_size, True)
    sw = d.textlength(source, font=sf)
    while sf_size > 6 and x + 8 + tw + 10 + sw > x + w - 8:
        sf_size -= 1
        sf = sans(sf_size, True)
        sw = d.textlength(source, font=sf)
    src = source
    while len(src) > 4 and x + 8 + tw + 10 + sw > x + w - 8:
        src = src[:-4] + "…"
        sw = d.textlength(src, font=sf)
    d.text((x + w - 8 - sw, y + h - 15), src, font=sf, fill=GREY)

HEROES_LARGE = [
    (1, scene_cartagena, "CARTAGENA SUPERMARKET SIEGE",
     "30 hostages taken in an Éxito store; 10 freed, ~20 still held as captors demand $2M + safe passage.",
     "AMERICAS", "REPORTED", "Sky News / IANS / Reuters", True),
    (2, scene_cia, "CIA + ODNI CYBERATTACK",
     "US spy agencies hit by a cyberattack on classified systems, CNN reports — 2 agencies hit.",
     "NORTH AMERICA", "REPORTED", "CNN, 25 Nov", False),
    (3, scene_iowa, "IOWA LEAD-AZIDE DETONATION",
     "Army to blow up 9,500 lbs of ageing lead azide — the biggest such blast in nearly 50 years; plume 100+ miles.",
     "NORTH AMERICA", "CONFIRMED", "Des Moines Register / US Army", False),
]
HEROES_MED = [
    (4, scene_nato, "NATO VOWS SPACE DEFENSE",
     "NATO vows to defend space after reports Russia may launch a nuclear-armed satellite, possibly Dec 2026.",
     "EUROPE", "REPORTED", "25 Nov"),
    (5, scene_russia, "RUSSIA ACCUSES UKRAINE OF “TERRORISM”",
     "Moscow warns of severe consequences after drone strikes on 2 Russian ships — in the Gulf of Finland and off Benghazi.",
     "EUROPE", "REPORTED", "25 Nov"),
    (6, scene_korea, "SOUTH KOREA EDUCATION MINISTER RESIGNS",
     "Minister Choi Kyo-jin quits over a national exam-cheating scandal.",
     "ASIA", "CONFIRMED", "25 Nov"),
    (8, scene_vaibhav, "VAIBHAV 204 OFF 53 BALLS",
     "India A star smashes the fastest List A double century — 204 off 53 balls, a world-record 28 sixes.",
     "ASIA / SPORT", "CONFIRMED", "Rising Stars Asia Cup"),
    (9, scene_dutch, "DUTCH COURT: CLIMATE TARGETS BINDING",
     "The Hague court keeps binding Dutch climate targets in force while the state’s appeal proceeds.",
     "EUROPE", "CONFIRMED", "NOS, 25 Nov"),
    (10, scene_huawei, "HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "Brooklyn jury convicts on bank fraud, wire fraud, sanctions violations and trade-secret theft.",
     "ASIA / TECH", "REPORTED", "25 Nov"),
]
ALSO = [
    (7, "AUSTRALIA–SOLOMON ISLANDS SECURITY PACT"),
    (11, "COP31 ENDS WITHOUT A DEAL"),
    (12, "GAZA DEATH TOLL 74,746"),
    (13, "266 MILLION FACE ACUTE FOOD INSECURITY"),
    (14, "WHO EVACUATES DRC EBOLA STAFF"),
    (15, "NORTH KOREA THREATENS SWISS OFFICE"),
    (16, "SETTLER ARSON CONDEMNED AS “JEWISH TERRORISM”"),
    (17, "12,000 EVACUATED FROM MANCHESTER CONCERT"),
    (18, "ANMER HALL BREAK-IN ARRESTS"),
    (19, "GIULIANI AWARDED MEDAL OF FREEDOM"),
    (20, "TRUMP SET TO UNVEIL NEW TARIFFS"),
    (21, "ÁBREGO GARCÍA LEAVES FOR SPAIN"),
    (22, "SENEGAL AFCON CHAMPIONS REINSTATED"),
    (23, "GUKESH HOLDS SINDAROV IN OPENER"),
    (24, "IRANIAN SINGER GETS 74 LASHES"),
    (25, "SHEIKH HASINA ANNOUNCES RETURN"),
    (26, "MACRON WEIGHS SPENDING CAPS"),
    (27, "NSW $35M DRUG SYNDICATE CHARGED"),
    (28, "ASIAN TECH SHARES SLIDE"),
    (29, "LEWIS PUGH SWIMS HORMUZ"),
    (30, "ISRAEL: IRAN DEVELOPING CHEMICAL WEAPONS"),
    (31, "LIKUD FRAUD CLAIMS DISMISSED"),
    (32, "EAST BENGAL HISTORIC WIN"),
    (33, "BEN STOKES ENTERS IPL 2027 AUCTION"),
    (34, "ARSENAL HELD BY DORTMUND"),
    (35, "KINBURN SPIT RESCUE MISSION"),
    (36, "PT USHA OUT OF IOA RACE"),
]
NUMBERS = [("30", "HOSTAGES TAKEN IN CARTAGENA"),
           ("9,500", "LBS OF LEAD AZIDE, IOWA BLAST"),
           ("74,746", "GAZA DEATH TOLL"),
           ("266M", "FACE ACUTE FOOD INSECURITY"),
           ("204", "RUNS OFF 53 BALLS — 28 SIXES"),
           ("10 of 12", "COUNTS: HUAWEI GUILTY")]

def build(path):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # ---- masthead ----
    f = serif(46)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(t, font=f)) / 2, 8), t, font=f, fill=NAVY)
    f2 = sans(13, True)
    t2 = "WEDNESDAY 25 NOVEMBER 2026  —  36 STORIES FROM 6 REGIONS"
    d.text(((W - d.textlength(t2, font=f2)) / 2, 60), t2, font=f2, fill=BRICK)
    d.line([(M, 80), (W - M, 80)], fill=NAVY, width=3)
    d.line([(M, 84), (W - M, 84)], fill=NAVY, width=1)
    # ---- numbers strip ----
    y0, y1 = 88, 140
    outline(d, (M, y0, W - M, y1))
    cw = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * cw
        if i:
            d.line([(cx, y0 + 4), (cx, y1 - 4)], fill=GREY, width=1)
        nf = fit_font(d, num, "DejaVuSans-Bold.ttf", 26, cw - 16)
        d.text((cx + (cw - d.textlength(num, font=nf)) / 2, y0 + 4), num,
               font=nf, fill=NAVY)
        lf = fit_font(d, lab, "DejaVuSans-Bold.ttf", 9, cw - 12, min_size=7)
        d.text((cx + (cw - d.textlength(lab, font=lf)) / 2, y0 + 34), lab,
               font=lf, fill=BRICK)
    # ---- 3 large heroes ----
    y = 144
    hw = 320
    for i, (num, fn, head, body, reg, st, src, top) in enumerate(HEROES_LARGE):
        x = M + i * (hw + 10)
        hero_panel(d, x, y, hw, 228, num, fn, head, body, reg, st, src, True, top)
    # ---- 6 medium heroes, 2 rows of 3 ----
    y = 376
    for row in range(2):
        for i in range(3):
            num, fn, head, body, reg, st, src = HEROES_MED[row * 3 + i]
            x = M + i * (hw + 10)
            hero_panel(d, x, y, hw, 140, num, fn, head, body, reg, st, src, False)
        y += 144
    # ---- bottom row: map (left) + ALSO (right) ----
    y = 660
    map_x, map_w, map_h = M, 460, 286
    outline(d, (map_x, y, map_x + map_w, y + map_h))
    d.rectangle([map_x + 2, y + 2, map_x + map_w - 2, y + 28], fill=NAVY)
    tf = sans(12, True)
    d.text((map_x + 10, y + 8), "WHERE IT HAPPENED — 36 STORIES, 36 PLACES",
           font=tf, fill=(255, 255, 255))
    draw_map(d, map_x + 8, y + 32, map_w - 16, 196)
    # region index under map: 6 cols x 6 rows
    ix, iy = map_x + 10, y + 232
    colw = (map_w - 16) / 6
    for i, n in enumerate(range(1, 37)):
        cx = ix + (i % 6) * colw
        cy = iy + (i // 6) * 9
        txt = f"{n} {PLACE[n]}"
        fnt = fit_font(d, txt, "DejaVuSans.ttf", 9, colw - 3, min_size=7)
        d.text((cx, cy), txt, font=fnt, fill=INK)
    # ALSO list
    ax, aw = 492, 510
    outline(d, (ax, y, ax + aw, y + map_h))
    tf = sans(13, True)
    d.text((ax + 10, y + 8), "ALSO ON 25 NOVEMBER", font=tf, fill=NAVY)
    d.line([(ax + 8, y + 28), (ax + aw - 8, y + 28)], fill=BRICK, width=2)
    colw2 = (aw - 20) / 2
    for i, (n, title) in enumerate(ALSO):
        col = i // 14
        row = i % 14
        cx = ax + 10 + col * colw2
        cy = y + 34 + row * 18
        badge(d, cx + 7, cy + 6, n, r=7)
        fnt = fit_font(d, title, "DejaVuSans.ttf", 10, colw2 - 22, min_size=7)
        d.text((cx + 18, cy), title, font=fnt, fill=INK)
    # ---- date check ----
    y = 950
    d.rectangle([M, y, W - M, y + 28], fill=(238, 228, 205), outline=NAVY, width=1)
    dc = ("DATE CHECK — LEFT OUT: Anthropic $2T IPO (19 Nov) • Russian extradition "
          "(5 Nov) • Missiles over Poland (20 Nov) • Tarwekamp blast (Dec 2024). "
          "Huawei verdict was 24 Nov, reported 25 Nov in Asia.")
    df = fit_font(d, dc, "DejaVuSans.ttf", 10, W - 2 * M - 16, min_size=7)
    d.text((M + 8, y + 8), dc, font=df, fill=INK)
    # ---- footer ----
    y = 982
    d.line([(M, y), (W - M, y)], fill=NAVY, width=2)
    ff = sans(9, True)
    ft = "Every story above happened or was first reported on Wednesday 25 November 2026."
    d.text(((W - d.textlength(ft, font=ff)) / 2, y + 5), ft, font=ff, fill=NAVY)
    fs = sans(8)
    ft2 = "Sources: Reuters • CNN • AP • NOS • Sky News • IANS • Des Moines Register • WHO • WFP"
    d.text(((W - d.textlength(ft2, font=fs)) / 2, y + 17), ft2, font=fs, fill=GREY)
    print("BOTTOM y = %d  page H = %d" % (y + 30, H))
    img.save(path)
    print("saved", path, os.path.getsize(path), "bytes")
