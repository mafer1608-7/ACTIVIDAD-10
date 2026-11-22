"""Utilidades para generar informes IEEE sobre la plantilla 'Plantilla IEEE-UMNG.docx' (python-docx)."""
import re
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FUENTE = "Garamond"
TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|\[\[.+?\]\]|_\{.+?\})")


class Informe:
    def __init__(self, plantilla):
        self.doc = docx.Document(plantilla)
        self.n_fig = 0
        self.n_tab = 0
        self._limpiar_cuerpo()

    # ------------------------------------------------------------ base
    def _limpiar_cuerpo(self):
        body = self.doc.element.body
        conservar = {p._p for p in self.doc.paragraphs[:4]}
        for hijo in list(body):
            if hijo.tag == qn("w:sectPr") or hijo in conservar:
                continue
            body.remove(hijo)

    @staticmethod
    def _fmt(run, size=None, bold=None, italic=None, hl=False, font=FUENTE):
        run.font.name = font
        rpr = run._r.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.insert(0, rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(a), font)
        if size:
            run.font.size = Pt(size)
        if bold is not None:
            run.font.bold = bold
        if italic is not None:
            run.font.italic = italic
        if hl:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW

    def _runs(self, par, texto, size=10, bold=None, italic=None):
        for trozo in TOKEN.split(texto):
            if not trozo:
                continue
            if trozo.startswith("**") and trozo.endswith("**"):
                r = par.add_run(trozo[2:-2]); self._fmt(r, size, True, italic)
            elif trozo.startswith("_{") and trozo.endswith("}"):
                r = par.add_run(trozo[2:-1]); self._fmt(r, size, bold, italic); r.font.subscript = True
            elif trozo.startswith("[[") and trozo.endswith("]]"):
                r = par.add_run("[" + trozo[2:-2] + "]"); self._fmt(r, size, bold, italic)
            elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
                r = par.add_run(trozo[1:-1]); self._fmt(r, size, bold, True)
            else:
                r = par.add_run(trozo); self._fmt(r, size, bold, italic)

    # ------------------------------------------------------------ portada
    def portada(self, titulo, autores, resumen, claves, fecha_pie=None):
        P = self.doc.paragraphs
        # titulo
        r = P[1].runs
        r[0].text = titulo
        for x in r[1:]:
            x._r.getparent().remove(x._r)
        # autores
        r = P[2].runs
        r[0].text = autores
        self._fmt(r[0], font="Courier New")
        for x in r[1:]:
            x._r.getparent().remove(x._r)
        # resumen
        r = P[3].runs
        r[0].text = resumen
        for x in r[1:]:
            x._r.getparent().remove(x._r)
        # palabras clave
        par = self.doc.add_paragraph(style="Index Terms") if "Index Terms" in [s.name for s in self.doc.styles] else self.doc.add_paragraph(style="IndexTerms")
        self._runs(par, "Palabras clave—" + claves, size=9, bold=True)
        # cabecera
        for t in self.doc.sections[0].header._element.iter(qn("w:t")):
            if t.text == "Asignatura, Semestre":
                t.text = "Micros y Laboratorio, Quinto Semestre"
        # pie de pagina (nota)
        for p in self.doc.part.package.iter_parts():
            if "footnotes" in str(p.partname):
                x = p.blob.decode("utf8")
                x = x.replace("<w:t>dia</w:t>", "<w:t>22</w:t>").replace("<w:t>mes</w:t>", "<w:t>noviembre</w:t>").replace("<w:t>año</w:t>", "<w:t>2026</w:t>")
                p._blob = x.encode("utf8")

    # ------------------------------------------------------------ texto
    def _sin_lista(self, par):
        ppr = par._p.get_or_add_pPr()
        num = OxmlElement("w:numPr")
        il = OxmlElement("w:ilvl"); il.set(qn("w:val"), "0")
        ni = OxmlElement("w:numId"); ni.set(qn("w:val"), "0")
        num.append(il); num.append(ni)
        ppr.append(num)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "0"); ind.set(qn("w:firstLine"), "0"); ind.set(qn("w:hanging"), "0")
        ppr.append(ind)

    def h1(self, texto):
        self._letra = 0
        self._romano = getattr(self, "_romano", 0) + 1
        romanos = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        par = self.doc.add_paragraph(style="Heading 1")
        self._sin_lista(par)
        self._runs(par, f"{romanos[self._romano - 1]}. {texto}", size=None)
        return par

    def h2(self, texto):
        # letra manual: la numeracion automatica se reinicia al insertar secciones de pagina completa
        self._letra = getattr(self, "_letra", 0) + 1
        par = self.doc.add_paragraph(style="Heading 2")
        self._sin_lista(par)
        self._runs(par, f"{chr(64 + self._letra)}. {texto}", size=None)
        return par

    def p(self, texto, size=10, align="both", sangria=True):
        par = self.doc.add_paragraph(style="Normal")
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if align == "both" else WD_ALIGN_PARAGRAPH.LEFT
        par.paragraph_format.space_after = Pt(4)
        self._runs(par, texto, size=size)
        return par

    def lista(self, items, size=10):
        for it in items:
            par = self.doc.add_paragraph(style="Normal")
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            par.paragraph_format.left_indent = Cm(0.5)
            par.paragraph_format.first_line_indent = Cm(-0.4)
            par.paragraph_format.space_after = Pt(2)
            self._runs(par, "• " + it, size=size)

    def ecuacion(self, expr, n):
        par = self.doc.add_paragraph(style="Normal")
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(3)
        self._runs(par, expr, size=10, italic=True)
        r = par.add_run(f"        ({n})")
        self._fmt(r, 10)

    # ------------------------------------------------------------ secciones a 1 / 2 columnas
    def _cols(self, n):
        sec = self.doc.sections[-1]._sectPr
        c = sec.find(qn("w:cols"))
        if c is None:
            c = OxmlElement("w:cols")
            sec.append(c)
        c.set(qn("w:num"), str(n))
        c.set(qn("w:space"), "288")

    def ancho_inicio(self):
        self.doc.add_section(WD_SECTION.CONTINUOUS)
        self._cols(1)

    def ancho_fin(self):
        self.doc.add_section(WD_SECTION.CONTINUOUS)
        self._cols(2)

    # ------------------------------------------------------------ figuras y tablas
    def figura(self, ruta, ancho_cm, pie, ancho_pagina=False):
        if ancho_pagina:
            self.ancho_inicio()
        par = self.doc.add_paragraph(style="Normal")
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_after = Pt(2)
        par.add_run().add_picture(ruta, width=Cm(ancho_cm))
        self.n_fig += 1
        cap = self.doc.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._runs(cap, f"Fig. {self.n_fig}. {pie}", size=9)
        if ancho_pagina:
            self.ancho_fin()
        return self.n_fig

    def marcador(self, texto, pie, alto_cm=3.2, ancho_pagina=False):
        """Recuadro para una imagen que debe insertar el estudiante (captura real)."""
        if ancho_pagina:
            self.ancho_inicio()
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = 1
        celda = t.cell(0, 0)
        tcpr = celda._tc.get_or_add_tcPr()
        b = OxmlElement("w:tcBorders")
        for lado in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), "dashed"); e.set(qn("w:sz"), "6"); e.set(qn("w:color"), "7F7F7F")
            b.append(e)
        tcpr.append(b)
        tr = t.rows[0]._tr
        trpr = tr.get_or_add_trPr()
        h = OxmlElement("w:trHeight"); h.set(qn("w:val"), str(int(alto_cm * 567))); h.set(qn("w:hRule"), "atLeast")
        trpr.append(h)
        par = celda.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._runs(par, "[[" + texto + "]]", size=9)
        self.n_fig += 1
        cap = self.doc.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._runs(cap, f"Fig. {self.n_fig}. {pie}", size=9)
        if ancho_pagina:
            self.ancho_fin()
        return self.n_fig

    def tabla(self, titulo, filas, anchos_cm, ancho_pagina=False, size=8, alinear=None):
        if ancho_pagina:
            self.ancho_inicio()
        self.n_tab += 1
        cap = self.doc.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.keep_with_next = True
        self._runs(cap, f"Tabla {self.n_tab}. {titulo}", size=9)
        t = self.doc.add_table(rows=len(filas), cols=len(filas[0]))
        t.alignment = 1
        t.autofit = False
        tblpr = t._tbl.tblPr
        bd = OxmlElement("w:tblBorders")
        for lado, v in (("top", "single"), ("bottom", "single")):
            e = OxmlElement(f"w:{lado}"); e.set(qn("w:val"), v); e.set(qn("w:sz"), "8"); e.set(qn("w:color"), "000000")
            bd.append(e)
        tblpr.append(bd)
        mar = OxmlElement("w:tblCellMar")
        for lado, w in (("top", 20), ("bottom", 20), ("left", 50), ("right", 50)):
            e = OxmlElement(f"w:{lado}"); e.set(qn("w:w"), str(w)); e.set(qn("w:type"), "dxa"); mar.append(e)
        tblpr.append(mar)
        for i, fila in enumerate(filas):
            for j, texto in enumerate(fila):
                c = t.cell(i, j)
                c.width = Cm(anchos_cm[j])
                par = c.paragraphs[0]
                par.paragraph_format.space_after = Pt(0)
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT if not alinear else alinear[j]
                self._runs(par, texto, size=size, bold=(i == 0))
                if i == 0:
                    tcpr = c._tc.get_or_add_tcPr()
                    b = OxmlElement("w:tcBorders")
                    e = OxmlElement("w:bottom"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:color"), "000000")
                    b.append(e); tcpr.append(b)
        sp = self.doc.add_paragraph(style="Normal")
        sp.paragraph_format.space_after = Pt(2)
        if ancho_pagina:
            self.ancho_fin()
        return self.n_tab

    # ------------------------------------------------------------ referencias
    def referencias(self, lista):
        self.h1("Referencias")
        for ref in lista:
            par = self.doc.add_paragraph(style="References")
            ppr = par._p.get_or_add_pPr()
            num = OxmlElement("w:numPr")
            il = OxmlElement("w:ilvl"); il.set(qn("w:val"), "0")
            ni = OxmlElement("w:numId"); ni.set(qn("w:val"), "4")
            num.append(il); num.append(ni)
            ppr.append(num)
            self._runs(par, ref, size=8)

    def guardar(self, ruta):
        try:
            self.doc.save(ruta)
        except PermissionError:          # archivo abierto en Word: no tocarlo, guardar al lado
            alt = ruta.replace(".docx", "_v2.docx")
            self.doc.save(alt)
            print("Archivo abierto en Word; guardado como", alt)



