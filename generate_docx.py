"""
Generate Word document matching the iApp AI API PDF style 100%.
PDF Style:
- Title page: large title + subtitle + date
- Each method: method_name code + description
- Info table: หมวดหมู่ / Endpoint / Authentication / ค่าใช้จ่าย / สถานะการทดสอบ
- Parameter table: 5 columns
- Return description
- Example code block (gray background)
- Response block (gray background)
- Error table (red header)
- Notes/Callout box
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ─── Color Palette (matching PDF) ───
C_PRIMARY   = RGBColor(0x1a, 0x3a, 0x5c)   # Dark navy
C_PRIMARY_L = RGBColor(0x2a, 0x50, 0x80)   # Medium navy
C_ACCENT    = RGBColor(0x0e, 0xa5, 0xe9)   # Sky blue
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY_50   = RGBColor(0xF8, 0xFA, 0xFC)
C_GRAY_100  = RGBColor(0xF1, 0xF5, 0xF9)
C_GRAY_200  = RGBColor(0xE2, 0xE8, 0xF0)
C_GRAY_600  = RGBColor(0x47, 0x55, 0x69)
C_GRAY_700  = RGBColor(0x33, 0x41, 0x55)
C_GRAY_900  = RGBColor(0x0F, 0x17, 0x2A)
C_GREEN     = RGBColor(0x16, 0xA3, 0x4A)
C_GREEN_BG  = RGBColor(0xF0, 0xFD, 0xF4)
C_YELLOW    = RGBColor(0xB4, 0x53, 0x09)
C_YELLOW_BG = RGBColor(0xFF, 0xFB, 0xEB)
C_RED       = RGBColor(0xDC, 0x26, 0x26)
C_RED_BG    = RGBColor(0xFE, 0xF2, 0xF2)
C_RED_DARK  = RGBColor(0x7F, 0x1D, 0x1D)
C_BLUE_BG   = RGBColor(0xEF, 0xF6, 0xFF)
C_CODE_BG   = RGBColor(0x0F, 0x17, 0x2A)
C_CODE_TEXT = RGBColor(0xE2, 0xE8, 0xF0)
C_VIOLET    = RGBColor(0x7C, 0x3A, 0xED)
C_CODE_STR  = RGBColor(0xC3, 0xE8, 0x8D)
C_CODE_KW   = RGBColor(0xC7, 0x92, 0xEA)
C_CODE_FN   = RGBColor(0x82, 0xAA, 0xFF)
C_TABLE_HDR = RGBColor(0x1E, 0x3A, 0x5F)  # param table header

def rgb_hex(color: RGBColor) -> str:
    """Convert RGBColor to 6-digit hex string."""
    return f'{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}'

def set_cell_bg(cell, rgb: RGBColor):
    """Set cell background color."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), rgb_hex(rgb))
    tcPr.append(shd)

def set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if val:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'), val.get('val', 'single'))
            el.set(qn('w:sz'), str(val.get('sz', 4)))
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), val.get('color', '000000'))
            tcBorders.append(el)
    tcPr.append(tcBorders)

def remove_table_borders(table):
    """Remove all borders from a table."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'none')
        el.set(qn('w:sz'), '0')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), 'auto')
        tblBorders.append(el)
    tblPr.append(tblBorders)

def set_table_border(table, color='E2E8F0'):
    """Set all inner borders of a table."""
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        tblBorders.append(el)
    tblPr.append(tblBorders)

def add_run_with_style(para, text, bold=False, italic=False, color=None, font_name='Sarabun', font_size=10, mono=False):
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    if mono:
        run.font.name = 'Courier New'
    else:
        run.font.name = font_name
    run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = color
    return run

def set_para_spacing(para, before=0, after=0, line_spacing=None):
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(before))
    spacing.set(qn('w:after'), str(after))
    if line_spacing:
        spacing.set(qn('w:line'), str(line_spacing))
        spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)

def set_para_indent(para, left=0):
    pPr = para._p.get_or_add_pPr()
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), str(left))
    pPr.append(ind)

# ─── Document Setup ───
doc = Document()

# Page margins
sections = doc.sections
for section in sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# Default font
doc.styles['Normal'].font.name = 'Sarabun'
doc.styles['Normal'].font.size = Pt(10)

# ──────────────────────────────────────────────────────
# TITLE PAGE
# ──────────────────────────────────────────────────────

# Header bar (navy table)
title_table = doc.add_table(rows=1, cols=1)
remove_table_borders(title_table)
title_table.rows[0].height = Cm(3.5)
tc = title_table.rows[0].cells[0]
set_cell_bg(tc, C_PRIMARY)
p = tc.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
set_para_spacing(p, before=60, after=60)
run = p.add_run('iApp AI API — คู่มือสำหรับนักพัฒนา')
run.font.name = 'Sarabun'
run.font.size = Pt(22)
run.font.bold = True
run.font.color.rgb = C_WHITE
p2 = tc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
run2 = p2.add_run('Face & eKYC Domain · 19 Methods · หมวด C-1 ถึง C-6')
run2.font.name = 'Sarabun'
run2.font.size = Pt(11)
run2.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)  # light blue

# Bottom border of title
tc2 = tc._tc
tcPr = tc2.get_or_add_tcPr()
tcBorders = OxmlElement('w:tcBorders')
bot = OxmlElement('w:bottom')
bot.set(qn('w:val'), 'single')
bot.set(qn('w:sz'), '12')
bot.set(qn('w:color'), '0EA5E9')
tcBorders.append(bot)
tcPr.append(tcBorders)

meta_para = doc.add_paragraph()
set_para_spacing(meta_para, before=60, after=80)
meta_run = meta_para.add_run('iApp Technology Co., Ltd.  ·  16 มิถุนายน 2569  ·  SDK: iapp-ai')
meta_run.font.name = 'Sarabun'
meta_run.font.size = Pt(9)
meta_run.font.color.rgb = C_GRAY_600
meta_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

doc.add_paragraph()

# ──────────────────────────────────────────────────────
# INTRO SECTION (General API structure)
# ──────────────────────────────────────────────────────
intro_heading = doc.add_paragraph()
set_para_spacing(intro_heading, before=40, after=80)
rh = intro_heading.add_run('การเริ่มต้นใช้งาน')
rh.font.name = 'Sarabun'
rh.font.size = Pt(14)
rh.font.bold = True
rh.font.color.rgb = C_PRIMARY

# Draw a thick left border by using a shaded paragraph
intro_body = doc.add_paragraph()
set_para_spacing(intro_body, before=0, after=100)
rb = intro_body.add_run('เอกสารนี้อธิบายวิธีเรียกใช้งาน iApp AI API แต่ละ method พร้อม parameter ที่ต้องส่ง ตัวอย่างโค้ด และ response ที่จะได้รับ')
rb.font.name = 'Sarabun'
rb.font.size = Pt(10)
rb.font.color.rgb = C_GRAY_700

# Base info table
base_rows = [
    ('Base URL',           'https://api.iapp.co.th'),
    ('Authentication',     'ส่ง API Key ผ่าน HTTP header: apikey: <YOUR_API_KEY>'),
    ('รูปแบบ request',     'POST (ยกเว้นที่ระบุไว้เป็นอย่างอื่น)'),
    ('รูปแบบ response',    'JSON ทุก endpoint'),
    ('หน่วยเครดิต',        'IC (iApp Credit) — หักต่อการเรียกแต่ละครั้งตามที่ระบุในแต่ละ method'),
]
base_table = doc.add_table(rows=len(base_rows), cols=2)
set_table_border(base_table, 'E2E8F0')
base_table.columns[0].width = Cm(5)
base_table.columns[1].width = Cm(11.5)

for i, (label, value) in enumerate(base_rows):
    row = base_table.rows[i]
    lc = row.cells[0]
    vc = row.cells[1]
    set_cell_bg(lc, C_GRAY_100)
    p = lc.paragraphs[0]
    set_para_spacing(p, before=40, after=40)
    add_run_with_style(p, label, bold=True, color=C_PRIMARY, font_size=9.5)
    p2 = vc.paragraphs[0]
    set_para_spacing(p2, before=40, after=40)
    add_run_with_style(p2, value, font_size=9.5, color=C_GRAY_700, mono=(i==0 or i==1))

doc.add_paragraph()

# Installation boxes
install_heading = doc.add_paragraph()
set_para_spacing(install_heading, before=60, after=40)
ih = install_heading.add_run('วิธีติดตั้ง Python SDK')
ih.font.name = 'Sarabun'
ih.font.size = Pt(10)
ih.font.bold = True
ih.font.color.rgb = C_GRAY_700

install_table = doc.add_table(rows=1, cols=2)
remove_table_borders(install_table)
for idx, (label, code) in enumerate([
    ('วิธีติดตั้ง', 'pip install iapp-ai'),
    ('ตัวอย่างการ authenticate', 'from iapp_ai import api\nclient = api("YOUR_API_KEY")')
]):
    cell = install_table.rows[0].cells[idx]
    set_cell_bg(cell, C_CODE_BG)
    lp = cell.paragraphs[0]
    set_para_spacing(lp, before=40, after=20)
    add_run_with_style(lp, label, font_size=8, color=C_GRAY_600)
    cp = cell.add_paragraph()
    set_para_spacing(cp, before=0, after=40)
    add_run_with_style(cp, code, font_size=9, color=C_ACCENT, mono=True)

    # Left border accent
    tc_xml = cell._tc
    tcPr = tc_xml.get_or_add_tcPr()
    tcBd = OxmlElement('w:tcBorders')
    l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '12'); l.set(qn('w:color'), '0EA5E9')
    tcBd.append(l); tcPr.append(tcBd)

doc.add_paragraph()

# Note about Live-verified
note_p = doc.add_paragraph()
set_para_spacing(note_p, before=40, after=120)
add_run_with_style(note_p, 'หมายเหตุ: ', bold=True, font_size=9, color=C_PRIMARY)
add_run_with_style(note_p, 'สถานะ ✅ Live-verified หมายความว่า iApp ได้ทดสอบ endpoint จริงและได้รับ HTTP 200 แล้ว', font_size=9, color=C_GRAY_600)

# ──────────────────────────────────────────────────────
# QUICK REFERENCE TABLE
# ──────────────────────────────────────────────────────
qr_heading = doc.add_paragraph()
set_para_spacing(qr_heading, before=80, after=80)
qh = qr_heading.add_run('ตารางสรุป 19 เมธอด (Quick Reference)')
qh.font.name = 'Sarabun'
qh.font.size = Pt(14)
qh.font.bold = True
qh.font.color.rgb = C_PRIMARY

methods_summary = [
    (1,  'face_liveness',                  'ตรวจว่าใบหน้าเป็นคนจริงหรือ Spoof',               'POST /v3/store/ekyc/face-passive-liveness'),
    (2,  'info_face_liveness',             'ดึงผล Liveness แบบ Async ด้วย taskGuid',          'GET /v3/store/ekyc/face-passive-liveness/{id}'),
    (3,  'face_verification',              'เปรียบเทียบใบหน้า 2 ภาพ (1:1 v1)',               'POST /v3/store/ekyc/face-verification'),
    (4,  'face_ver2',                      'เปรียบเทียบใบหน้า 2 ภาพ (1:1 v2)',               'POST /v3/store/ekyc/face-verification'),
    (5,  'face_detect_single',             'ตรวจจับใบหน้าเดี่ยว + Bounding Box',             'POST /v3/store/ekyc/face-detection/single'),
    (6,  'face_detect_multi',              'ตรวจจับใบหน้าหลายคนในภาพเดียว',                 'POST /v3/store/ekyc/face-detection/multi'),
    (7,  'face_recog_add',                 'ลงทะเบียนใบหน้าเข้าฐานข้อมูล',                   'POST /v3/store/ekyc/face-recognition/add'),
    (8,  'face_recog_remove',              'ลบข้อมูลใบหน้าจากฐานข้อมูล',                     'POST /v3/store/ekyc/face-recognition/remove'),
    (9,  'face_recog_check',               'ตรวจสอบจำนวนใบหน้าในฐานข้อมูล',                 'POST /v3/store/ekyc/face-recognition/check'),
    (10, 'face_recog_export',              'ส่งออก Feature Vectors เป็น CSV',                'POST /v3/store/ekyc/face-recognition/export'),
    (11, 'face_recog_import',              'นำเข้าใบหน้าจำนวนมากผ่าน CSV',                   'POST /v3/store/ekyc/face-recognition/import'),
    (12, 'face_recog_single',              'ค้นหาระบุตัวตนใบหน้าเดี่ยว (1:N)',               'POST /v3/store/ekyc/face-recognition/single'),
    (13, 'face_recog_multi',               'ค้นหาระบุตัวตนใบหน้ากลุ่ม',                      'POST /v3/store/ekyc/face-recognition/multi'),
    (14, 'face_recog_facecrop',            'ครอบและค้นหาใบหน้าจากฐานข้อมูล',                'POST /v3/store/ekyc/face-recognition/facecrop'),
    (15, 'face_ver_config_score',          'ตั้ง Threshold สำหรับ face_verification',         'POST /face_config_score'),
    (16, 'face_detect_config_score',       'ตั้ง Threshold สำหรับ face_detect',               'POST /face_config_score'),
    (17, 'face_recog_config_score',        'ตั้ง Threshold สำหรับ face_recog',                'POST /face_config_score'),
    (18, 'img_bg_removal_file',            'ลบพื้นหลังภาพ (Background Removal)',             'POST /v3/store/smart-city/remove-background'),
    (19, 'face_id_card_verification',  'เปรียบเทียบ Selfie vs บัตรประชาชน',              'POST /v3/store/ekyc/face-and-id-card-verification'),
]

qr_table = doc.add_table(rows=1 + len(methods_summary), cols=4)
set_table_border(qr_table, 'E2E8F0')
qr_table.columns[0].width = Cm(1.0)
qr_table.columns[1].width = Cm(5.5)
qr_table.columns[2].width = Cm(6.0)
qr_table.columns[3].width = Cm(6.0)

# Header row
hdr_row = qr_table.rows[0]
for cidx, (label, w) in enumerate([('#', Cm(1.0)), ('Method Name', Cm(5.5)), ('คำอธิบาย', Cm(6.0)), ('Endpoint', Cm(6.0))]):
    cell = hdr_row.cells[cidx]
    set_cell_bg(cell, C_PRIMARY)
    p = cell.paragraphs[0]
    set_para_spacing(p, before=60, after=60)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run_with_style(p, label, bold=True, color=C_WHITE, font_size=9)

# Data rows
for i, (num, method, desc, endpoint) in enumerate(methods_summary):
    row = qr_table.rows[i + 1]
    bg = C_GRAY_50 if i % 2 == 1 else C_WHITE
    # num
    nc = row.cells[0]
    set_cell_bg(nc, bg)
    np = nc.paragraphs[0]
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(np, before=40, after=40)
    add_run_with_style(np, str(num), bold=True, color=C_PRIMARY, font_size=9)
    # method
    mc = row.cells[1]
    set_cell_bg(mc, bg)
    mp = mc.paragraphs[0]
    set_para_spacing(mp, before=40, after=40)
    add_run_with_style(mp, method, color=C_PRIMARY_L, font_size=9, mono=True)
    # desc
    dc = row.cells[2]
    set_cell_bg(dc, bg)
    dp = dc.paragraphs[0]
    set_para_spacing(dp, before=40, after=40)
    add_run_with_style(dp, desc, font_size=9, color=C_GRAY_700)
    # endpoint
    ec = row.cells[3]
    set_cell_bg(ec, bg)
    ep = ec.paragraphs[0]
    set_para_spacing(ep, before=40, after=40)
    add_run_with_style(ep, endpoint, font_size=8.5, color=C_GRAY_600, mono=True)

doc.add_paragraph()

# ──────────────────────────────────────────────────────
# HELPER FUNCTIONS for each method section
# ──────────────────────────────────────────────────────

def add_section_divider(doc):
    """Add a horizontal rule (thin paragraph)."""
    p = doc.add_paragraph()
    set_para_spacing(p, before=60, after=60)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:color'), 'E2E8F0')
    pBdr.append(bottom)
    pPr.append(pBdr)

def add_method_header(doc, num, name, description):
    """Method header: dark navy box with number + name + description."""
    tbl = doc.add_table(rows=1, cols=2)
    remove_table_borders(tbl)
    tbl.rows[0].height = Cm(1.5)

    # Number cell
    num_cell = tbl.rows[0].cells[0]
    set_cell_bg(num_cell, C_PRIMARY)
    num_cell.width = Cm(1.5)
    np = num_cell.paragraphs[0]
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_spacing(np, before=60, after=0)
    add_run_with_style(np, str(num), bold=True, color=C_WHITE, font_size=14)

    # Name + desc cell
    name_cell = tbl.rows[0].cells[1]
    set_cell_bg(name_cell, C_PRIMARY_L)
    np2 = name_cell.paragraphs[0]
    set_para_spacing(np2, before=40, after=20)
    add_run_with_style(np2, name, bold=True, color=RGBColor(0x38, 0xBD, 0xF8), font_size=13, mono=True)
    desc_p = name_cell.add_paragraph()
    set_para_spacing(desc_p, before=0, after=40)
    add_run_with_style(desc_p, description, color=RGBColor(0xCC, 0xCC, 0xCC), font_size=9.5)

def add_info_table(doc, rows_data):
    """Meta info table: 2 columns, left=label, right=value."""
    tbl = doc.add_table(rows=len(rows_data), cols=2)
    set_table_border(tbl, 'E2E8F0')
    tbl.columns[0].width = Cm(4.5)
    tbl.columns[1].width = Cm(12.0)
    for i, (label, value, is_ok) in enumerate(rows_data):
        lc = tbl.rows[i].cells[0]
        vc = tbl.rows[i].cells[1]
        set_cell_bg(lc, C_GRAY_100)
        lp = lc.paragraphs[0]
        set_para_spacing(lp, before=40, after=40)
        add_run_with_style(lp, label, bold=True, color=C_GRAY_700, font_size=9.5)
        vp = vc.paragraphs[0]
        set_para_spacing(vp, before=40, after=40)
        if is_ok == 'ok':
            add_run_with_style(vp, '✅ ', font_size=9.5, color=C_GREEN)
            add_run_with_style(vp, value, font_size=9.5, color=C_GREEN, bold=True)
        elif is_ok == 'warn':
            add_run_with_style(vp, '⚠️ ', font_size=9.5, color=C_YELLOW)
            add_run_with_style(vp, value, font_size=9.5, color=C_YELLOW, bold=True)
        elif is_ok == 'code':
            add_run_with_style(vp, value, font_size=9.5, color=C_PRIMARY_L, mono=True)
        else:
            add_run_with_style(vp, value, font_size=9.5, color=C_GRAY_700)

def add_sub_label(doc, text):
    """Section sub-label like 'พารามิเตอร์'"""
    p = doc.add_paragraph()
    set_para_spacing(p, before=100, after=40)
    r = p.add_run(text.upper())
    r.font.name = 'Sarabun'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = C_GRAY_600

def add_param_table(doc, params):
    """5-column parameter table."""
    headers = ['พารามิเตอร์', 'ชนิดข้อมูล', 'จำเป็น', 'ค่าเริ่มต้น', 'คำอธิบาย']
    col_widths = [Cm(3.5), Cm(2.5), Cm(2.0), Cm(2.5), Cm(6.0)]
    tbl = doc.add_table(rows=1 + len(params), cols=5)
    set_table_border(tbl, 'E2E8F0')
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = w

    # Header
    hrow = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hrow.cells[i]
        set_cell_bg(cell, C_TABLE_HDR)
        p = cell.paragraphs[0]
        set_para_spacing(p, before=50, after=50)
        add_run_with_style(p, h, bold=True, color=C_WHITE, font_size=9)

    # Data
    for ri, (pname, ptype, req, default, desc) in enumerate(params):
        row = tbl.rows[ri + 1]
        bg = C_GRAY_50 if ri % 2 == 1 else C_WHITE
        for ci in range(5):
            set_cell_bg(row.cells[ci], bg)
            p = row.cells[ci].paragraphs[0]
            set_para_spacing(p, before=40, after=40)

        # param name
        add_run_with_style(row.cells[0].paragraphs[0], pname, color=C_PRIMARY_L, font_size=9, mono=True)
        # type
        add_run_with_style(row.cells[1].paragraphs[0], ptype, color=C_VIOLET, font_size=9, mono=True)
        # required
        req_p = row.cells[2].paragraphs[0]
        req_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if req == 'ใช่':
            add_run_with_style(req_p, 'จำเป็น', bold=True, color=C_RED, font_size=8.5)
        else:
            add_run_with_style(req_p, 'ไม่จำเป็น', color=C_GRAY_600, font_size=8.5)
        # default
        def_p = row.cells[3].paragraphs[0]
        def_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run_with_style(def_p, default, color=C_GRAY_600, font_size=9, mono=True)
        # desc
        add_run_with_style(row.cells[4].paragraphs[0], desc, font_size=9, color=C_GRAY_700)

def add_code_block(doc, code_text):
    """Dark background code block (matching PDF style)."""
    tbl = doc.add_table(rows=1, cols=1)
    remove_table_borders(tbl)
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, C_CODE_BG)

    # Left accent border
    tc_xml = cell._tc
    tcPr = tc_xml.get_or_add_tcPr()
    tcBd = OxmlElement('w:tcBorders')
    l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '16'); l.set(qn('w:color'), '0EA5E9')
    tcBd.append(l); tcPr.append(tcBd)

    p = cell.paragraphs[0]
    set_para_spacing(p, before=60, after=60)
    for line in code_text.split('\n'):
        if p.runs:
            p.add_run('\n')
        add_run_with_style(p, line, font_size=9, color=C_CODE_TEXT, mono=True)

def add_json_block(doc, json_text):
    """Green-bordered JSON response block."""
    tbl = doc.add_table(rows=1, cols=1)
    remove_table_borders(tbl)
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, RGBColor(0x0D, 0x11, 0x17))

    tc_xml = cell._tc
    tcPr = tc_xml.get_or_add_tcPr()
    tcBd = OxmlElement('w:tcBorders')
    l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '16'); l.set(qn('w:color'), '16A34A')
    tcBd.append(l); tcPr.append(tcBd)

    p = cell.paragraphs[0]
    set_para_spacing(p, before=60, after=60)
    for line in json_text.split('\n'):
        if p.runs:
            p.add_run('\n')
        add_run_with_style(p, line, font_size=9, color=C_CODE_STR, mono=True)

def add_return_desc(doc, text):
    """Green background return description."""
    tbl = doc.add_table(rows=1, cols=1)
    remove_table_borders(tbl)
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, C_GREEN_BG)

    tc_xml = cell._tc
    tcPr = tc_xml.get_or_add_tcPr()
    tcBd = OxmlElement('w:tcBorders')
    l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '16'); l.set(qn('w:color'), '16A34A')
    tcBd.append(l); tcPr.append(tcBd)

    p = cell.paragraphs[0]
    set_para_spacing(p, before=60, after=60)
    add_run_with_style(p, text, font_size=9.5, color=RGBColor(0x16, 0x65, 0x34))

def add_error_table(doc, errors):
    """Error table: dark red header."""
    headers = ['HTTP Status', 'ความหมาย', 'วิธีแก้ไข']
    col_widths = [Cm(2.5), Cm(6.0), Cm(8.0)]
    tbl = doc.add_table(rows=1 + len(errors), cols=3)
    set_table_border(tbl, 'E2E8F0')
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = w

    hrow = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hrow.cells[i]
        set_cell_bg(cell, C_RED_DARK)
        p = cell.paragraphs[0]
        set_para_spacing(p, before=50, after=50)
        add_run_with_style(p, h, bold=True, color=C_WHITE, font_size=9)

    for ri, (code, meaning, fix) in enumerate(errors):
        row = tbl.rows[ri + 1]
        bg = RGBColor(0xFF, 0xF5, 0xF5) if ri % 2 == 1 else C_WHITE
        for ci in range(3):
            set_cell_bg(row.cells[ci], bg)
            p = row.cells[ci].paragraphs[0]
            set_para_spacing(p, before=40, after=40)
        sc = row.cells[0].paragraphs[0]
        sc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run_with_style(sc, code, bold=True, color=C_RED, font_size=9, mono=True)
        add_run_with_style(row.cells[1].paragraphs[0], meaning, font_size=9, color=C_GRAY_700)
        add_run_with_style(row.cells[2].paragraphs[0], fix, font_size=9, color=C_GRAY_700)

def add_callout(doc, style, title, text):
    """Note/Warning/Important callout box."""
    if style == 'note':
        bg, border, tc, titc = C_BLUE_BG, '0EA5E9', C_PRIMARY_L, RGBColor(0x1D, 0x4E, 0xD8)
        icon = '💡'
    elif style == 'warning':
        bg, border, tc, titc = C_YELLOW_BG, 'F59E0B', C_YELLOW, C_YELLOW
        icon = '⚠️'
    else:  # important
        bg, border, tc, titc = C_RED_BG, 'DC2626', C_RED, C_RED
        icon = '⛔'

    tbl = doc.add_table(rows=1, cols=1)
    remove_table_borders(tbl)
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, bg)

    tc_xml = cell._tc
    tcPr = tc_xml.get_or_add_tcPr()
    tcBd = OxmlElement('w:tcBorders')
    l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '16'); l.set(qn('w:color'), border)
    tcBd.append(l); tcPr.append(tcBd)

    title_p = cell.paragraphs[0]
    set_para_spacing(title_p, before=60, after=20)
    add_run_with_style(title_p, f'{icon} {title}', bold=True, color=titc, font_size=9.5)

    body_p = cell.add_paragraph()
    set_para_spacing(body_p, before=0, after=60)
    add_run_with_style(body_p, text, font_size=9.5, color=tc)

def add_spacer(doc, lines=1):
    for _ in range(lines):
        p = doc.add_paragraph()
        set_para_spacing(p, before=0, after=0)

# ──────────────────────────────────────────────────────
# API REFERENCE HEADING
# ──────────────────────────────────────────────────────
api_ref_heading = doc.add_paragraph()
set_para_spacing(api_ref_heading, before=120, after=80)
arh = api_ref_heading.add_run('API Reference')
arh.font.name = 'Sarabun'
arh.font.size = Pt(16)
arh.font.bold = True
arh.font.color.rgb = C_PRIMARY

# ──────────────────────────────────────────────────────
# METHOD 1: face_liveness
# ──────────────────────────────────────────────────────
add_method_header(doc, 1, 'face_liveness',
    'ตรวจสอบว่ารูปภาพใบหน้าเป็นบุคคลจริง (Real) หรือภาพลอกเลียนแบบ (Spoof) เหมาะสำหรับขั้นตอน eKYC Passive Liveness')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                              None),
    ('Endpoint',         'POST /v3/store/ekyc/face-passive-liveness',         'code'),
    ('Authentication',   'apikey: <YOUR_API_KEY>',                             'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการเรียก 1 ครั้ง',                          None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                      'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธของไฟล์รูปภาพใบหน้า (JPG/PNG ≤ 10 MB)'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์ form-data เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติมที่ต้องการอัปโหลด'),
])
add_sub_label(doc, 'ค่าที่ได้รับกลับ')
add_return_desc(doc, 'JSON ประกอบด้วย: filename, predict (REAL/SPOOF), score, darkness, data, normalized, taskGuid (สำหรับ Async polling)')
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''from iapp_ai import api
import iapp_ai.module_api as module_api

client = api("YOUR_API_KEY")
resp = client.face_liveness("img/selfie.jpg")
print(resp.json()["predict"])   # REAL หรือ SPOOF
print("taskGuid:", module_api.taskGuid)''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "filename": "selfie.jpg",
  "predict": "SPOOF",
  "score": 0.611,
  "darkness": 0,
  "data": { "SPOOF": 0.720, "REAL": 0.280 },
  "normalized": { "SPOOF": 0.611, "REAL": 0.389 },
  "taskGuid": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
}''')
add_sub_label(doc, 'รหัสข้อผิดพลาด')
add_error_table(doc, [
    ('400/422', 'รูปแบบหรือขนาดไฟล์ไม่ถูกต้อง',  'ใช้รูป JPG/PNG ขนาดไม่ต่ำกว่า 200×200 px'),
    ('402',     'เครดิตไม่เพียงพอ',               'เติม IC ในระบบก่อนเรียกใช้งาน'),
])
add_callout(doc, 'note', 'หมายเหตุ (C-1)',
    'ในรุ่นก่อนมีบั๊กที่เก็บ HTTP Response ทั้งก้อนไว้ใน taskGuid ปัจจุบันแก้ไขแล้ว — ดึงเฉพาะค่า String ของ ID เพื่อนำไป Polling ต่อใน info_face_liveness ได้อย่างถูกต้อง')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 2: info_face_liveness
# ──────────────────────────────────────────────────────
add_method_header(doc, 2, 'info_face_liveness',
    'ดึงผลการตรวจสอบ Liveness แบบ Asynchronous โดยใช้ taskGuid ที่ได้จาก face_liveness')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                                          None),
    ('Endpoint',         'GET /v3/store/ekyc/face-passive-liveness/{taskGuid}',            'code'),
    ('Authentication',   'apikey: <YOUR_API_KEY>',                                          'code'),
    ('ค่าใช้จ่าย',       'ฟรี (ไม่หักเครดิต)',                                             None),
    ('สถานะการทดสอบ',   'ต้องใช้ taskGuid จริงจาก face_liveness',                          'warn'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('taskGuid', 'str',          'ใช่',  '""',   'รหัสภารกิจที่ได้จาก face_liveness'),
    ('headers',  'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('url',      'List[Any]',    'ไม่', 'None', 'Legacy parameter (ไม่ใช้งานแล้ว)'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''# สอง-ขั้นตอน: ส่งรูปก่อน แล้ว poll ผลลัพธ์
resp1 = client.face_liveness("img/selfie.jpg")
task_id = module_api.taskGuid

resp2 = client.info_face_liveness(taskGuid=task_id)
print(resp2.json())''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc, '{ "status": "completed", "result": { "predict": "REAL", "score": 0.985 } }')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 3: face_verification
# ──────────────────────────────────────────────────────
add_method_header(doc, 3, 'face_verification',
    'เปรียบเทียบรูปใบหน้า 2 ภาพแบบ 1:1 พร้อมกำหนด company namespace และ min_score')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                     None),
    ('Endpoint',         'POST /v3/store/ekyc/face-verification',    'code'),
    ('Authentication',   'apikey: <YOUR_API_KEY>',                    'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการเรียก 1 ครั้ง',                 None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',             'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path1',    'str',          'ใช่',  '—',    'พาธรูปใบหน้าที่ 1'),
    ('file_path2',    'str',          'ใช่',  '—',    'พาธรูปใบหน้าที่ 2'),
    ('company_name',  'str',          'ใช่',  '—',    'ชื่อ company/namespace ของบริษัท'),
    ('min_score',     'float',        'ใช่',  '—',    'คะแนนขั้นต่ำสำหรับยืนยันตัวตน (0–100)'),
    ('headers',       'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',  'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์ form-data เพิ่มเติม'),
    ('files',         'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_verification(
    "img/id_photo.jpg", "img/selfie.jpg",
    company_name="my_company", min_score=80.0
)
print(resp.json()["matched"])   # True / False''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "duration": 0.171,
  "matched": false,
  "message": "file2: face size is too small.",
  "score": 0.0,
  "threshold": 80,
  "api_status_code": "E424",
  "status_code": 200
}''')
add_sub_label(doc, 'รหัสข้อผิดพลาด')
add_error_table(doc, [
    ('400/422', 'ขนาดใบหน้าเล็กเกินไป',           'ใช้รูปที่ใบหน้าชัดเจน ≥ 200×200 px'),
    ('402',     'เครดิตไม่เพียงพอ',               'เติม IC ในระบบ'),
])
add_callout(doc, 'important', 'การแก้ไขในแผน C-3',
    'ฟังก์ชันนี้เปิดไฟล์พร้อมกัน 2 รูป ในรุ่นก่อนมีปัญหา File Handle รั่วไหล ปัจจุบันใช้ Context Manager ปิดไฟล์อัตโนมัติแล้ว')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 4: face_ver2
# ──────────────────────────────────────────────────────
add_method_header(doc, 4, 'face_ver2',
    'เปรียบเทียบรูปใบหน้า 2 ภาพแบบ v2 ไม่ต้องระบุ company_name และ min_score')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                     None),
    ('Endpoint',         'POST /v3/store/ekyc/face-verification',    'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการเรียก 1 ครั้ง',                 None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',             'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path1',   'str',          'ใช่',  '—',    'พาธรูปใบหน้าที่ 1'),
    ('file_path2',   'str',          'ใช่',  '—',    'พาธรูปใบหน้าที่ 2'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม เช่น threshold'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_ver2("img/face1.jpg", "img/face2.jpg")\nprint(resp.json())')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 5: face_detect_single
# ──────────────────────────────────────────────────────
add_method_header(doc, 5, 'face_detect_single',
    'ตรวจจับใบหน้าเดี่ยวในรูปภาพ คืนค่า Bounding Box และ Detection Score พร้อม crop ใบหน้า')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                         None),
    ('Endpoint',         'POST /v3/store/ekyc/face-detection/single',    'code'),
    ('ค่าใช้จ่าย',       '0.2 IC ต่อการเรียก 1 ครั้ง',                   None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                 'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธรูปภาพที่ต้องการตรวจจับ'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'ข้อมูล payload เสริม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_detect_single("img/photo.jpg")\nprint("Confidence:", resp.json()["detection_score"])')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "bbox": {
    "xmin": 822.67, "ymin": 187.18,
    "xmax": 1185.97, "ymax": 682.44
  },
  "detection_score": 0.9999,
  "face": "data:image/png;base64,..."
}''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 6: face_detect_multi
# ──────────────────────────────────────────────────────
add_method_header(doc, 6, 'face_detect_multi',
    'ตรวจจับและระบุพิกัด Bounding Box ของทุกใบหน้าในรูปภาพเดียว')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                        None),
    ('Endpoint',         'POST /v3/store/ekyc/face-detection/multi',    'code'),
    ('ค่าใช้จ่าย',       '0.5 IC ต่อการเรียก 1 ครั้ง',                  None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธรูปภาพกลุ่มที่ต้องการตรวจ'),
    ('company_name', 'str',          'ใช่',  '—',    'Company namespace'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์ form-data เสริม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_detect_multi("img/group.jpg", company_name="my_company")\nprint("Faces found:", len(resp.json()["result"]))')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "message": "successfully performed",
  "process_time": 0.757,
  "result": [
    { "bbox": {"xmax": 1185, "xmin": 822, "ymax": 682, "ymin": 187}, "detection_score": 0.999 }
  ]
}''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 7: face_recog_add
# ──────────────────────────────────────────────────────
add_method_header(doc, 7, 'face_recog_add',
    'ลงทะเบียนใบหน้าใหม่เข้าฐานข้อมูล Face Recognition ของบริษัท')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                          None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/add',     'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการลงทะเบียน 1 ภาพ',                   None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                  'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธรูปใบหน้าบุคคลใหม่'),
    ('company_name', 'str',          'ใช่',  '—',    'Company namespace ที่จัดเก็บ'),
    ('name',         'str',          'ใช่',  '—',    'ชื่อบุคคลเจ้าของใบหน้า'),
    ('password',     'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'ข้อมูล form-data เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_add(
    "img/john.jpg", company_name="my_company",
    name="john_doe", password="secure_pass"
)
print(resp.json()["message"])''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc, '{ "company": "my_company", "face_id": "260616-1", "message": "successfully added" }')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 8: face_recog_remove
# ──────────────────────────────────────────────────────
add_method_header(doc, 8, 'face_recog_remove', 'ลบข้อมูลใบหน้าของบุคคลออกจากฐานข้อมูล Face Recognition')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                             None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/remove',      'code'),
    ('ค่าใช้จ่าย',       '0.1 IC ต่อการเรียก 1 ครั้ง',                       None),
    ('สถานะการทดสอบ',   'ต้องใช้ face_id จริงจากฐานข้อมูล',                  'warn'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('company_name',     'str',          'ใช่',  '—',    'Company namespace'),
    ('name',             'str',          'ใช่',  '—',    'ชื่อบุคคลที่ต้องการลบ'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('date',             'str',          'ใช่',  '—',    'วันที่ลงทะเบียนครั้งแรก (YYYY-MM-DD)'),
    ('face_id',          'str',          'ใช่',  '—',    'Face ID จากระบบ (เช่น "260616-1")'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_remove(
    "my_company", "john_doe", "secure_pass",
    date="2026-06-16", face_id="260616-1"
)
print(resp.json()["message"])''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc, '{ "message": "successfully removed" }')
add_sub_label(doc, 'รหัสข้อผิดพลาด')
add_error_table(doc, [('421', 'face_id ไม่ถูกต้อง', 'ตรวจสอบ face_id จาก face_recog_check ก่อน')])
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 9: face_recog_check
# ──────────────────────────────────────────────────────
add_method_header(doc, 9, 'face_recog_check', 'ตรวจสอบสถิติจำนวนและรายชื่อใบหน้าทั้งหมดในฐานข้อมูลบริษัท')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                             None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/check',       'code'),
    ('ค่าใช้จ่าย',       '0.2 IC ต่อการตรวจ',                                None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                     'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('company_name',     'str',          'ใช่',  '—',    'Company namespace'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านสำหรับตรวจสอบสิทธิ์'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_recog_check("my_company", "secure_pass")\nprint("Total features:", resp.json()["feature_count"])')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "company": "my_company",
  "feature_count": 12,
  "message": "successfully performed",
  "name": { "john_doe": 1, "jane_smith": 2 },
  "name_count": 2
}''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 10: face_recog_export
# ──────────────────────────────────────────────────────
add_method_header(doc, 10, 'face_recog_export', 'ส่งออก Feature Vectors ของทุกใบหน้าในฐานข้อมูลเป็น CSV สำหรับสำรองข้อมูล')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                              None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/export',       'code'),
    ('ค่าใช้จ่าย',       '2 IC ต่อการส่งออก',                                 None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                      'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('company_name',     'str',          'ใช่',  '—',    'ชื่อโดเมนบริษัท'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านเข้าถึง'),
    ('type_file',        'str',          'ใช่',  '—',    'รูปแบบไฟล์ส่งออก (แนะนำ "csv")'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_export("my_company", "secure_pass", "csv")
csv_data = resp.text
print(csv_data[:200])   # CSV content''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc, 'company,name,face_id,feature\nmy_company,john_doe,260616-1,0.051097 -0.02256 0.07414 ...')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 11: face_recog_import
# ──────────────────────────────────────────────────────
add_method_header(doc, 11, 'face_recog_import', 'นำเข้าข้อมูลใบหน้าจำนวนมากพร้อมกันผ่านไฟล์ CSV')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                              None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/import',       'code'),
    ('ค่าใช้จ่าย',       '5 IC ต่อการนำเข้า',                                 None),
    ('สถานะการทดสอบ',   'ต้องใช้ CSV ที่มีรูปแบบถูกต้อง',                     'warn'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธของไฟล์ CSV ที่ต้องการนำเข้า'),
    ('company_name', 'str',          'ใช่',  '—',    'ชื่อโดเมนบริษัท'),
    ('password',     'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_import(
    file_path="exports/backup.csv",
    company_name="my_company",
    password="secure_pass"
)
print("Import Status:", resp.json().get("message"))''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 12: face_recog_single
# ──────────────────────────────────────────────────────
add_method_header(doc, 12, 'face_recog_single',
    'ค้นหาและระบุตัวตนใบหน้าเดี่ยว (1:N) เปรียบเทียบกับทุกคนในฐานข้อมูลบริษัท')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                              None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/single',       'code'),
    ('ค่าใช้จ่าย',       '1.5 IC ต่อการค้นหา',                                None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                      'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'รูปภาพเป้าหมายที่ต้องการค้นหา'),
    ('company_name', 'str',          'ใช่',  '—',    'Company namespace ที่ใช้ค้นหา'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'ข้อมูลเพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_single("img/who_is_this.jpg", "my_company")
result = resp.json()
if result.get("name") != "unknown":
    print(f"Identified: {result[\'name\']} (Score: {result[\'recognition_score\']})")''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc,
'''{
  "bbox": { "xmax": 1185.97, "xmin": 822.67, "ymax": 682.44, "ymin": 187.18 },
  "company": "my_company",
  "detection_score": 0.9999,
  "message": "successfully performed",
  "name": "john_doe",
  "recognition_score": 0.9567
}''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 13: face_recog_multi
# ──────────────────────────────────────────────────────
add_method_header(doc, 13, 'face_recog_multi',
    'ระบุตัวตนของทุกใบหน้าในภาพพร้อมกัน (Many:N) เปรียบเทียบกับฐานข้อมูล')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                             None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/multi',       'code'),
    ('ค่าใช้จ่าย',       '2 IC ต่อการค้นหา',                                 None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                     'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'รูปภาพกลุ่มที่ต้องการค้นหา'),
    ('company_name', 'str',          'ใช่',  '—',    'Company namespace'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.face_recog_multi("img/staff_meeting.jpg", "my_company")
for person in resp.json().get("result", []):
    print(f"Name: {person.get(\'name\')}, BBox: {person.get(\'bbox\')}")''')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 14: face_recog_facecrop
# ──────────────────────────────────────────────────────
add_method_header(doc, 14, 'face_recog_facecrop',
    'ครอบภาพใบหน้าและค้นหาระบุตัวตนจากฐานข้อมูลในขั้นตอนเดียว')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                               None),
    ('Endpoint',         'POST /v3/store/ekyc/face-recognition/facecrop',      'code'),
    ('ค่าใช้จ่าย',       '1.5 IC ต่อการเรียก',                                  None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                       'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'รูปภาพเป้าหมาย'),
    ('company_name', 'str',          'ใช่',  '—',    'Company namespace'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'ข้อมูลเพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_recog_facecrop("img/snapshot.jpg", "my_company")\nprint("Result:", resp.json())')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 15: face_ver_config_score
# ──────────────────────────────────────────────────────
add_method_header(doc, 15, 'face_ver_config_score',
    'ตั้งค่าเกณฑ์คะแนน (Threshold) สำหรับ face_verification ของ Company')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC (Score Config)',                 None),
    ('Endpoint',         'POST /face_config_score',             'code'),
    ('ค่าใช้จ่าย',       'ฟรี',                                 None),
    ('สถานะการทดสอบ',   'ต้องใช้ credentials บริษัทที่ถูกต้อง','warn'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('detect_value',     'float',        'ใช่',  '—',    'เกณฑ์ตรวจจับใบหน้า (0.0–1.0)'),
    ('compare_value',    'float',        'ใช่',  '—',    'เกณฑ์เปรียบเทียบใบหน้า (0.0–1.0)'),
    ('company_name',     'str',          'ใช่',  '—',    'Company namespace'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_ver_config_score(0.5, 0.7, "my_company", "secure_pass")')
add_callout(doc, 'note', 'หมายเหตุ (C-2)',
    'ทั้ง 3 เมธอด Config Score (face_ver_*, face_detect_*, face_recog_*) ถูก refactor ให้เรียกผ่าน private helper _face_config_score จุดเดียว ลดโค้ดซ้ำซ้อนและลดโอกาสผิดพลาดในการอัปเกรด URL ในอนาคต')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 16: face_detect_config_score
# ──────────────────────────────────────────────────────
add_method_header(doc, 16, 'face_detect_config_score',
    'ตั้งค่าเกณฑ์คะแนนสำหรับ face_detect ของ Company')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC (Score Config)',   None),
    ('Endpoint',         'POST /face_config_score','code'),
    ('ค่าใช้จ่าย',       'ฟรี',                   None),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('detect_value',     'float',        'ใช่',  '—',    'เกณฑ์ตรวจจับใบหน้า (0.0–1.0)'),
    ('company_name',     'str',          'ใช่',  '—',    'Company namespace'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_detect_config_score(0.6, "my_company", "secure_pass")')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 17: face_recog_config_score
# ──────────────────────────────────────────────────────
add_method_header(doc, 17, 'face_recog_config_score',
    'ตั้งค่าเกณฑ์คะแนนสำหรับ face_recognition (detect + recog) ของ Company')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC (Score Config)',   None),
    ('Endpoint',         'POST /face_config_score','code'),
    ('ค่าใช้จ่าย',       'ฟรี',                   None),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('detect_value',     'float',        'ใช่',  '—',    'เกณฑ์ตรวจจับ (0.0–1.0)'),
    ('recog_value',      'float',        'ใช่',  '—',    'เกณฑ์จำแนกตัวตน (0.0–1.0)'),
    ('company_name',     'str',          'ใช่',  '—',    'Company namespace'),
    ('company_password', 'str',          'ใช่',  '—',    'รหัสผ่านประจำฐานข้อมูล'),
    ('headers',          'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload',     'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์เพิ่มเติม'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc, 'resp = client.face_recog_config_score(0.5, 0.75, "my_company", "secure_pass")')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 18: img_bg_removal_file
# ──────────────────────────────────────────────────────
add_method_header(doc, 18, 'img_bg_removal_file',
    'ลบพื้นหลังรูปภาพ (Background Removal) บันทึกผลลัพธ์ลงไฟล์ตามที่กำหนด')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'Smart City / Image Processing',                       None),
    ('Endpoint',         'POST /v3/store/smart-city/remove-background',          'code'),
    ('Authentication',   'apikey: <YOUR_API_KEY>',                               'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการเรียก 1 ครั้ง',                             None),
    ('สถานะการทดสอบ',   'ทดสอบแล้ว (16 มิถุนายน 2569)',                        'ok'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('file_path',    'str',          'ใช่',  '—',    'พาธของรูปภาพต้นฉบับ'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์ form-data เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
    ('output_path',  'str',          'ไม่', 'None', 'พาธที่ต้องการบันทึกไฟล์ผลลัพธ์'),
])
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''resp = client.img_bg_removal_file(
    "img/avatar.jpg",
    output_path="img/avatar_no_bg.png"
)
print(f"บันทึกแล้ว ({len(resp.content)} bytes)")''')
add_callout(doc, 'note', 'หมายเหตุ (C-4)',
    'รุ่นก่อนบันทึกไฟล์ Hardcoded ที่ "media/img_bg_removal_file.jpg" เสมอ ปัจจุบันใช้ output_path แบบยืดหยุ่น ตามระบบ build_output_path (แผนงาน C-4)')
add_section_divider(doc)

# ──────────────────────────────────────────────────────
# METHOD 19: face_id_card_verification
# ──────────────────────────────────────────────────────
add_method_header(doc, 19, 'face_id_card_verification',
    'เปรียบเทียบรูป selfie กับรูปหน้าบนบัตรประชาชน เพื่อยืนยันว่าเป็นบุคคลเดียวกัน เหมาะสำหรับขั้นตอน eKYC')
add_spacer(doc)
add_info_table(doc, [
    ('หมวดหมู่',         'eKYC',                                                              None),
    ('Endpoint',         'POST /v3/store/ekyc/face-and-id-card-verification',                 'code'),
    ('Authentication',   'apikey: <YOUR_API_KEY>',                                             'code'),
    ('ค่าใช้จ่าย',       '1 IC ต่อการเรียก 1 ครั้ง',                                          None),
    ('สถานะการทดสอบ',   'ยังไม่ได้ทดสอบกับข้อมูลจริง (ต้องใช้รูปบัตรและ selfie จริง)',        'warn'),
])
add_sub_label(doc, 'พารามิเตอร์')
add_param_table(doc, [
    ('id_card_path', 'str',          'ใช่',  '—',    'path ของไฟล์รูปบัตรประชาชน (JPG/PNG ขนาดอย่างน้อย 600×400 px ไม่เกิน 10 MB)'),
    ('selfie_path',  'str',          'ใช่',  '—',    'path ของไฟล์รูป selfie (เงื่อนไขเดียวกับรูปบัตร)'),
    ('headers',      'Dict[str,str]','ไม่', 'None', 'HTTP headers เพิ่มเติม'),
    ('data_payload', 'Dict[str,Any]','ไม่', 'None', 'พารามิเตอร์ form-data เพิ่มเติม'),
    ('files',        'List[Any]',    'ไม่', 'None', 'ไฟล์เพิ่มเติม'),
])
add_sub_label(doc, 'ค่าที่ได้รับกลับ')
add_return_desc(doc, 'JSON ประกอบด้วยค่า confidence ของแต่ละรูปและค่ารวม รวมถึงผล isSamePerson (true/false)')
add_sub_label(doc, 'ตัวอย่างการใช้งาน')
add_code_block(doc,
'''# ⚠️ ต้องสลับอาร์กิวเมนต์ — ดูข้อควรทราบด้านล่าง
resp = client.face_id_card_verification(
    id_card_path="img/selfie.jpg",   # ส่ง selfie เป็น file0
    selfie_path="img/idcard.jpg"     # ส่ง ID card เป็น file1
)
print(resp.json()["isSamePerson"])''')
add_sub_label(doc, 'ตัวอย่าง response (HTTP 200)')
add_json_block(doc, '{\n  "isSamePerson": true,\n  "confidence": 0.982345\n}')
add_sub_label(doc, 'รหัสข้อผิดพลาด')
add_error_table(doc, [
    ('400/422', 'รูปขนาดเล็กเกินไปหรือรูปแบบไฟล์ไม่รองรับ', 'ใช้รูป JPG หรือ PNG ขนาดอย่างน้อย 600×400 px'),
    ('402',     'เครดิตไม่เพียงพอ',                           'เติม IC ในระบบก่อนเรียกใช้งาน'),
])
add_callout(doc, 'warning', 'ข้อควรทราบ — Parameter Swap Bug',
    'Backend คาดหวัง file0 = selfie และ file1 = ID card แต่ parameter ชื่อ id_card_path ถูก map ไปที่ file0 — ดังนั้นจำเป็นต้องสลับอาร์กิวเมนต์ตามตัวอย่างด้านบน คือส่ง selfie เข้า id_card_path และส่ง ID card เข้า selfie_path')

# ──────────────────────────────────────────────────────
# GLOBAL ERROR TABLE
# ──────────────────────────────────────────────────────
add_spacer(doc)
global_err_heading = doc.add_paragraph()
set_para_spacing(global_err_heading, before=120, after=80)
geh = global_err_heading.add_run('รหัสข้อผิดพลาดทั่วไป')
geh.font.name = 'Sarabun'
geh.font.size = Pt(14)
geh.font.bold = True
geh.font.color.rgb = C_PRIMARY

add_error_table(doc, [
    ('400',     'ส่งข้อมูลผิดรูปแบบ',                         'ตรวจสอบชนิดและชื่อ field ให้ถูกต้อง'),
    ('401',     'API Key ไม่ถูกต้องหรือไม่ได้ส่งมา',         'ตรวจสอบ API Key อีกครั้ง'),
    ('402',     'เครดิตไม่เพียงพอ',                           'เติม IC ในระบบก่อนเรียกใช้งาน'),
    ('421',     'Company name หรือ password ไม่ถูกต้อง',      'ตรวจสอบ credentials ของ Company'),
    ('422',     'ข้อมูลไม่ผ่านการตรวจสอบ (Validation Error)', 'ตรวจสอบว่าส่ง field ที่จำเป็นครบแล้ว'),
    ('424',     'ขนาดใบหน้าเล็กเกินไปในขั้นตอนประมวลผล',    'ใช้รูปที่ใบหน้าชัดเจน ไม่ถูกบดบัง'),
    ('500',     'ข้อผิดพลาดภายในของ Server',                  'รอแล้วลองใหม่ หรือตรวจสอบรูปแบบ/ขนาดไฟล์'),
])

# Footer paragraph
add_spacer(doc, 2)
footer_p = doc.add_paragraph()
set_para_spacing(footer_p, before=60, after=0)
add_run_with_style(footer_p, 'iApp AI API — คู่มือสำหรับนักพัฒนา (Face & eKYC)  ·  C-1 ถึง C-6  ·  iApp Technology Co., Ltd.  ·  16 มิถุนายน 2569',
    font_size=8, color=C_GRAY_600)
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ──────────────────────────────────────────────────────
# SAVE
# ──────────────────────────────────────────────────────
out_path = r"C:\Users\minii\OneDrive\เดสก์ท็อป\iapp\c1_c6_methods_manual.docx"
doc.save(out_path)
print(f"Done! Saved to: {out_path}")
