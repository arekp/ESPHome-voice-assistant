# Obudowa asystenta głosowego na bazie szablonu Thingiverse 6110473 (GC9A01 Round OLED Case, mikeyisinoz, CC BY).
# Skrypt Fusion 360 (Utilities > Scripts, albo przez MCP). Tworzy nowy dokument (Direct Design):
#   - "Obudowa ESP32" – nowa skrzynka: górne GORA mm (kołnierz pod pokrywę Middle) skopiowane 1:1
#     z GC9A01_Round_OLED_Case_ribbed_usb.stl, niżej ten sam przekrój, wydłużony pod ESP32-S3,
#     z mocowaniem płytki, otworem USB-C w dnie, gondolami mikrofonu INMP441 na prawym i (lustrzanie, MIC_LEFT)
#     lewym boku (osobne wciskane kratki) i ramką wzmacniacza MAX98357A,
#   - "Szablon (pokrywa)" – oryginalne Middle / Support / Front z szablonu (siatki, tylko podgląd),
#   - "Elektronika (podgląd)" – obwiednie modułów (docs/WYMIARY_KOMPONENTOW.md) do kontroli kolizji.
#   - "Statecznik" – płetwa w stylu Star Trek za tylną ścianką z głośnikiem 63 x 63 (Ø45, gł. 12), z dwóch części:
#     korpus (kratka na lewym boku) i pokrywka; przykręcana do dna obudowy 3 x M3x8 + nakrętki.
# Eksport: obudowa/obudowa_esp32.stl, statecznik_korpus.stl, statecznik_pokrywa.stl, kratka_mikrofonu.stl.
# Układ: Z – od tylnej ścianki (z = 0) do przodu (wyświetlacz), -Y – strona z wyprowadzeniami wyświetlacza
# (wycięcie w Middle), +X – prawy bok (mikrofon). Wymiary w mm.
import adsk.core, adsk.fusion, math, os, traceback

DIR = r'C:\Projekty\ESPHome-voice-assistant\obudowa'
SZABLON = os.path.join(DIR, 'szablon1')
CASE_STL = os.path.join(SZABLON, 'GC9A01_Round_OLED_Case_ribbed_usb.stl')
CASE_C = (-98.0525, -47.9435)      # środek XY szablonu w jego współrzędnych
CASE_TOP = 63.97                   # wysokość szablonu (kołnierz 58,97–63,97)

# ---- obudowa ----
H = 72.0            # nowa wysokość skrzynki (szablon 63,97)
GORA = 10.0         # tyle mm od góry zostaje z szablonu bez zmian
FLOOR = 2.0         # grubość dna (tylnej ścianki)
# przekrój szablonu (z wierzchołków STL): obrys zewnętrzny i wnętrze, przeciwnie do wskazówek zegara
OUTER = [(-24.948, -20.02), (-20.024, -24.944), (19.97, -24.944), (24.948, -19.967),
         (24.948, 20.236), (20.24, 24.944), (-19.676, 24.944), (-24.948, 19.673)]
INNER = [(-23.003, -18.71), (-18.667, -23.046), (18.698, -23.046), (22.997, -18.747),
         (22.997, 18.89), (18.933, 22.954), (-18.702, 22.954), (-23.003, 18.654)]
IX0, IX1, IY0, IY1 = -23.003, 22.997, -23.046, 22.954   # wnętrze

# ---- ESP32-S3 YD (płytka pionowo, USB-C w dół do dna, goldpiny w stronę lewej ściany -X) ----
ESP_W, ESP_PCB, ESP_LEN, ESP_T, ESP_TOP, ESP_UNDER = 27.94, 57.15, 63.39, 1.6, 4.5, 25.0
USB_C1, USB_C2 = 8.1, 19.8          # środki gniazd od krawędzi płytki (symetryczne: 27,94 - 8,1 = 19,84)
PLUG_W, PLUG_H = 12.5, 7.5          # otwór na wtyk USB-C (z osłoną)
ESP_X0 = IX0 + ESP_UNDER            # spód PCB (strona goldpinów)
ESP_Y1 = IY1 - 2.0                  # odsunięcie od fazy w narożniku (wtyki dupont)
ESP_Y0 = ESP_Y1 - ESP_W
RIB_T, RIB_FLANGE_W, RIB_FLANGE_T = 2.4, 15.0, 1.6   # żebro między rzędami goldpinów (taśma dwustronna)

# ---- mikrofon INMP441: gondola czujnika na zewnątrz prawego boku (+X), port skierowany do przodu (+Z) ----
# Kanał kwadratowy na PCB 14 x 14, płytka wsuwana od przodu na półkę, dociskana wciskaną kratką („kolektor Bussarda”).
# Goldpiny przy krawędzi od strony obudowy, przewody wchodzą do środka przez szczelinę w ściance.
OX1 = 24.948                        # zewnętrzna prawa ścianka obudowy
MIC, MIC_WALL, MIC_R = 15.4, 3.5, 7.0    # kanał na PCB, ścianka gondoli, promień zewnętrznych narożników przekroju
MIC_YC, MIC_ZF, MIC_ZB = 6.0, 70.0, 42.0   # środek w Y, przód gondoli, dno kanału
MIC_RF, MIC_ZK, MIC_TAIL_R = 2.0, 46.0, 14.0   # zaokrąglenie przodu; początek ogona i jego promień (dalej 45° do ściany)
MIC_DOME, MIC_DOME_D = 1.5, 15.0          # kopułka kratki (wysokość, Ø)
MIC_BX0 = OX1 + 1.0                 # kanał: od strony obudowy
MIC_CAP_T, MIC_PCB_T, MIC_LEDGE = 2.0, 1.7, 2.0          # kratka, PCB (z luzem), szerokość półki
MIC_SLOT_W = 12.0                   # szczelina na przewody do wnętrza obudowy (szerokość w Y)
MIC_LEFT = True                     # druga, lustrzana gondola na lewym boku (-X); kratka ta sama – drukować 2 szt.
MIC_HOLES = [(0, 1, 2.0), (3.8, 8, 1.6), (6.2, 12, 1.2)]  # kratka: (promień, liczba, Ø)
# ---- wzmacniacz MAX98357A (dolna ścianka -Y, odsunięty od fazy prawego narożnika) ----
AMP_X, AMP_Z, AMP_Z0 = 20.2, 18.6, 33.7                # wewn. ramka (X, Z), początek w Z
AMP_X1 = 18.4                                          # prawa krawędź wnętrza ramki
FRAME_T, FRAME_H = 1.6, 3.5                            # grubość i wysokość ramek

# ---- statecznik z głośnikiem (za tylną ścianką, z < 0); profil w płaszczyźnie (z, y) ----
FIN = [(0, -24.94), (0, 24.94), (-14, 52), (-90, 60), (-104, 54), (-92, -24.94)]
SPK_SQ, SPK_DIA, SPK_DEPTH = 63.0, 45.0, 12.0   # głośnik: kwadrat ramki, membrana, głębokość
FIN_WALL, LID_T = 2.4, 2.4          # ścianki korpusu płetwy, grubość pokrywki
FIN_X0 = -24.948                    # płetwa przy lewym boku obudowy (z dala od otworu USB-C)
FIN_X1 = FIN_X0 + FIN_WALL + SPK_DEPTH + 1.0 + LID_T   # kieszeń = głębokość głośnika + 1 mm
SPK_C = (-52.0, 12.0)              # środek głośnika (z, y)
GRILL_W, GRILL_P = 2.0, 4.0        # szczeliny kratki (szerokość, rozstaw)
FIN_BOSS = [(-10, -18), (-10, 20), (-60, 51), (-95, 40)]     # tuleje wkrętów pokrywki (z, y)
FIN_SCREW = [(-17, -17), (-12, 12)]                         # M3 przez dno obudowy i nasadę płetwy (x, y)
SPK_WIRE = (-12, -8, 6.0)         # otwór na przewody głośnika w dnie i nasadzie (x, y, Ø)

MM = 0.1


def P(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def run(_context):
    app = adsk.core.Application.get()
    try:
        for d in list(app.documents):
            if d.name.startswith('Bez nazwy') or d.name.startswith('Untitled'):
                d.close(False)
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des = adsk.fusion.Design.cast(app.activeProduct)
        des.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = des.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        B = adsk.fusion.BooleanTypes

        def box(x0, x1, y0, y1, z0, z1):
            c = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
            o = adsk.core.OrientedBoundingBox3D.create(
                c, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                abs(x1 - x0) * MM, abs(y1 - y0) * MM, abs(z1 - z0) * MM)
            return tbm.createBox(o)

        def cyl(a, b, d):
            return tbm.createCylinderOrCone(P(*a), d / 2 * MM, P(*b), d / 2 * MM)

        def union(*bs):
            r = bs[0]
            for b in bs[1:]:
                tbm.booleanOperation(r, b, B.UnionBooleanType)
            return r

        # ---------- 1. górna część z szablonu (bez zmian) ----------
        mesh = root.meshBodies.add(CASE_STL, adsk.fusion.MeshUnits.MillimeterMeshUnit).item(0)
        mci = root.features.meshConvertFeatures.createInput([mesh])
        try:
            mci.meshConvertMethodType = adsk.fusion.MeshConvertMethodTypes.PrismaticMeshConvertMethodType
        except Exception:
            pass
        mcf = root.features.meshConvertFeatures.add(mci)
        conv = mcf.bodies.item(0) if hasattr(mcf, 'bodies') and mcf.bodies.count else root.bRepBodies.item(root.bRepBodies.count - 1)
        top = tbm.copy(conv)
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(-CASE_C[0] * MM, -CASE_C[1] * MM, (H - CASE_TOP) * MM)
        tbm.transform(top, m)
        tbm.booleanOperation(top, box(-30, 30, -30, 30, H - GORA, H + 1), B.IntersectionBooleanType)
        conv.deleteMe()                 # siatkę zużywa konwersja

        # ---------- 2. dolna część: ten sam przekrój, wydłużona ----------
        sk = root.sketches.add(root.xYConstructionPlane)
        L = sk.sketchCurves.sketchLines
        for poly in (OUTER, INNER):
            pts = [P(x, y, 0) for x, y in poly]
            for i in range(len(pts)):
                L.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])
        profs = sorted([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
        ring, inner = profs[0], profs[1]
        ex = root.features.extrudeFeatures
        e1 = ex.addSimple(ring, adsk.core.ValueInput.createByReal((H - GORA + 0.01) * MM),
                          adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        e2 = ex.addSimple(inner, adsk.core.ValueInput.createByReal(FLOOR * MM),
                          adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        case = union(tbm.copy(e1.bodies.item(0)), tbm.copy(e2.bodies.item(0)), top)
        e1.bodies.item(0).deleteMe()
        e2.bodies.item(0).deleteMe()
        sk.deleteMe()

        # ---------- 3. ESP32: żebro, ogranicznik, otwór USB-C ----------
        yc = (ESP_Y0 + ESP_Y1) / 2
        rib = union(box(IX0 - 0.5, ESP_X0 - RIB_FLANGE_T, yc - RIB_T / 2, yc + RIB_T / 2, FLOOR - 0.1, FLOOR + ESP_PCB - 2),
                    box(ESP_X0 - RIB_FLANGE_T, ESP_X0, yc - RIB_FLANGE_W / 2, yc + RIB_FLANGE_W / 2, FLOOR + 2, FLOOR + ESP_PCB - 2))
        stop = box(ESP_X0 - 2, ESP_X0 + ESP_T + ESP_TOP, ESP_Y0 - 2.3, ESP_Y0 - 0.3, FLOOR - 0.1, FLOOR + 3)
        union(case, rib, stop)
        ux = ESP_X0 + ESP_T + 1.6                      # oś gniazd USB-C (gniazdo 3,2 nad PCB)
        u0, u1 = ESP_Y0 + USB_C1 - PLUG_W / 2, ESP_Y0 + USB_C2 + PLUG_W / 2
        r = PLUG_H / 2
        usb = union(box(ux - r, ux + r, u0 + r, u1 - r, -1, FLOOR + 1),
                    cyl((ux, u0 + r, -1), (ux, u0 + r, FLOOR + 1), PLUG_H),
                    cyl((ux, u1 - r, -1), (ux, u1 - r, FLOOR + 1), PLUG_H))
        tbm.booleanOperation(case, usb, B.DifferenceBooleanType)

        # ---------- 4. mikrofon: gondola czujnika na prawym boku ----------
        def extrude_poly(plane, path, axis, a0, a1):
            # graniastosłup z konturu path między a0 i a1 wzdłuż osi axis; path: punkty 2D albo łuki
            # ('arc', cx, cy, r, kąt0, kąt1), współrzędne 2D to pozostałe dwie osie w kolejności x, y, z
            def p3(u, v):
                q = [u, v]
                q.insert(axis, 0.0)
                return sk3.modelToSketchSpace(P(*q))
            sk3 = root.sketches.add(plane)
            ends = []          # (początek, koniec, łuk lub None)
            for it in path:
                if it[0] == 'arc':
                    _, cx, cy, r, t0, t1 = it
                    pt = [(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t))) for t in (t0, (t0 + t1) / 2, t1)]
                    ends.append((pt[0], pt[2], pt))
                else:
                    ends.append((it, it, None))
            for i, (st, en, pt) in enumerate(ends):
                if pt:
                    sk3.sketchCurves.sketchArcs.addByThreePoints(p3(*pt[0]), p3(*pt[1]), p3(*pt[2]))
                nxt = ends[(i + 1) % len(ends)][0]
                if math.hypot(nxt[0] - en[0], nxt[1] - en[1]) > 1e-6:
                    sk3.sketchCurves.sketchLines.addByTwoPoints(p3(*en), p3(*nxt))
            f = root.features.extrudeFeatures.addSimple(sk3.profiles.item(0), adsk.core.ValueInput.createByReal((a1 - a0) * MM),
                                                        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            b = tbm.copy(f.bodies.item(0))
            mn = f.bodies.item(0).boundingBox.minPoint
            mn = (mn.x, mn.y, mn.z)[axis]
            f.bodies.item(0).deleteMe()
            sk3.deleteMe()
            v = [0.0, 0.0, 0.0]
            v[axis] = a0 * MM - mn
            mt = adsk.core.Matrix3D.create()
            mt.translation = adsk.core.Vector3D.create(*v)
            tbm.transform(b, mt)
            return b

        def arc(cx, cy, r, a0, a1, n=None):
            return [('arc', cx, cy, r, a0, a1)]

        bx0, bx1 = MIC_BX0, MIC_BX0 + MIC
        by0, by1 = MIC_YC - MIC / 2, MIC_YC + MIC / 2
        px0, px1 = OX1 - 0.5, bx1 + MIC_WALL
        py0, py1 = by0 - MIC_WALL, by1 + MIC_WALL
        # gondola = część wspólna trzech wyciągnięć: przekroju (x, y), profilu bocznego (x, z) i profilu z góry (y, z)
        rt, s2 = MIC_TAIL_R, math.sqrt(0.5)
        xa, za = px1 - rt + rt * s2, MIC_ZK - rt * s2          # koniec łuku ogona, dalej prosto pod 45°
        z_tip = za - (xa - px0)
        cs = [(px0, py0)] + arc(px1 - MIC_R, py0 + MIC_R, MIC_R, -90, 0) + arc(px1 - MIC_R, py1 - MIC_R, MIC_R, 0, 90) + [(px0, py1)]
        side = [(px0, z_tip)] + arc(px1 - rt, MIC_ZK, rt, -45, 0) + arc(px1 - MIC_RF, MIC_ZF - MIC_RF, MIC_RF, 0, 90, 4) + [(px0, MIC_ZF)]
        top = [(py0, z_tip - 1), (py1, z_tip - 1)] + arc(py1 - MIC_RF, MIC_ZF - MIC_RF, MIC_RF, 0, 90, 4) +               arc(py0 + MIC_RF, MIC_ZF - MIC_RF, MIC_RF, 90, 180, 4)
        pod = extrude_poly(root.xYConstructionPlane, cs, 2, z_tip - 1, MIC_ZF + 1)
        tbm.booleanOperation(pod, extrude_poly(root.xZConstructionPlane, side, 1, py0 - 1, py1 + 1),
                             B.IntersectionBooleanType)
        tbm.booleanOperation(pod, extrude_poly(root.yZConstructionPlane, top, 0, px0 - 1, px1 + 1),
                             B.IntersectionBooleanType)
        z_pcb = MIC_ZF - MIC_CAP_T - MIC_PCB_T          # półka pod PCB
        zl0 = z_pcb - 1.5
        mic_ops = [
            (B.UnionBooleanType, pod),
            (B.DifferenceBooleanType, box(bx0, bx1, by0, by1, MIC_ZB, MIC_ZF + 1)),
            (B.DifferenceBooleanType, box(bx0 - 1, bx1 + 1, by0 - 1, by1 + 1, MIC_ZF - MIC_CAP_T, MIC_ZF + 1)),
            # półka: cała krawędź zewnętrzna i zewnętrzne połowy boków (krawędź od obudowy wolna – goldpiny)
            (B.UnionBooleanType, union(box(bx1 - MIC_LEDGE, bx1 + 0.1, by0 - 0.1, by1 + 0.1, zl0, z_pcb),
                                       box(bx0 + MIC / 2, bx1 + 0.1, by0 - 0.1, by0 + MIC_LEDGE, zl0, z_pcb),
                                       box(bx0 + MIC / 2, bx1 + 0.1, by1 - MIC_LEDGE, by1 + 0.1, zl0, z_pcb))),
            # szczelina na przewody: z kanału gondoli do wnętrza obudowy
            (B.DifferenceBooleanType, box(IX1 - 1, bx0 + 1, MIC_YC - MIC_SLOT_W / 2, MIC_YC + MIC_SLOT_W / 2, MIC_ZB, zl0)),
        ]
        mirror = adsk.core.Matrix3D.create()             # odbicie x -> -x (druga gondola na lewym boku)
        mirror.setCell(0, 0, -1)

        def mirrored(b):
            b = tbm.copy(b)
            tbm.transform(b, mirror)
            return b

        for op, b in mic_ops:
            tbm.booleanOperation(case, tbm.copy(b), op)
        if MIC_LEFT:
            for op, b in mic_ops:
                tbm.booleanOperation(case, mirrored(b), op)
        # kratka wciskana w gniazdo (luz 0,15 na stronę)
        mic_cap = box(bx0 - 0.85, bx1 + 0.85, by0 - 0.85, by1 + 0.85, MIC_ZF - MIC_CAP_T, MIC_ZF)
        mcx = (bx0 + bx1) / 2
        rs = ((MIC_DOME_D / 2) ** 2 + MIC_DOME ** 2) / (2 * MIC_DOME)      # kopułka: czasza kuli
        dome = tbm.createSphere(P(mcx, MIC_YC, MIC_ZF + MIC_DOME - rs), rs * MM)
        tbm.booleanOperation(dome, box(mcx - 10, mcx + 10, MIC_YC - 10, MIC_YC + 10, MIC_ZF - 0.01, MIC_ZF + 5), B.IntersectionBooleanType)
        union(mic_cap, dome)
        for r_, n_, d_ in MIC_HOLES:
            for i in range(n_):
                a = 2 * math.pi * i / n_
                x, y = mcx + r_ * math.cos(a), MIC_YC + r_ * math.sin(a)
                tbm.booleanOperation(mic_cap, cyl((x, y, MIC_ZF - MIC_CAP_T - 1), (x, y, MIC_ZF + MIC_DOME + 1), d_), B.DifferenceBooleanType)

        # ---------- 5. wzmacniacz: ramka na dolnej ściance (-Y) przy prawym boku + otwór na przewody ----------
        ax0, ax1, az1 = AMP_X1 - AMP_X, AMP_X1, AMP_Z0 + AMP_Z
        amp_fr = box(ax0 - FRAME_T, ax1 + FRAME_T, IY0 - 0.5, IY0 + FRAME_H, AMP_Z0 - FRAME_T, az1 + FRAME_T)
        tbm.booleanOperation(amp_fr, box(ax0, ax1, IY0 - 1, IY0 + FRAME_H + 1, AMP_Z0, az1), B.DifferenceBooleanType)
        union(case, amp_fr)
        # otwory w dnie: przewody głośnika i wkręty statecznika
        for x, y, d in [SPK_WIRE] + [(x, y, 3.4) for x, y in FIN_SCREW]:
            tbm.booleanOperation(case, cyl((x, y, -1), (x, y, FLOOR + 1), d), B.DifferenceBooleanType)

        body = root.bRepBodies.add(case)
        body.name = 'Obudowa ESP32'
        cap_body = root.bRepBodies.add(mic_cap)
        cap_body.name = 'Kratka mikrofonu'
        if MIC_LEFT:
            root.bRepBodies.add(mirrored(mic_cap)).name = 'Kratka mikrofonu (lewa)'

        # ---------- 5a. statecznik z głośnikiem ----------
        def offset_poly(poly, d):
            # przesunięcie wielokąta (z, y) do środka o d
            n = len(poly)
            area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
            sgn = 1 if area > 0 else -1
            lines = []
            for i in range(n):
                (a0, a1), (b0, b1) = poly[i], poly[(i + 1) % n]
                l = math.hypot(b0 - a0, b1 - a1)
                nx, ny = -(b1 - a1) / l * sgn, (b0 - a0) / l * sgn      # normalna do wnętrza
                lines.append(((a0 + nx * d, a1 + ny * d), (b0 - a0, b1 - a1)))
            out = []
            for i in range(n):
                (p, r), (q, s_) = lines[i - 1], lines[i]
                den = r[0] * s_[1] - r[1] * s_[0]
                t = ((q[0] - p[0]) * s_[1] - (q[1] - p[1]) * s_[0]) / den
                out.append((p[0] + t * r[0], p[1] + t * r[1]))
            return out

        def prism(poly, x0, x1):
            # graniastosłup o profilu (z, y) między x0 i x1
            sk2 = root.sketches.add(root.yZConstructionPlane)
            pts = [sk2.modelToSketchSpace(P(0, y, z)) for z, y in poly]
            for i in range(len(pts)):
                sk2.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])
            f = root.features.extrudeFeatures.addSimple(sk2.profiles.item(0), adsk.core.ValueInput.createByReal((x1 - x0) * MM),
                                                        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            b = tbm.copy(f.bodies.item(0))
            mn = f.bodies.item(0).boundingBox.minPoint.x
            f.bodies.item(0).deleteMe()
            sk2.deleteMe()
            mt = adsk.core.Matrix3D.create()
            mt.translation = adsk.core.Vector3D.create(x0 * MM - mn, 0, 0)
            tbm.transform(b, mt)
            return b

        lid_x0 = FIN_X1 - LID_T
        cav_x0 = FIN_X0 + FIN_WALL
        fin = prism(FIN, FIN_X0, lid_x0)
        tbm.booleanOperation(fin, prism(offset_poly(FIN, FIN_WALL), cav_x0, lid_x0 + 1), B.DifferenceBooleanType)
        sz, sy = SPK_C
        # ramka ustalająca głośnik na wewnętrznej stronie kratki
        hs = SPK_SQ / 2 + 0.3
        sq = box(cav_x0 - 0.1, cav_x0 + 3, sy - hs - FRAME_T, sy + hs + FRAME_T, sz - hs - FRAME_T, sz + hs + FRAME_T)
        tbm.booleanOperation(sq, box(cav_x0 - 1, cav_x0 + 4, sy - hs, sy + hs, sz - hs, sz + hs), B.DifferenceBooleanType)
        tbm.booleanOperation(sq, prism(FIN, FIN_X0, lid_x0), B.IntersectionBooleanType)
        union(fin, sq)
        # tuleje wkrętów pokrywki
        for z, y in FIN_BOSS:
            boss = cyl((cav_x0 - 0.1, y, z), (lid_x0, y, z), 7.0)
            tbm.booleanOperation(boss, prism(FIN, FIN_X0, lid_x0), B.IntersectionBooleanType)
            union(fin, boss)
            tbm.booleanOperation(fin, cyl((cav_x0 + 1, y, z), (lid_x0 + 1, y, z), 2.5), B.DifferenceBooleanType)
        # kratka: poziome szczeliny (jak gondola warp) w kole Ø membrany + rowek „deflektora”
        rr = SPK_DIA / 2 - 0.5
        k = 0
        while True:
            dy = -rr + 1.5 + k * GRILL_P
            if dy > rr - 1.5:
                break
            hl = math.sqrt(rr * rr - dy * dy) - GRILL_W / 2
            if hl > 1:
                slot = union(box(FIN_X0 - 1, cav_x0 + 1, sy + dy - GRILL_W / 2, sy + dy + GRILL_W / 2, sz - hl, sz + hl),
                             cyl((FIN_X0 - 1, sy + dy, sz - hl), (cav_x0 + 1, sy + dy, sz - hl), GRILL_W),
                             cyl((FIN_X0 - 1, sy + dy, sz + hl), (cav_x0 + 1, sy + dy, sz + hl), GRILL_W))
                tbm.booleanOperation(fin, slot, B.DifferenceBooleanType)
            k += 1
        ring = cyl((FIN_X0 - 1, sy, sz), (FIN_X0 + 0.8, sy, sz), SPK_DIA + 7)
        tbm.booleanOperation(ring, cyl((FIN_X0 - 2, sy, sz), (FIN_X0 + 2, sy, sz), SPK_DIA + 4), B.DifferenceBooleanType)
        tbm.booleanOperation(fin, ring, B.DifferenceBooleanType)
        # nasada: wkręty do dna obudowy i przewody głośnika
        for x, y, d in [SPK_WIRE] + [(x, y, 3.4) for x, y in FIN_SCREW]:
            tbm.booleanOperation(fin, cyl((x, y, 1), (x, y, -FIN_WALL - 1), d), B.DifferenceBooleanType)
        lid = prism(FIN, lid_x0, FIN_X1)
        for z, y in FIN_BOSS:
            tbm.booleanOperation(lid, cyl((lid_x0 - 1, y, z), (FIN_X1 + 1, y, z), 3.4), B.DifferenceBooleanType)
        fin_body = root.bRepBodies.add(fin)
        fin_body.name = 'Statecznik - korpus'
        lid_body = root.bRepBodies.add(lid)
        lid_body.name = 'Statecznik - pokrywa'

        # ---------- 6. podgląd: pokrywa z szablonu ----------
        def mesh_occ(name, stl, mat):
            occ = root.occurrences.addNewComponent(mat)
            occ.component.name = name
            mb = occ.component.meshBodies.add(os.path.join(SZABLON, stl), adsk.fusion.MeshUnits.MillimeterMeshUnit)
            return occ

        def mat(flip, tx, ty, tz):
            mm_ = adsk.core.Matrix3D.create()
            if flip:   # obrót 180° wokół Y
                mm_.setWithCoordinateSystem(adsk.core.Point3D.create(tx * MM, ty * MM, tz * MM),
                                            adsk.core.Vector3D.create(-1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                                            adsk.core.Vector3D.create(0, 0, -1))
            else:
                mm_.translation = adsk.core.Vector3D.create(tx * MM, ty * MM, tz * MM)
            return mm_

        mesh_occ('Szablon Middle', 'GC9A01_Round_OLED_Middle_notched.stl', mat(True, -92.7, 25.695, H + 15))
        mesh_occ('Szablon Support', 'GC9A01_Round_OLED_Support.stl', mat(False, 30.71, 25.66, H))
        mesh_occ('Szablon Front', 'GC9A01_Round_OLED_Front_Contoured2.stl.stl', mat(False, -1.805, 94.745, H + 15))

        # ---------- 7. podgląd: elektronika ----------
        eo = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        ec = eo.component
        ec.name = 'Elektronika (podglad)'
        zt = H + 15 - 2                      # tył przedniej ścianki Middle = przód modułu wyświetlacza
        parts = {
            'ESP32 PCB': box(ESP_X0, ESP_X0 + ESP_T, ESP_Y0, ESP_Y1, FLOOR, FLOOR + ESP_PCB),
            'ESP32 WROOM': box(ESP_X0 + ESP_T, ESP_X0 + ESP_T + 3.3, yc - 9, yc + 9, FLOOR + ESP_LEN - 25.5, FLOOR + ESP_LEN),
            'ESP32 USB-C': union(box(ESP_X0 + ESP_T, ESP_X0 + ESP_T + 3.2, ESP_Y0 + USB_C1 - 4.5, ESP_Y0 + USB_C1 + 4.5, FLOOR, FLOOR + 7.5),
                                 box(ESP_X0 + ESP_T, ESP_X0 + ESP_T + 3.2, ESP_Y0 + USB_C2 - 4.5, ESP_Y0 + USB_C2 + 4.5, FLOOR, FLOOR + 7.5)),
            'ESP32 goldpiny+dupont': union(box(IX0 + 2.5, ESP_X0, ESP_Y0 + 0.02, ESP_Y0 + 2.52, FLOOR + 1, FLOOR + ESP_PCB - 1),
                                           box(IX0 + 2.5, ESP_X0, ESP_Y1 - 2.52, ESP_Y1 - 0.02, FLOOR + 1, FLOOR + ESP_PCB - 1)),
            'INMP441': union(box(bx0 + 0.7, bx1 - 0.7, by0 + 0.7, by1 - 0.7, z_pcb + 0.05, z_pcb + 1.65),
                             box(mcx - 2.5, mcx + 2.5, MIC_YC - 2.5, MIC_YC + 2.5, z_pcb - 1.2, z_pcb + 0.05)),
            'INMP441 dupont': box(bx0 + 0.7, bx0 + 3.2, by0 + 0.7, by1 - 0.7, z_pcb - 17, z_pcb),   # piny od strony obudowy
            'MAX98357A': box(AMP_X1 - 19.8, AMP_X1 - 0.4, IY0 + 0.05, IY0 + 3, AMP_Z0 + 0.4, AMP_Z0 + 0.4 + 17.8),
            'MAX98357A dupont': box(AMP_X1 - 3.4, AMP_X1 - 0.9, IY0 + 3, IY0 + 20, AMP_Z0 + 0.4, AMP_Z0 + 17.8),
            'GC9A01': union(cyl((0, 0, zt - 11.5), (0, 0, zt), 38), box(-8, 8, -22.75, -15, zt - 11.5, zt - 1.6)),
            'GC9A01 dupont': box(-10.2, 10.2, -22, -19.5, zt - 11.5 - 18, zt - 11.5),
            'Glosnik': union(box(cav_x0 + 0.05, cav_x0 + 3, sy - SPK_SQ / 2, sy + SPK_SQ / 2, sz - SPK_SQ / 2, sz + SPK_SQ / 2),
                             cyl((cav_x0 + 3, sy, sz), (cav_x0 + SPK_DEPTH, sy, sz), SPK_DIA - 5)),
        }
        if MIC_LEFT:
            parts['INMP441 (lewy)'] = mirrored(parts['INMP441'])
            parts['INMP441 dupont (lewy)'] = mirrored(parts['INMP441 dupont'])
        solids = [case, fin, lid, mic_cap] + ([mirrored(mic_cap)] if MIC_LEFT else [])
        report = []
        for name, b in parts.items():
            nb = ec.bRepBodies.add(b)
            nb.name = name
            nb.opacity = 0.6
            v = 0.0
            for sb in solids:
                hit = tbm.copy(sb)
                tbm.booleanOperation(hit, tbm.copy(b), B.IntersectionBooleanType)
                v += hit.volume * 1000 if hit.volume else 0.0
            report.append('%s: kolizja %.1f mm3' % (name, v) if v > 0.01 else '%s: OK' % name)

        # ---------- 8. eksport ----------
        bb = body.boundingBox
        print('Obudowa: %.2f x %.2f x %.2f mm, objetosc %.1f cm3' % (
            (bb.maxPoint.x - bb.minPoint.x) * 10, (bb.maxPoint.y - bb.minPoint.y) * 10,
            (bb.maxPoint.z - bb.minPoint.z) * 10, body.volume))
        print('\n'.join(report))
        em = des.exportManager
        for b, fn in ((body, 'obudowa_esp32.stl'), (fin_body, 'statecznik_korpus.stl'), (lid_body, 'statecznik_pokrywa.stl'),
                      (cap_body, 'kratka_mikrofonu.stl')):
            o = em.createSTLExportOptions(b, os.path.join(DIR, fn))
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            em.execute(o)
            bb = b.boundingBox
            print('STL %s: %.1f x %.1f x %.1f mm' % (fn, (bb.maxPoint.x - bb.minPoint.x) * 10,
                  (bb.maxPoint.y - bb.minPoint.y) * 10, (bb.maxPoint.z - bb.minPoint.z) * 10))
        app.activeViewport.fit()
    except Exception:
        print(traceback.format_exc())
