"""
Mall Management System — Tkinter GUI
Requires: pip install mysql-connector-python
Run:      python mall_gui.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys

# ─────────────────────────────────────────────
#  THEME COLOURS  — vibrant & colourful
# ─────────────────────────────────────────────
BG        = "#0f0f1a"   # deep midnight background
SIDEBAR   = "#12122a"   # sidebar — darker navy
CARD      = "#1a1a35"   # card bg
CARD2     = "#1e1e42"   # slightly lighter card
ACCENT    = "#00d4ff"   # vivid cyan
ACCENT2   = "#bf5fff"   # vivid purple
ACCENT3   = "#ff6b9d"   # vivid pink
SUCCESS   = "#00e676"   # vivid green
WARNING   = "#ffd740"   # vivid amber
DANGER    = "#ff5252"   # vivid red
ORANGE    = "#ff9100"   # vivid orange
TEAL      = "#1de9b6"   # vivid teal
TEXT      = "#e8eaf6"   # bright white-blue
SUBTEXT   = "#9e9ec8"   # muted lavender
WHITE     = "#ffffff"
ENTRY_BG  = "#252550"
BTN_BG    = "#00d4ff"
BTN_FG    = "#0f0f1a"
BTN_HOV   = "#66e8ff"
HDR_BG    = "#252550"
ROW_ALT   = "#151530"
ROW_SEL   = "#2a2a6a"
# stat card colours
STAT_COLS = ["#00d4ff","#bf5fff","#00e676","#ffd740","#ff6b9d","#ff9100"]
FONT      = ("Segoe UI", 10)
FONT_B    = ("Segoe UI", 10, "bold")
FONT_H    = ("Segoe UI", 13, "bold")
FONT_T    = ("Segoe UI", 16, "bold")
FONT_MONO = ("Consolas", 10)

# ─────────────────────────────────────────────
#  DB CONNECTION
# ─────────────────────────────────────────────
conn = None

def get_connection(host, user, password, database):
    return mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

def install_triggers(c):
    cur = c.cursor()
    trigger_names = [
        "trg_check_salary_before_insert",
        "trg_check_salary_before_update",
        "trg_compute_final_amount",
        "trg_log_interaction_on_bill"
    ]
    for d in trigger_names:
        try:
            cur.execute(f"DROP TRIGGER IF EXISTS {d}")
        except Error:
            pass

    triggers = [
        """CREATE TRIGGER trg_check_salary_before_insert
        BEFORE INSERT ON EMPLOYEE FOR EACH ROW
        BEGIN IF NEW.Salary<=0 THEN SET NEW.Salary=15000; END IF; END""",
        """CREATE TRIGGER trg_check_salary_before_update
        BEFORE UPDATE ON EMPLOYEE FOR EACH ROW
        BEGIN IF NEW.Salary<=0 THEN SET NEW.Salary=15000; END IF; END""",
        """CREATE TRIGGER trg_compute_final_amount
        BEFORE INSERT ON BILL FOR EACH ROW
        BEGIN
        IF NEW.Discount IS NULL THEN SET NEW.Discount=0; END IF;
        SET NEW.Final_Amount=GREATEST(NEW.Total_Amount - (NEW.Total_Amount * NEW.Discount / 100), 0);
        END""",
        """CREATE TRIGGER trg_log_interaction_on_bill
        AFTER INSERT ON BILL FOR EACH ROW
        BEGIN
        DECLARE v INT;
        SELECT Employee_ID INTO v FROM EMPLOYEE WHERE SSN=NEW.SSN LIMIT 1;
        IF v IS NOT NULL THEN
        INSERT IGNORE INTO EMPLOYEE_CUSTOMER(Employee_ID,Customer_ID,Interaction_Date)
        VALUES(v,NEW.Customer_ID,NEW.Bill_Date);
        END IF;
        END""",
    ]
    for t in triggers:
        cur.execute(t)
    c.commit()
    cur.close()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def style_button(b, color=BTN_BG, fg=BTN_FG, hover=BTN_HOV):
    b.config(bg=color, fg=fg, relief="flat", cursor="hand2",
             font=FONT_B, padx=12, pady=6, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=color))

def make_entry(parent, width=28):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 font=FONT, relief="flat", width=width, bd=4)
    return e

def make_label(parent, text, bold=False, color=TEXT, size=10):
    f = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
    return tk.Label(parent, text=text, bg=CARD2, fg=color, font=f)

def lf(parent, text, color=ACCENT):
    f = tk.LabelFrame(parent, text=text, bg=CARD2, fg=color,
                      font=FONT_B, bd=1, relief="groove", padx=10, pady=8)
    return f

def scrollable_frame(parent):
    canvas = tk.Canvas(parent, bg=CARD, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=CARD)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return inner

# ─────────────────────────────────────────────
#  CUSTOM STYLED DROPDOWN
# ─────────────────────────────────────────────
class StyledDropdown(tk.Frame):
    def __init__(self, parent, values=None, width=28,
                 bg=ENTRY_BG, fg=TEXT, accent=ACCENT,
                 placeholder="— select —", **kw):
        super().__init__(parent, bg=bg, **kw)
        self._values      = list(values or [])
        self._placeholder = placeholder
        self._accent      = accent
        self._var         = tk.StringVar(value=placeholder)
        self._popup       = None
        self._callback    = None
        self._width       = width
        self._btn = tk.Button(
            self, textvariable=self._var, anchor="w",
            bg=bg, fg=SUBTEXT,
            activebackground=ENTRY_BG, activeforeground=TEXT,
            font=FONT, relief="flat", bd=0,
            width=width, padx=8, pady=5,
            cursor="hand2", command=self._toggle
        )
        self._btn.pack(side="left", fill="x", expand=True)
        self._arrow = tk.Label(
            self, text="▾", bg=bg, fg=accent,
            font=("Segoe UI", 11), cursor="hand2", padx=4
        )
        self._arrow.pack(side="right")
        self._arrow.bind("<Button-1>", lambda e: self._toggle())
        self.config(highlightthickness=1,
                    highlightbackground=HDR_BG,
                    highlightcolor=accent)
        self.bind("<Enter>",  lambda e: self.config(highlightbackground=accent))
        self.bind("<Leave>",  lambda e: self.config(highlightbackground=HDR_BG))

    def get(self):
        v = self._var.get()
        return "" if v == self._placeholder else v

    def set(self, value):
        if value:
            self._var.set(value)
            self._btn.config(fg=TEXT)
        else:
            self._var.set(self._placeholder)
            self._btn.config(fg=SUBTEXT)

    def set_values(self, values):
        self._values = list(values)

    def bind_select(self, callback):
        self._callback = callback

    def _toggle(self):
        if self._popup and self._popup.winfo_exists():
            self._close()
        else:
            self._open()

    def _open(self):
        if not self._values:
            return
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        w = max(self.winfo_width(), 220)
        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.configure(bg=self._accent)
        popup.attributes("-topmost", True)
        self._popup = popup
        inner = tk.Frame(popup, bg=CARD, padx=1, pady=1)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        max_vis = min(9, len(self._values))
        lb = tk.Listbox(
            inner,
            bg=CARD, fg=TEXT,
            selectbackground=ROW_SEL, selectforeground=WHITE,
            font=FONT, relief="flat", bd=0,
            activestyle="none", height=max_vis,
            highlightthickness=0, exportselection=False,
        )
        vsb = ColorScrollbar(inner, orient="vertical",
                             command=lb.yview,
                             track=CARD, thumb=self._accent,
                             thumb_hover=BTN_HOV, width=6)
        lb.configure(yscrollcommand=vsb.set)
        for item in self._values:
            lb.insert("end", "  " + item)
        cur = self.get()
        for i, v in enumerate(self._values):
            if v == cur:
                lb.selection_set(i); lb.see(i); break
        vsb.pack(side="right", fill="y")
        lb.pack(side="left", fill="both", expand=True)
        lb.bind("<Motion>",          lambda e: (lb.selection_clear(0,"end"),
                                                 lb.selection_set(lb.nearest(e.y))))
        lb.bind("<ButtonRelease-1>", lambda e: self._select(lb))
        lb.bind("<Return>",          lambda e: self._select(lb))
        lb.bind("<Escape>",          lambda e: self._close())
        popup.bind("<FocusOut>",     lambda e: self.after(120, self._close_if_gone))
        lb.focus_set()
        popup.update_idletasks()
        h = lb.winfo_reqheight() + 4
        popup.wm_geometry(f"{w}x{h}+{x}+{y}")

    def _select(self, lb):
        sel = lb.curselection()
        if not sel: return
        value = self._values[sel[0]]
        self._var.set(value)
        self._btn.config(fg=TEXT)
        self._close()
        self.event_generate("<<DropdownSelected>>")
        if self._callback:
            self._callback()

    def _close(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None

    def _close_if_gone(self):
        try:
            if self._popup and self._popup.winfo_exists():
                if not self._popup.focus_get():
                    self._close()
        except Exception:
            self._close()

# ─────────────────────────────────────────────
#  TREEVIEW TABLE
# ─────────────────────────────────────────────
NUMERIC_COLS = {
    "Bills","Units","Units Sold","Qty",
    "Price","Total","Discount","Final","Final Amount","Revenue",
    "Total Spent","Avg Bill","Salary","Fee","Mins","Items Sold",
    "Revenue Handled","Bills Processed","Line Total","Duration",
    "Total_Amount","Final_Amount","Quantity","Price (Rs)",
    "Floor",
}
ID_COLS = {
    "Bill ID","ID","Item ID","Shop ID","Mall ID",
    "Slot ID","Employee ID","Customer ID","Parking ID",
}

class ColorScrollbar(tk.Canvas):
    def __init__(self, parent, orient="vertical", command=None,
                 track=CARD, thumb=ACCENT, thumb_hover=BTN_HOV, **kw):
        self._orient   = orient
        self._command  = command
        self._track    = track
        self._thumb    = thumb
        self._thumb_hov= thumb_hover
        self._pos      = (0.0, 1.0)
        self._dragging = False
        self._drag_start = 0
        if orient == "vertical":
            kw.setdefault("width",  8)
            kw.setdefault("cursor", "arrow")
        else:
            kw.setdefault("height", 8)
            kw.setdefault("cursor", "arrow")
        super().__init__(parent, bg=track, highlightthickness=0,
                         relief="flat", **kw)
        self.bind("<Configure>",       self._draw)
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<B1-Motion>",       self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda e: self._draw(hover=True))
        self.bind("<Leave>", lambda e: self._draw(hover=False))

    def set(self, first, last):
        self._pos = (float(first), float(last))
        self._draw()

    def _thumb_coords(self):
        W, H = self.winfo_width(), self.winfo_height()
        f, l = self._pos
        if self._orient == "vertical":
            y0 = max(2, int(f * H))
            y1 = min(H - 2, int(l * H))
            y1 = max(y1, y0 + 20)
            return 2, y0, W - 2, y1
        else:
            x0 = max(2, int(f * W))
            x1 = min(W - 2, int(l * W))
            x1 = max(x1, x0 + 20)
            return x0, 2, x1, H - 2

    def _draw(self, event=None, hover=False):
        self.delete("all")
        self.config(bg=self._track)
        color = self._thumb_hov if hover else self._thumb
        coords = self._thumb_coords()
        self.create_rectangle(*coords, fill=color, outline="", width=0)

    def _on_press(self, event):
        self._dragging = True
        self._drag_start = event.y if self._orient == "vertical" else event.x

    def _on_drag(self, event):
        if not self._dragging or not self._command: return
        W, H = self.winfo_width(), self.winfo_height()
        size = H if self._orient == "vertical" else W
        pos  = event.y if self._orient == "vertical" else event.x
        delta = (pos - self._drag_start) / size
        self._drag_start = pos
        f, l = self._pos
        span = l - f
        new_f = max(0.0, min(1.0 - span, f + delta))
        self._command("moveto", new_f)

    def _on_release(self, event):
        self._dragging = False

def make_tree(parent, columns, height=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Mall.Treeview",
                    background=CARD, foreground=TEXT, fieldbackground=CARD,
                    rowheight=28, font=FONT, borderwidth=0)
    style.configure("Mall.Treeview.Heading",
                    background=HDR_BG, foreground=ACCENT, font=FONT_B,
                    relief="flat", padding=(8, 6))
    style.map("Mall.Treeview",
              background=[("selected", ROW_SEL)],
              foreground=[("selected", WHITE)])
    frame = tk.Frame(parent, bg=BG)
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Mall.Treeview", height=height)
    vsb = ColorScrollbar(frame, orient="vertical",
                         command=tree.yview,
                         track=BG, thumb=ACCENT2, thumb_hover=ACCENT)
    hsb = ColorScrollbar(frame, orient="horizontal",
                         command=tree.xview,
                         track=BG, thumb=ACCENT2, thumb_hover=ACCENT,
                         height=8)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    for col in columns:
        is_num = col in NUMERIC_COLS
        is_id  = col in ID_COLS
        if is_id:
            w      = max(70, len(col) * 9)
            anchor = "w"
        elif is_num:
            w      = max(85, len(col) * 10)
            anchor = "e"
        else:
            w      = max(120, len(col) * 12)
            anchor = "w"
        tree.heading(col, text=col, anchor=anchor)
        tree.column(col, width=w, anchor=anchor, minwidth=55, stretch=True)
    tree.tag_configure("odd",  background=CARD)
    tree.tag_configure("even", background=ROW_ALT)
    vsb.pack(side="right", fill="y", pady=2)
    hsb.pack(side="bottom", fill="x", padx=2)
    tree.pack(fill="both", expand=True)
    frame.pack(fill="both", expand=True, padx=4, pady=4)
    return tree

def load_tree(tree, rows):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end",
                    values=[str(v) if v is not None else "" for v in row],
                    tags=(tag,))

def fetch(sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    hdrs = [d[0] for d in cur.description]
    cur.close()
    return hdrs, rows

def execute(sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    cur.close()

def fetchone(sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    r = cur.fetchone()
    cur.close()
    return r

# ═══════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ═══════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mall Management System — Connect")
        self.geometry("440x520")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build()

    def _build(self):
        banner = tk.Frame(self, bg="#1a0a3a")
        banner.pack(fill="x")
        tk.Label(banner, text="🏬", bg="#1a0a3a", fg=ACCENT2,
                 font=("Segoe UI", 28)).pack(pady=(14,2))
        tk.Label(banner, text="Mall Management System",
                 bg="#1a0a3a", fg=WHITE,
                 font=("Segoe UI", 13, "bold")).pack()
        tk.Label(banner, text="Connect to your database to begin",
                 bg="#1a0a3a", fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(pady=(2,12))
        tk.Frame(self, bg=ACCENT2, height=2).pack(fill="x")
        card = tk.Frame(self, bg=CARD2, padx=28, pady=16)
        card.pack(padx=30, pady=14, fill="x")
        fields = [("Host",     "localhost"),
                  ("User",     "root"),
                  ("Password", ""),
                  ("Database", "MALL_MANAGEMENT_SYSTEM")]
        self.entries = {}
        for label, default in fields:
            row = tk.Frame(card, bg=CARD2)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD2, fg=SUBTEXT,
                     font=FONT_B, width=10, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=ACCENT,
                         font=FONT, relief="flat", width=22, bd=4,
                         highlightthickness=1,
                         highlightbackground=HDR_BG,
                         highlightcolor=ACCENT)
            e.insert(0, default)
            if label == "Password":
                e.config(show="*")
            e.pack(side="left", fill="x", expand=True)
            self.entries[label] = e
        self.status = tk.Label(self, text="", bg=BG, fg=DANGER, font=FONT)
        self.status.pack(pady=(6, 2))
        btn = tk.Button(self, text="  Connect  →",
                        command=self._connect,
                        bg=ACCENT2, fg=WHITE, font=FONT_B,
                        relief="flat", padx=24, pady=10,
                        cursor="hand2", bd=0)
        btn.pack(pady=8)
        btn.bind("<Enter>", lambda e: btn.config(bg="#d580ff"))
        btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT2))

    def _connect(self):
        global conn
        host = self.entries["Host"].get().strip()
        user = self.entries["User"].get().strip()
        pwd  = self.entries["Password"].get()
        db   = self.entries["Database"].get().strip()
        try:
            conn = get_connection(host, user, pwd, db)
            install_triggers(conn)
            self.destroy()
            app = MainApp()
            app.mainloop()
        except Error as e:
            self.status.config(text=str(e))

# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mall Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._build()
        self._show("dashboard")

    def _build(self):
        # ── Sidebar ──────────────────────────────
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        hdr = tk.Frame(self.sidebar, bg="#1a0a3a", pady=0)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏬", bg="#1a0a3a", fg=ACCENT2,
                 font=("Segoe UI", 22)).pack(pady=(18,2))
        tk.Label(hdr, text="Mall MS",
                 bg="#1a0a3a", fg=WHITE, font=("Segoe UI", 13, "bold")).pack()
        tk.Label(hdr, text="Management System",
                 bg="#1a0a3a", fg=SUBTEXT, font=("Segoe UI", 8)).pack(pady=(0,14))
        tk.Frame(self.sidebar, bg=ACCENT2, height=2).pack(fill="x")
        self.nav_btns = {}
        pages = [
            ("dashboard",  "📊", "Dashboard",      ACCENT),
            ("billing",    "🧾", "Place Order",    SUCCESS),
            ("view",       "🔍", "View & Search",  ACCENT2),
            ("analytics",  "📈", "Analytics",      WARNING),
            ("manage",     "⚙️",  "Manage Data",    ORANGE),
            ("parking_mgr","🅿", "Parking Manager",TEAL),     # ← NEW
            ("queries",    "💾", "SQL Queries",    ACCENT3),
        ]
        tk.Frame(self.sidebar, bg=SIDEBAR, height=8).pack()
        for key, icon, label, color in pages:
            b = tk.Button(self.sidebar,
                          text=f"  {icon}  {label}",
                          anchor="w",
                          command=lambda k=key: self._show(k),
                          bg=SIDEBAR, fg=TEXT, font=("Segoe UI", 10),
                          relief="flat", bd=0, padx=12, pady=11,
                          cursor="hand2",
                          activebackground=CARD2,
                          activeforeground=color)
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, b=b, c=color: b.config(bg=CARD2, fg=c))
            b.bind("<Leave>", lambda e, b=b, k=key: b.config(
                bg=CARD if self._active == k else SIDEBAR,
                fg=self._active_color if self._active == k else TEXT))
            self.nav_btns[key] = (b, color)
        self._active = "dashboard"
        self._active_color = ACCENT
        # ── Content area ─────────────────────────
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.frames = {}
        for key, _, _, _ in pages:
            f = tk.Frame(self.content, bg=BG)
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[key] = f
        self._build_dashboard(self.frames["dashboard"])
        self._build_billing(self.frames["billing"])
        self._build_view(self.frames["view"])
        self._build_analytics(self.frames["analytics"])
        self._build_manage(self.frames["manage"])
        self._build_parking_manager(self.frames["parking_mgr"])   # ← NEW
        self._build_queries(self.frames["queries"])

    def _show(self, key):
        self._active = key
        for k, (b, color) in self.nav_btns.items():
            if k == key:
                b.config(bg=CARD2, fg=color)
                self._active_color = color
            else:
                b.config(bg=SIDEBAR, fg=TEXT)
        self.frames[key].lift()
        if key == "dashboard":
            self._refresh_dashboard()
        elif key == "parking_mgr":
            self._pm_refresh_slots()

    def _page_header(self, parent, title, subtitle="", color=ACCENT):
        hdr = tk.Frame(parent, bg=BG, pady=10)
        hdr.pack(fill="x", padx=24)
        bar = tk.Frame(hdr, bg=color, width=4)
        bar.pack(side="left", fill="y", padx=(0,12))
        text_col = tk.Frame(hdr, bg=BG)
        text_col.pack(side="left")
        tk.Label(text_col, text=title, bg=BG, fg=TEXT,
                 font=FONT_T).pack(anchor="w")
        if subtitle:
            tk.Label(text_col, text=subtitle, bg=BG, fg=SUBTEXT,
                     font=FONT).pack(anchor="w")
        tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=24, pady=(4,12))

    # ═══════════════════════════════════
    #  DASHBOARD
    # ═══════════════════════════════════
    def _build_dashboard(self, parent):
        self._page_header(parent, "Dashboard", "Live summary from the database", ACCENT)
        self.dash_cards = tk.Frame(parent, bg=BG)
        self.dash_cards.pack(fill="x", padx=24, pady=4)
        self.dash_tree_frame = tk.Frame(parent, bg=BG)
        self.dash_tree_frame.pack(fill="both", expand=True, padx=24, pady=8)

    def _refresh_dashboard(self):
        for w in self.dash_cards.winfo_children():
            w.destroy()
        for w in self.dash_tree_frame.winfo_children():
            w.destroy()
        stats = [
            ("Shops",     "SELECT COUNT(*) FROM SHOP",           ACCENT,  "🏪"),
            ("Customers", "SELECT COUNT(*) FROM CUSTOMER",       ACCENT2, "👥"),
            ("Bills",     "SELECT COUNT(*) FROM BILL",           SUCCESS, "🧾"),
            ("Employees", "SELECT COUNT(*) FROM EMPLOYEE",       WARNING, "👔"),
            ("Items",     "SELECT COUNT(*) FROM ITEM",           ORANGE,  "📦"),
            ("Parking",   "SELECT COUNT(*) FROM PARKING_RECORD", TEAL,    "🅿️"),
        ]
        for label, sql, color, icon in stats:
            val = fetchone(sql)[0]
            card = tk.Frame(self.dash_cards, bg=CARD2, padx=20, pady=14,
                            relief="flat", bd=0, highlightthickness=2,
                            highlightbackground=color)
            card.pack(side="left", padx=6, pady=4)
            tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0,8))
            tk.Label(card, text=icon, bg=CARD2, fg=color,
                     font=("Segoe UI", 18)).pack()
            tk.Label(card, text=str(val), bg=CARD2, fg=color,
                     font=("Segoe UI", 24, "bold")).pack()
            tk.Label(card, text=label, bg=CARD2, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack()
        tk.Label(self.dash_tree_frame, text="Recent Bills",
                 bg=BG, fg=TEXT, font=FONT_H).pack(anchor="w", pady=(4,6))
        cols = ["Bill ID","Customer","Shop","Date","Final Amount"]
        tree = make_tree(self.dash_tree_frame, cols, height=12)
        _, rows = fetch("""
        SELECT B.Bill_ID, C.Name, S.Shop_Name, B.Bill_Date, B.Final_Amount
        FROM BILL B
        JOIN CUSTOMER C ON B.Customer_ID=C.Customer_ID
        JOIN SHOP S     ON B.Shop_ID=S.Shop_ID
        ORDER BY B.Bill_Date DESC, B.Bill_ID DESC LIMIT 20
        """)
        load_tree(tree, rows)

    # ═══════════════════════════════════
    #  BILLING — PLACE ORDER
    # ═══════════════════════════════════
    def _build_billing(self, parent):
        self._page_header(parent, "Place an Order", "Select customer, shop, items and generate a bill", SUCCESS)
        body = tk.Frame(parent, bg=BG)
        body.pack(fill="both", expand=True, padx=24)
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="y", padx=(0,16))
        f1 = lf(left, "1. Customer", ACCENT)
        f1.pack(fill="x", pady=4)
        self.bill_cust_var = tk.StringVar()
        self.bill_cust_cb = StyledDropdown(f1, width=30, accent=ACCENT)
        self.bill_cust_cb.pack(pady=4)
        tk.Button(f1, text="↻ Refresh", command=self._load_billing_customers,
                  bg=CARD2, fg=SUBTEXT, font=("Segoe UI",9), relief="flat",
                  cursor="hand2").pack()
        f2 = lf(left, "2. Shop", ACCENT2)
        f2.pack(fill="x", pady=4)
        self.bill_shop_var = tk.StringVar()
        self.bill_shop_cb = StyledDropdown(f2, width=30, accent=ACCENT2)
        self.bill_shop_cb.pack(pady=4)
        self.bill_shop_cb.bind_select(self._on_shop_select)
        f3 = lf(left, "3. Cashier (SSN)", TEAL)
        f3.pack(fill="x", pady=4)
        self.bill_cashier_var = tk.StringVar()
        self.bill_cashier_cb = StyledDropdown(f3, width=30, accent=TEAL)
        self.bill_cashier_cb.pack(pady=4)
        f4 = lf(left, "4. Discount (%)", WARNING)
        f4.pack(fill="x", pady=4)
        self.bill_disc_var = tk.StringVar(value="0")
        tk.Label(f4, text="Enter 0–100  (e.g. 10 = 10% off)",
                 bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w")
        make_entry(f4, 10).pack(pady=4)
        self.bill_disc_entry = f4.winfo_children()[-1]
        self.bill_disc_entry.config(textvariable=self.bill_disc_var)
        btn_bill = tk.Button(left, text="Generate Bill ✓",
                             command=self._generate_bill)
        style_button(btn_bill, color=SUCCESS, fg=BG, hover="#c3f0bf")
        btn_bill.pack(fill="x", pady=12)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Available Items", bg=BG, fg=TEXT,
                 font=FONT_H).pack(anchor="w", pady=(0,4))
        self.item_tree = make_tree(right,
                                   ["Item ID","Item Name","Category","Price"], height=8)
        self.item_tree.bind("<Double-1>", self._add_to_cart)
        tk.Label(right, text="Cart  (double-click item above to add)",
                 bg=BG, fg=SUBTEXT, font=FONT).pack(anchor="w", pady=(8,4))
        self.cart_tree = make_tree(right,
                                   ["Item ID","Name","Price","Qty","Line Total"], height=5)
        btn_row = tk.Frame(right, bg=BG)
        btn_row.pack(fill="x", pady=4)
        b_rem = tk.Button(btn_row, text="Remove Selected",
                          command=self._remove_from_cart)
        style_button(b_rem, color=DANGER, fg=BG, hover="#f5a9ba")
        b_rem.pack(side="left", padx=(0,8))
        b_clr = tk.Button(btn_row, text="Clear Cart",
                          command=self._clear_cart)
        style_button(b_clr, color=ENTRY_BG, fg=TEXT, hover=HDR_BG)
        b_clr.pack(side="left")
        self.cart_items = []
        self._load_billing_customers()
        self._load_billing_shops()

    def _load_billing_customers(self):
        _, rows = fetch("SELECT Customer_ID, Name FROM CUSTOMER ORDER BY Customer_ID")
        self.bill_cust_map = {f"{r[0]} — {r[1]}": r[0] for r in rows}
        self.bill_cust_cb.set_values(list(self.bill_cust_map.keys()))
        self.bill_cust_cb.set("")

    def _load_billing_shops(self):
        _, rows = fetch("SELECT Shop_ID, Shop_Name FROM SHOP ORDER BY Shop_ID")
        self.bill_shop_map = {f"{r[0]} — {r[1]}": r[0] for r in rows}
        self.bill_shop_cb.set_values(list(self.bill_shop_map.keys()))
        self.bill_shop_cb.set("")

    def _on_shop_select(self):
        key = self.bill_shop_cb.get()
        if not key: return
        shop_id = self.bill_shop_map[key]
        _, rows = fetch(
            "SELECT Item_ID, Item_Name, Category, Price FROM ITEM WHERE Shop_ID=%s",
            (shop_id,))
        load_tree(self.item_tree, rows)
        _, rows2 = fetch(
            "SELECT SSN, Employee_Name FROM EMPLOYEE WHERE Shop_ID=%s", (shop_id,))
        self.bill_cashier_map = {f"{r[0]} — {r[1]}": r[0] for r in rows2}
        self.bill_cashier_cb.set_values(list(self.bill_cashier_map.keys()))
        self.bill_cashier_cb.set("")

    def _add_to_cart(self, event=None):
        sel = self.item_tree.selection()
        if not sel: return
        vals = self.item_tree.item(sel[0], "values")
        item_id, name, cat, price = vals[0], vals[1], vals[2], float(vals[3])
        qty_win = tk.Toplevel(self)
        qty_win.title("Quantity")
        qty_win.geometry("260x120")
        qty_win.configure(bg=CARD)
        qty_win.grab_set()
        tk.Label(qty_win, text=f"Quantity for {name}:",
                 bg=CARD, fg=TEXT, font=FONT).pack(pady=12)
        qty_var = tk.StringVar(value="1")
        e = make_entry(qty_win, 8)
        e.config(textvariable=qty_var)
        e.pack()
        def confirm():
            try:
                q = int(qty_var.get())
                if q < 1: raise ValueError
            except ValueError:
                messagebox.showerror("Error","Enter a valid quantity >= 1", parent=qty_win)
                return
            found_idx = -1
            for idx, (c_id, c_name, c_price, c_qty) in enumerate(self.cart_items):
                if c_id == int(item_id):
                    found_idx = idx
                    break
            if found_idx != -1:
                old_qty = self.cart_items[found_idx][3]
                self.cart_items[found_idx] = (int(item_id), name, price, old_qty + q)
            else:
                self.cart_items.append((int(item_id), name, price, q))
            self._refresh_cart()
            qty_win.destroy()
        tk.Button(qty_win, text="Add to Cart", command=confirm,
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=4, cursor="hand2").pack(pady=8)

    def _remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel: return
        idx = self.cart_tree.index(sel[0])
        self.cart_items.pop(idx)
        self._refresh_cart()

    def _clear_cart(self):
        self.cart_items.clear()
        self._refresh_cart()

    def _refresh_cart(self):
        rows = [(iid, name, f"{price:.2f}", qty, f"{price*qty:.2f}")
                for iid, name, price, qty in self.cart_items]
        load_tree(self.cart_tree, rows)

    def _generate_bill(self):
        if not self.bill_cust_cb.get():
            messagebox.showerror("Error","Select a customer"); return
        if not self.bill_shop_cb.get():
            messagebox.showerror("Error","Select a shop"); return
        if not self.bill_cashier_cb.get():
            messagebox.showerror("Error","Select a cashier"); return
        if not self.cart_items:
            messagebox.showerror("Error","Cart is empty"); return
        try:
            disc_pct = float(self.bill_disc_var.get() or 0)
            if disc_pct < 0 or disc_pct > 100:
                messagebox.showerror("Error","Discount must be between 0 and 100"); return
        except ValueError:
            messagebox.showerror("Error","Invalid discount percentage"); return
        cust_id  = self.bill_cust_map[self.bill_cust_cb.get()]
        shop_id  = self.bill_shop_map[self.bill_shop_cb.get()]
        ssn      = self.bill_cashier_map[self.bill_cashier_cb.get()]
        total    = sum(p * q for _, _, p, q in self.cart_items)
        disc_rs  = round(total * disc_pct / 100, 2)
        now      = datetime.now()
        row = fetchone("SELECT COALESCE(MAX(Bill_ID),500)+1 FROM BILL")
        new_id = row[0]
        execute("""INSERT INTO BILL(Bill_ID,Bill_Date,Bill_Time,Total_Amount,
        Discount,Final_Amount,Customer_ID,Shop_ID,SSN)
        VALUES(%s,%s,%s,%s,%s,NULL,%s,%s,%s)""",
                (new_id, now.date(), now.time(), total, disc_pct,
                 cust_id, shop_id, ssn))
        for iid, _, _, qty in self.cart_items:
            execute("INSERT INTO BILL_ITEM(Bill_ID,Item_ID,Quantity) VALUES(%s,%s,%s)",
                    (new_id, iid, qty))
        final = float(fetchone("SELECT Final_Amount FROM BILL WHERE Bill_ID=%s",(new_id,))[0])
        win = tk.Toplevel(self)
        win.title(f"Receipt — Bill #{new_id}")
        win.geometry("480x440")
        win.configure(bg=CARD2)
        txt = scrolledtext.ScrolledText(win, bg=CARD2, fg=TEXT,
                                        font=FONT_MONO, relief="flat")
        txt.pack(fill="both", expand=True, padx=12, pady=12)
        lines = [
            "=" * 52,
            f"  RECEIPT   Bill #{new_id}",
            f"  Date: {now.strftime('%Y-%m-%d %H:%M')}",
            "-" * 52,
            f"  {'Item':<22} {'Qty':>4}  {'Price':>8}  {'Total':>9}",
            "-" * 52,
        ]
        for _, name, price, qty in self.cart_items:
            lines.append(f"  {name:<22} {qty:>4}  {price:>8.2f}  {price*qty:>9.2f}")
        lines += [
            "-" * 52,
            f"  {'Subtotal':<36} {total:>9.2f}",
            f"  {'Discount ({:.0f}%)'.format(disc_pct):<36} {disc_rs:>9.2f}",
            f"  {'FINAL AMOUNT':<36} {final:>9.2f}",
            "=" * 52,
            "",
            "  [Trigger] Final_Amount = Total - (Total × Discount%)",
            "  [Trigger] Interaction logged",
        ]
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")
        self._clear_cart()
        self.bill_cust_cb.set("")
        self.bill_shop_cb.set("")
        self.bill_cashier_cb.set("")

    # ═══════════════════════════════════
    #  VIEW & SEARCH
    # ═══════════════════════════════════
    def _build_view(self, parent):
        self._page_header(parent, "View & Search", "Browse bills, customers, items", ACCENT2)
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=24, pady=4)
        style = ttk.Style()
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD, foreground=TEXT,
                        padding=[14,6], font=FONT)
        style.map("TNotebook.Tab", background=[("selected",HDR_BG)],
                  foreground=[("selected",ACCENT)])
        t1 = tk.Frame(nb, bg=BG); nb.add(t1, text="All Bills")
        tk.Button(t1, text="↻ Load Bills", command=lambda: self._load_bills(bt1),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(anchor="w", padx=12, pady=8)
        bt1 = make_tree(t1, ["Bill ID","Customer","Shop","Date","Total","Discount","Final"])
        self._load_bills(bt1)
        t2 = tk.Frame(nb, bg=BG); nb.add(t2, text="Bills by Customer")
        row2 = tk.Frame(t2, bg=BG); row2.pack(fill="x", padx=12, pady=8)
        tk.Label(row2, text="Customer:", bg=BG, fg=TEXT, font=FONT).pack(side="left")
        self.view_cust_var = tk.StringVar()
        _, rows = fetch("SELECT Customer_ID, Name FROM CUSTOMER ORDER BY Customer_ID")
        cust_map2 = {f"{r[0]} — {r[1]}": r[0] for r in rows}
        cb2 = StyledDropdown(row2, values=list(cust_map2.keys()), width=28, accent=ACCENT2)
        cb2.pack(side="left", padx=8)
        bt2 = make_tree(t2, ["Bill ID","Shop","Date","Final Amount","Cashier"])
        tk.Button(row2, text="Search",
                  command=lambda: self._search_cust_bills(bt2, cust_map2, cb2),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, cursor="hand2").pack(side="left")
        t3 = tk.Frame(nb, bg=BG); nb.add(t3, text="Search Items")
        row3 = tk.Frame(t3, bg=BG); row3.pack(fill="x", padx=12, pady=8)
        tk.Label(row3, text="Name contains:", bg=BG, fg=TEXT, font=FONT).pack(side="left")
        self.item_search_var = tk.StringVar()
        e3 = make_entry(row3, 20); e3.config(textvariable=self.item_search_var)
        e3.pack(side="left", padx=8)
        bt3 = make_tree(t3, ["ID","Name","Category","Price","Shop"])
        tk.Button(row3, text="Search",
                  command=lambda: self._search_items(bt3, self.item_search_var),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, cursor="hand2").pack(side="left")
        self._search_items(bt3, self.item_search_var)

    def _load_bills(self, tree):
        _, rows = fetch("""
        SELECT B.Bill_ID,C.Name,S.Shop_Name,B.Bill_Date,
        B.Total_Amount,B.Discount,B.Final_Amount
        FROM BILL B
        JOIN CUSTOMER C ON B.Customer_ID=C.Customer_ID
        JOIN SHOP S ON B.Shop_ID=S.Shop_ID
        ORDER BY B.Bill_Date DESC, B.Bill_ID DESC
        """)
        load_tree(tree, rows)

    def _search_cust_bills(self, tree, cust_map, cb):
        if not cb.get(): return
        cid = cust_map[cb.get()]
        _, rows = fetch("""
        SELECT B.Bill_ID,S.Shop_Name,B.Bill_Date,B.Final_Amount,E.Employee_Name
        FROM BILL B
        JOIN SHOP S ON B.Shop_ID=S.Shop_ID
        JOIN EMPLOYEE E ON B.SSN=E.SSN
        WHERE B.Customer_ID=%s ORDER BY B.Bill_Date DESC
        """, (cid,))
        load_tree(tree, rows)

    def _search_items(self, tree, var):
        q = f"%{var.get()}%"
        _, rows = fetch("""
        SELECT I.Item_ID,I.Item_Name,I.Category,I.Price,S.Shop_Name
        FROM ITEM I JOIN SHOP S ON I.Shop_ID=S.Shop_ID
        WHERE I.Item_Name LIKE %s ORDER BY I.Item_Name
        """, (q,))
        load_tree(tree, rows)

    # ═══════════════════════════════════
    #  ANALYTICS
    # ═══════════════════════════════════
    def _build_analytics(self, parent):
        self._page_header(parent, "Analytics & Reports", "Business intelligence from your data", WARNING)
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=24, pady=4)
        tabs = [
            ("Customer Spending", self._build_cust_report),
            ("Shop Revenue",      self._build_shop_report),
            ("Top Items",         self._build_top_items),
            ("Employees",         self._build_emp_report),
            ("Parking",           self._build_parking_report),
        ]
        for name, builder in tabs:
            t = tk.Frame(nb, bg=BG)
            nb.add(t, text=name)
            builder(t)

    def _build_cust_report(self, parent):
        tk.Button(parent, text="↻ Load", command=lambda: self._load_cust_report(tree),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(anchor="w", padx=12, pady=8)
        tree = make_tree(parent, ["Name","City","Bills","Total Spent","Avg Bill","Tier"])
        self._load_cust_report(tree)

    def _load_cust_report(self, tree):
        _, rows = fetch("""
        SELECT C.Name, C.City, COUNT(B.Bill_ID),
        COALESCE(SUM(B.Final_Amount),0),
        COALESCE(AVG(B.Final_Amount),0),
        CASE WHEN SUM(B.Final_Amount)>=50000 THEN 'PLATINUM'
        WHEN SUM(B.Final_Amount)>=20000 THEN 'GOLD'
        WHEN SUM(B.Final_Amount)>=5000  THEN 'SILVER'
        ELSE 'STANDARD' END
        FROM CUSTOMER C LEFT JOIN BILL B ON C.Customer_ID=B.Customer_ID
        GROUP BY C.Customer_ID,C.Name,C.City ORDER BY 4 DESC
        """)
        load_tree(tree, rows)

    def _build_shop_report(self, parent):
        tk.Button(parent, text="↻ Load", command=lambda: self._load_shop_report(tree),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(anchor="w", padx=12, pady=8)
        tree = make_tree(parent, ["Shop","Category","Bills","Revenue","Items Sold"])
        self._load_shop_report(tree)

    def _load_shop_report(self, tree):
        _, rows = fetch("""
        SELECT S.Shop_Name,S.Category,COUNT(DISTINCT B.Bill_ID),
        COALESCE(SUM(B.Final_Amount),0),COALESCE(SUM(BI.Quantity),0)
        FROM SHOP S LEFT JOIN BILL B ON S.Shop_ID=B.Shop_ID
        LEFT JOIN BILL_ITEM BI ON B.Bill_ID=BI.Bill_ID
        GROUP BY S.Shop_ID,S.Shop_Name,S.Category ORDER BY 4 DESC
        """)
        load_tree(tree, rows)

    def _build_top_items(self, parent):
        row = tk.Frame(parent, bg=BG); row.pack(fill="x", padx=12, pady=8)
        tk.Label(row, text="Top N items:", bg=BG, fg=TEXT, font=FONT).pack(side="left")
        self.top_n_var = tk.StringVar(value="5")
        e = make_entry(row, 5); e.config(textvariable=self.top_n_var); e.pack(side="left",padx=8)
        tree = make_tree(parent, ["Item","Category","Shop","Units Sold","Revenue"])
        tk.Button(row, text="Load",
                  command=lambda: self._load_top_items(tree, self.top_n_var),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, cursor="hand2").pack(side="left")
        self._load_top_items(tree, self.top_n_var)

    def _load_top_items(self, tree, var):
        try: n = int(var.get())
        except: n = 5
        _, rows = fetch("""
        SELECT I.Item_Name,I.Category,S.Shop_Name,
        SUM(BI.Quantity),SUM(BI.Quantity*I.Price)
        FROM ITEM I JOIN BILL_ITEM BI ON I.Item_ID=BI.Item_ID
        JOIN SHOP S ON I.Shop_ID=S.Shop_ID
        GROUP BY I.Item_ID,I.Item_Name,I.Category,S.Shop_Name
        ORDER BY 5 DESC LIMIT %s
        """, (n,))
        load_tree(tree, rows)

    def _build_emp_report(self, parent):
        tk.Button(parent, text="↻ Load", command=lambda: self._load_emp_report(tree),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(anchor="w", padx=12, pady=8)
        tree = make_tree(parent, ["Name","Designation","Shop","Bills","Revenue Handled","Salary"])
        self._load_emp_report(tree)

    def _load_emp_report(self, tree):
        _, rows = fetch("""
        SELECT E.Employee_Name,E.Designation,S.Shop_Name,
        COUNT(B.Bill_ID),COALESCE(SUM(B.Final_Amount),0),E.Salary
        FROM EMPLOYEE E LEFT JOIN BILL B ON E.SSN=B.SSN
        JOIN SHOP S ON E.Shop_ID=S.Shop_ID
        GROUP BY E.Employee_ID,E.Employee_Name,E.Designation,S.Shop_Name,E.Salary
        ORDER BY 5 DESC
        """)
        load_tree(tree, rows)

    def _build_parking_report(self, parent):
        tk.Button(parent, text="↻ Load", command=lambda: self._load_parking(tree),
                  bg=BTN_BG, fg=BTN_FG, font=FONT_B, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(anchor="w", padx=12, pady=8)
        tree = make_tree(parent, ["Vehicle","Slot","Type","Entry","Exit","Mins","Fee"])
        self._load_parking(tree)

    def _load_parking(self, tree):
        _, rows = fetch("""
        SELECT PR.Vehicle_Number,PS.Slot_Number,PS.Slot_Type,
        PR.Entry_Time,PR.Exit_Time,PR.Duration,PR.Parking_Fee
        FROM PARKING_RECORD PR JOIN PARKING_SLOT PS ON PR.Slot_ID=PS.Slot_ID
        ORDER BY PR.Entry_Time DESC
        """)
        load_tree(tree, rows)

    # ═══════════════════════════════════
    #  MANAGE DATA
    # ═══════════════════════════════════
    def _build_manage(self, parent):
        self._page_header(parent, "Manage Data", "Add/remove customers, employees, items, shops, parking slots", ORANGE)
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=24, pady=4)
        tabs = [
            ("Add Customer",        self._build_add_customer),
            ("Add Employee",        self._build_add_employee),
            ("Update Salary",       self._build_update_salary),
            ("Add Item",            self._build_add_item),
            ("Add Shop",            self._build_add_shop),
            ("Add Parking Slot",    self._build_add_parking),
            ("Remove Parking Slot", self._build_remove_parking),   # ← NEW
        ]
        for name, builder in tabs:
            t = tk.Frame(nb, bg=BG)
            nb.add(t, text=name)
            builder(t)

    def _form_frame(self, parent):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(pady=20, padx=40, anchor="nw")
        f = tk.Frame(outer, bg=CARD2, padx=24, pady=20,
                     highlightthickness=1, highlightbackground=HDR_BG)
        f.pack()
        return f

    def _form_row(self, parent, label, default="", show=None):
        row = tk.Frame(parent, bg=CARD2)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        var = tk.StringVar(value=default)
        e = tk.Entry(row, bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                     font=FONT, relief="flat", width=26, bd=4,
                     highlightthickness=1, highlightbackground=HDR_BG,
                     highlightcolor=ACCENT)
        e.config(textvariable=var)
        if show: e.config(show=show)
        e.pack(side="left")
        return var

    def _build_add_customer(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Add New Customer", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,12))
        name  = self._form_row(f, "Name")
        phone = self._form_row(f, "Phone")
        email = self._form_row(f, "Email")
        city  = self._form_row(f, "City")
        msg   = tk.Label(f, text="", bg=CARD2, font=FONT)
        msg.pack(pady=4)
        def submit():
            if not name.get().strip():
                msg.config(text="Name is required", fg=DANGER); return
            row = fetchone("SELECT COALESCE(MAX(Customer_ID),300)+1 FROM CUSTOMER")
            nid = row[0]
            try:
                execute("""INSERT INTO CUSTOMER(Customer_ID,Name,Phone_No,Email_ID,City)
                VALUES(%s,%s,%s,%s,%s)""",
                        (nid, name.get(), phone.get(), email.get(), city.get()))
                msg.config(text=f"✓ Customer added with ID = {nid}", fg=SUCCESS)
                for v in [name,phone,email,city]: v.set("")
            except Error as e:
                msg.config(text=str(e), fg=DANGER)
        b = tk.Button(f, text="Add Customer", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    def _build_add_employee(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Add New Employee", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,4))
        tk.Label(f, text="Note: Salary ≤ 0 will be auto-corrected to Rs 15,000 by trigger",
                 bg=CARD2, fg=WARNING, font=("Segoe UI",9)).pack(anchor="w", pady=(0,10))
        ssn    = self._form_row(f, "SSN (unique)")
        name   = self._form_row(f, "Name")
        desig  = self._form_row(f, "Designation")
        salary = self._form_row(f, "Salary (Rs)", "0")
        phone  = self._form_row(f, "Phone")
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Shop", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        _, shops = fetch("SELECT Shop_ID, Shop_Name FROM SHOP ORDER BY Shop_ID")
        shop_map = {f"{r[0]} — {r[1]}": r[0] for r in shops}
        shop_dd = StyledDropdown(row, values=list(shop_map.keys()), width=26, accent=SUCCESS)
        shop_dd.pack(side="left")
        msg = tk.Label(f, text="", bg=CARD2, font=FONT); msg.pack(pady=4)
        def submit():
            if not ssn.get().strip() or not name.get().strip():
                msg.config(text="SSN and Name are required", fg=DANGER); return
            if not shop_dd.get():
                msg.config(text="Select a shop", fg=DANGER); return
            try: sal = float(salary.get())
            except: msg.config(text="Invalid salary", fg=DANGER); return
            nid = fetchone("SELECT COALESCE(MAX(Employee_ID),200)+1 FROM EMPLOYEE")[0]
            shop_id = shop_map[shop_dd.get()]
            try:
                execute("""INSERT INTO EMPLOYEE(Employee_ID,SSN,Employee_Name,
                Designation,Salary,Phone_No,Shop_ID)
                VALUES(%s,%s,%s,%s,%s,%s,%s)""",
                        (nid,ssn.get(),name.get(),desig.get(),sal,phone.get(),shop_id))
                stored = float(fetchone("SELECT Salary FROM EMPLOYEE WHERE Employee_ID=%s",(nid,))[0])
                note = f"  (trigger corrected to {stored})" if stored != sal else ""
                msg.config(text=f"✓ Employee added ID={nid}{note}", fg=SUCCESS)
                for v in [ssn,name,desig,salary,phone]: v.set("")
                shop_dd.set("")
            except Error as e:
                msg.config(text=str(e), fg=DANGER)
        b = tk.Button(f, text="Add Employee", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    def _build_update_salary(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Update Employee Salary", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,4))
        tk.Label(f, text="Trigger will reject salary ≤ 0 and reset to Rs 15,000",
                 bg=CARD2, fg=WARNING, font=("Segoe UI",9)).pack(anchor="w", pady=(0,10))
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Employee", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        _, emps = fetch("SELECT Employee_ID,Employee_Name,Salary FROM EMPLOYEE ORDER BY Employee_ID")
        emp_map = {f"{r[0]} — {r[1]}  (Rs {r[2]})": (r[0], float(r[2])) for r in emps}
        emp_dd = StyledDropdown(row, values=list(emp_map.keys()), width=32, accent=WARNING)
        emp_dd.pack(side="left")
        new_sal = self._form_row(f, "New Salary (Rs)", "0")
        msg = tk.Label(f, text="", bg=CARD2, font=FONT); msg.pack(pady=4)
        def submit():
            if not emp_dd.get():
                msg.config(text="Select an employee", fg=DANGER); return
            try: sal = float(new_sal.get())
            except: msg.config(text="Invalid salary", fg=DANGER); return
            eid, _ = emp_map[emp_dd.get()]
            execute("UPDATE EMPLOYEE SET Salary=%s WHERE Employee_ID=%s",(sal,eid))
            stored = float(fetchone("SELECT Salary FROM EMPLOYEE WHERE Employee_ID=%s",(eid,))[0])
            note = f"  ← trigger corrected to {stored}" if stored != sal else ""
            msg.config(text=f"✓ Salary updated to Rs {stored:,.2f}{note}", fg=SUCCESS)
        b = tk.Button(f, text="Update Salary", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    def _build_add_item(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Add New Item", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,12))
        name     = self._form_row(f, "Item Name")
        category = self._form_row(f, "Category")
        price    = self._form_row(f, "Price (Rs)", "0")
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Shop", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        _, shops = fetch("SELECT Shop_ID,Shop_Name FROM SHOP ORDER BY Shop_ID")
        shop_map = {f"{r[0]} — {r[1]}": r[0] for r in shops}
        shop_dd = StyledDropdown(row, values=list(shop_map.keys()), width=26, accent=ORANGE)
        shop_dd.pack(side="left")
        msg = tk.Label(f, text="", bg=CARD2, font=FONT); msg.pack(pady=4)
        def submit():
            if not name.get().strip():
                msg.config(text="Item name required", fg=DANGER); return
            if not shop_dd.get():
                msg.config(text="Select a shop", fg=DANGER); return
            try: p = float(price.get())
            except: msg.config(text="Invalid price", fg=DANGER); return
            nid = fetchone("SELECT COALESCE(MAX(Item_ID),400)+1 FROM ITEM")[0]
            shop_id = shop_map[shop_dd.get()]
            try:
                execute("INSERT INTO ITEM(Item_ID,Item_Name,Category,Price,Shop_ID) VALUES(%s,%s,%s,%s,%s)",
                        (nid, name.get(), category.get(), p, shop_id))
                msg.config(text=f"✓ Item added with ID = {nid}", fg=SUCCESS)
                for v in [name,category,price]: v.set("")
                shop_dd.set("")
            except Error as e:
                msg.config(text=str(e), fg=DANGER)
        b = tk.Button(f, text="Add Item", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    def _build_add_shop(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Add New Shop", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,12))
        name     = self._form_row(f, "Shop Name")
        category = self._form_row(f, "Category")
        owner    = self._form_row(f, "Owner Name")
        floor_no = self._form_row(f, "Floor Number", "1")
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Mall", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        _, malls = fetch("SELECT Mall_ID,Mall_Name FROM MALL ORDER BY Mall_ID")
        mall_map = {f"{r[0]} — {r[1]}": r[0] for r in malls}
        mall_dd = StyledDropdown(row, values=list(mall_map.keys()), width=26, accent=ACCENT2)
        mall_dd.pack(side="left")
        msg = tk.Label(f, text="", bg=CARD2, font=FONT); msg.pack(pady=4)
        def submit():
            if not name.get().strip():
                msg.config(text="Shop name required", fg=DANGER); return
            if not mall_dd.get():
                msg.config(text="Select a mall", fg=DANGER); return
            try: fl = int(floor_no.get())
            except: msg.config(text="Invalid floor number", fg=DANGER); return
            nid = fetchone("SELECT COALESCE(MAX(Shop_ID),100)+1 FROM SHOP")[0]
            mall_id = mall_map[mall_dd.get()]
            try:
                execute("INSERT INTO SHOP(Shop_ID,Shop_Name,Category,Owner_Name,Floor_No,Mall_ID) VALUES(%s,%s,%s,%s,%s,%s)",
                        (nid,name.get(),category.get(),owner.get(),fl,mall_id))
                msg.config(text=f"✓ Shop added with ID = {nid}", fg=SUCCESS)
                for v in [name,category,owner,floor_no]: v.set("")
                mall_dd.set("")
            except Error as e:
                msg.config(text=str(e), fg=DANGER)
        b = tk.Button(f, text="Add Shop", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    def _build_add_parking(self, parent):
        f = self._form_frame(parent)
        tk.Label(f, text="Add New Parking Slot", bg=CARD2, fg=ACCENT,
                 font=FONT_H).pack(anchor="w", pady=(0,12))
        slot_num  = self._form_row(f, "Slot Number (e.g. A3)")
        slot_type = self._form_row(f, "Type (Car/Bike/Bus)", "Car")
        floor_no  = self._form_row(f, "Floor (use -1 for basement)", "0")
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Mall", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")
        _, malls = fetch("SELECT Mall_ID,Mall_Name FROM MALL ORDER BY Mall_ID")
        mall_map = {f"{r[0]} — {r[1]}": r[0] for r in malls}
        mall_dd = StyledDropdown(row, values=list(mall_map.keys()), width=26, accent=TEAL)
        mall_dd.pack(side="left")
        msg = tk.Label(f, text="", bg=CARD2, font=FONT); msg.pack(pady=4)
        def submit():
            if not slot_num.get().strip():
                msg.config(text="Slot number required", fg=DANGER); return
            if not mall_dd.get():
                msg.config(text="Select a mall", fg=DANGER); return
            try: fl = int(floor_no.get())
            except: msg.config(text="Invalid floor", fg=DANGER); return
            nid = fetchone("SELECT COALESCE(MAX(Slot_ID),600)+1 FROM PARKING_SLOT")[0]
            mall_id = mall_map[mall_dd.get()]
            try:
                execute("INSERT INTO PARKING_SLOT(Slot_ID,Slot_Number,Slot_Type,Floor_No,Mall_ID) VALUES(%s,%s,%s,%s,%s)",
                        (nid,slot_num.get(),slot_type.get(),fl,mall_id))
                msg.config(text=f"✓ Parking slot added with ID = {nid}", fg=SUCCESS)
                for v in [slot_num,floor_no]: v.set("")
                slot_type.set("Car"); mall_dd.set("")
            except Error as e:
                msg.config(text=str(e), fg=DANGER)
        b = tk.Button(f, text="Add Slot", command=submit)
        style_button(b); b.pack(pady=8, anchor="w")

    # ─────────────────────────────────────────────
    #  NEW: REMOVE PARKING SLOT
    # ─────────────────────────────────────────────
    def _build_remove_parking(self, parent):
        """Tab to remove a parking slot (only if it has no active/linked records)."""
        f = self._form_frame(parent)
        tk.Label(f, text="Remove Parking Slot", bg=CARD2, fg=DANGER,
                 font=FONT_H).pack(anchor="w", pady=(0,4))
        tk.Label(f,
                 text="Only slots with no linked parking records can be deleted.\n"
                      "Select a slot from the list, verify details, then confirm.",
                 bg=CARD2, fg=WARNING, font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(0,10))

        # Slot picker row
        row = tk.Frame(f, bg=CARD2); row.pack(fill="x", pady=5)
        tk.Label(row, text="Parking Slot", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=22, anchor="w").pack(side="left")

        self._rm_slot_map = {}
        self._rm_slot_dd = StyledDropdown(row, width=32, accent=DANGER)
        self._rm_slot_dd.pack(side="left")

        def refresh_slots():
            _, rows = fetch("""
                SELECT PS.Slot_ID, PS.Slot_Number, PS.Slot_Type, PS.Floor_No, M.Mall_Name
                FROM PARKING_SLOT PS JOIN MALL M ON PS.Mall_ID = M.Mall_ID
                ORDER BY PS.Slot_ID
            """)
            self._rm_slot_map = {
                f"{r[0]} — {r[1]}  ({r[2]}, Floor {r[3]}, {r[4]})": r[0]
                for r in rows
            }
            self._rm_slot_dd.set_values(list(self._rm_slot_map.keys()))
            self._rm_slot_dd.set("")
            rm_msg.config(text="")

        refresh_btn = tk.Button(f, text="↻ Refresh slot list", command=refresh_slots,
                                bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 9),
                                relief="flat", cursor="hand2")
        refresh_btn.pack(anchor="w", pady=(2, 8))

        rm_msg = tk.Label(f, text="", bg=CARD2, font=FONT)
        rm_msg.pack(pady=4)

        def do_remove():
            key = self._rm_slot_dd.get()
            if not key:
                rm_msg.config(text="Please select a slot first.", fg=DANGER)
                return
            slot_id = self._rm_slot_map[key]
            # Check for linked PARKING_RECORD rows
            linked = fetchone(
                "SELECT COUNT(*) FROM PARKING_RECORD WHERE Slot_ID=%s", (slot_id,))[0]
            if linked > 0:
                rm_msg.config(
                    text=f"✗ Cannot delete — {linked} parking record(s) linked to this slot.",
                    fg=DANGER)
                return
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Permanently delete slot:\n\n  {key}\n\nThis cannot be undone.",
                icon="warning")
            if not confirm:
                return
            try:
                execute("DELETE FROM PARKING_SLOT WHERE Slot_ID=%s", (slot_id,))
                rm_msg.config(text=f"✓ Slot ID {slot_id} deleted successfully.", fg=SUCCESS)
                refresh_slots()
            except Error as e:
                rm_msg.config(text=str(e), fg=DANGER)

        b = tk.Button(f, text="🗑  Delete Selected Slot", command=do_remove)
        style_button(b, color=DANGER, fg=WHITE, hover="#ff7070")
        b.pack(pady=8, anchor="w")

        # Load slots on first visit
        refresh_slots()

    # ═══════════════════════════════════════════════════════════════
    #  NEW: PARKING MANAGER PAGE
    # ═══════════════════════════════════════════════════════════════
    def _build_parking_manager(self, parent):
        self._page_header(parent, "Parking Manager",
                          "Record vehicle entry/exit. Trigger prevents double-booking slots.", TEAL)

        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=24, pady=4)

        # ── Tab 1: Vehicle Entry ────────────────────────────────────
        t_entry = tk.Frame(nb, bg=BG); nb.add(t_entry, text="🚗  Vehicle Entry")
        self._build_pm_entry_tab(t_entry)

        # ── Tab 2: Vehicle Exit ─────────────────────────────────────
        t_exit = tk.Frame(nb, bg=BG); nb.add(t_exit, text="🚪  Vehicle Exit")
        self._build_pm_exit_tab(t_exit)

        # ── Tab 3: Occupancy ────────────────────────────────────────
        t_occ = tk.Frame(nb, bg=BG); nb.add(t_occ, text="📊  Occupancy")
        self._build_pm_occupancy_tab(t_occ)

    # ── Vehicle Entry tab ───────────────────────────────────────────
    def _build_pm_entry_tab(self, parent):
        body = tk.Frame(parent, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # Left: table of AVAILABLE slots
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        hdr_row = tk.Frame(left, bg=BG); hdr_row.pack(fill="x")
        tk.Label(hdr_row, text="Available Slots", bg=BG, fg=TEXT,
                 font=FONT_H).pack(side="left", pady=(0, 6))
        tk.Button(hdr_row, text="↻ Refresh",
                  command=self._pm_refresh_slots,
                  bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=8).pack(side="left", padx=10)

        self.pm_slot_tree = make_tree(
            left, ["Slot ID", "Number", "Type", "Floor", "Mall"], height=12)
        self.pm_slot_tree.bind("<<TreeviewSelect>>", self._pm_on_slot_select)
        self._pm_refresh_slots()

        # Right: entry form
        right = tk.Frame(body, bg=CARD2, padx=20, pady=20,
                         highlightthickness=1, highlightbackground=HDR_BG)
        right.pack(side="left", fill="y")

        tk.Label(right, text="Record Vehicle Entry", bg=CARD2, fg=TEAL,
                 font=FONT_H).pack(anchor="w", pady=(0, 12))

        # Slot ID (auto-filled on row click, or manual)
        r1 = tk.Frame(right, bg=CARD2); r1.pack(fill="x", pady=5)
        tk.Label(r1, text="Slot ID", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        self.pm_entry_slot_var = tk.StringVar()
        e_slot = tk.Entry(r1, textvariable=self.pm_entry_slot_var,
                          bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                          font=FONT, relief="flat", width=14, bd=4)
        e_slot.pack(side="left")

        # Vehicle number
        r2 = tk.Frame(right, bg=CARD2); r2.pack(fill="x", pady=5)
        tk.Label(r2, text="Vehicle Number", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        self.pm_entry_veh_var = tk.StringVar()
        tk.Entry(r2, textvariable=self.pm_entry_veh_var,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                 font=FONT, relief="flat", width=14, bd=4).pack(side="left")

        tk.Label(right, text="(Click a row above to auto-fill Slot ID)",
                 bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 10))

        self.pm_entry_msg = tk.Label(right, text="", bg=CARD2, font=FONT, wraplength=220)
        self.pm_entry_msg.pack(pady=4)

        b = tk.Button(right, text="Record Entry  →", command=self._pm_record_entry)
        style_button(b, color=TEAL, fg=BG, hover="#a0fff0")
        b.pack(pady=8, anchor="w")

    def _pm_refresh_slots(self):
        """Reload available (unoccupied) parking slots."""
        try:
            _, rows = fetch("""
                SELECT PS.Slot_ID, PS.Slot_Number, PS.Slot_Type,
                       PS.Floor_No, M.Mall_Name
                FROM PARKING_SLOT PS
                JOIN MALL M ON PS.Mall_ID = M.Mall_ID
                WHERE PS.Slot_ID NOT IN (
                    SELECT Slot_ID FROM PARKING_RECORD WHERE Exit_Time IS NULL
                )
                ORDER BY PS.Slot_ID
            """)
            load_tree(self.pm_slot_tree, rows)
        except Exception:
            pass  # tree may not exist yet on first call

    def _pm_on_slot_select(self, event=None):
        """Auto-fill Slot ID field when user clicks a row."""
        sel = self.pm_slot_tree.selection()
        if sel:
            vals = self.pm_slot_tree.item(sel[0], "values")
            self.pm_entry_slot_var.set(vals[0])

    def _pm_record_entry(self):
        slot_id = self.pm_entry_slot_var.get().strip()
        vehicle = self.pm_entry_veh_var.get().strip().upper()
        if not slot_id:
            self.pm_entry_msg.config(text="Slot ID is required.", fg=DANGER); return
        if not vehicle:
            self.pm_entry_msg.config(text="Vehicle number is required.", fg=DANGER); return
        try:
            slot_id = int(slot_id)
        except ValueError:
            self.pm_entry_msg.config(text="Slot ID must be a number.", fg=DANGER); return

        # Check slot exists
        slot = fetchone("SELECT Slot_ID FROM PARKING_SLOT WHERE Slot_ID=%s", (slot_id,))
        if not slot:
            self.pm_entry_msg.config(text=f"Slot ID {slot_id} does not exist.", fg=DANGER)
            return

        # Check not already occupied
        occupied = fetchone(
            "SELECT COUNT(*) FROM PARKING_RECORD WHERE Slot_ID=%s AND Exit_Time IS NULL",
            (slot_id,))[0]
        if occupied:
            self.pm_entry_msg.config(
                text=f"Slot {slot_id} is already occupied!", fg=DANGER)
            return

        # Check vehicle not already parked somewhere
        already = fetchone(
            "SELECT COUNT(*) FROM PARKING_RECORD WHERE Vehicle_Number=%s AND Exit_Time IS NULL",
            (vehicle,))[0]
        if already:
            self.pm_entry_msg.config(
                text=f"Vehicle {vehicle} is already parked in another slot.", fg=DANGER)
            return

        now = datetime.now()
        new_id = fetchone("SELECT COALESCE(MAX(Parking_ID),700)+1 FROM PARKING_RECORD")[0]
        try:
            execute("""
                INSERT INTO PARKING_RECORD
                    (Parking_ID, Vehicle_Number, Entry_Time, Exit_Time,
                     Duration, Parking_Fee, Slot_ID)
                VALUES (%s, %s, %s, NULL, NULL, NULL, %s)
            """, (new_id, vehicle, now, slot_id))
            self.pm_entry_msg.config(
                text=f"✓ Entry recorded!\nParking ID: {new_id}\nVehicle: {vehicle}\nSlot: {slot_id}",
                fg=SUCCESS)
            self.pm_entry_slot_var.set("")
            self.pm_entry_veh_var.set("")
            self._pm_refresh_slots()
        except Error as e:
            self.pm_entry_msg.config(text=str(e), fg=DANGER)

    # ── Vehicle Exit tab ────────────────────────────────────────────
    def _build_pm_exit_tab(self, parent):
        body = tk.Frame(parent, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # Left: currently occupied slots
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        hdr_row = tk.Frame(left, bg=BG); hdr_row.pack(fill="x")
        tk.Label(hdr_row, text="Currently Occupied Slots", bg=BG, fg=TEXT,
                 font=FONT_H).pack(side="left", pady=(0, 6))
        tk.Button(hdr_row, text="↻ Refresh",
                  command=self._pm_refresh_occupied,
                  bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=8).pack(side="left", padx=10)

        self.pm_occ_tree = make_tree(
            left,
            ["Parking ID", "Vehicle", "Slot", "Type", "Entry Time", "Mall"],
            height=12)
        self.pm_occ_tree.bind("<<TreeviewSelect>>", self._pm_on_occ_select)
        self._pm_refresh_occupied()

        # Right: exit form
        right = tk.Frame(body, bg=CARD2, padx=20, pady=20,
                         highlightthickness=1, highlightbackground=HDR_BG)
        right.pack(side="left", fill="y")

        tk.Label(right, text="Record Vehicle Exit", bg=CARD2, fg=ORANGE,
                 font=FONT_H).pack(anchor="w", pady=(0, 12))

        r1 = tk.Frame(right, bg=CARD2); r1.pack(fill="x", pady=5)
        tk.Label(r1, text="Parking ID", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        self.pm_exit_pid_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.pm_exit_pid_var,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                 font=FONT, relief="flat", width=14, bd=4).pack(side="left")

        r2 = tk.Frame(right, bg=CARD2); r2.pack(fill="x", pady=5)
        tk.Label(r2, text="Fee per Hour (Rs)", bg=CARD2, fg=SUBTEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        self.pm_fee_rate_var = tk.StringVar(value="50")
        tk.Entry(r2, textvariable=self.pm_fee_rate_var,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                 font=FONT, relief="flat", width=14, bd=4).pack(side="left")

        tk.Label(right, text="(Click a row above to auto-fill Parking ID)",
                 bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 10))

        self.pm_exit_msg = tk.Label(right, text="", bg=CARD2, font=FONT, wraplength=220)
        self.pm_exit_msg.pack(pady=4)

        b = tk.Button(right, text="Record Exit  →", command=self._pm_record_exit)
        style_button(b, color=ORANGE, fg=BG, hover="#ffc060")
        b.pack(pady=8, anchor="w")

    def _pm_refresh_occupied(self):
        try:
            _, rows = fetch("""
                SELECT PR.Parking_ID, PR.Vehicle_Number, PS.Slot_Number,
                       PS.Slot_Type, PR.Entry_Time, M.Mall_Name
                FROM PARKING_RECORD PR
                JOIN PARKING_SLOT PS ON PR.Slot_ID = PS.Slot_ID
                JOIN MALL M ON PS.Mall_ID = M.Mall_ID
                WHERE PR.Exit_Time IS NULL
                ORDER BY PR.Entry_Time DESC
            """)
            load_tree(self.pm_occ_tree, rows)
        except Exception:
            pass

    def _pm_on_occ_select(self, event=None):
        sel = self.pm_occ_tree.selection()
        if sel:
            vals = self.pm_occ_tree.item(sel[0], "values")
            self.pm_exit_pid_var.set(vals[0])

    def _pm_record_exit(self):
        pid_str = self.pm_exit_pid_var.get().strip()
        if not pid_str:
            self.pm_exit_msg.config(text="Parking ID is required.", fg=DANGER); return
        try:
            pid = int(pid_str)
            rate = float(self.pm_fee_rate_var.get())
        except ValueError:
            self.pm_exit_msg.config(text="Invalid Parking ID or fee rate.", fg=DANGER); return

        rec = fetchone("""
            SELECT Parking_ID, Entry_Time FROM PARKING_RECORD
            WHERE Parking_ID=%s AND Exit_Time IS NULL
        """, (pid,))
        if not rec:
            self.pm_exit_msg.config(
                text=f"No active entry found for Parking ID {pid}.", fg=DANGER)
            return

        entry_time = rec[1]
        now        = datetime.now()
        duration_m = max(1, int((now - entry_time).total_seconds() / 60))
        fee        = round((duration_m / 60) * rate, 2)

        try:
            execute("""
                UPDATE PARKING_RECORD
                SET Exit_Time=%s, Duration=%s, Parking_Fee=%s
                WHERE Parking_ID=%s
            """, (now, duration_m, fee, pid))
            self.pm_exit_msg.config(
                text=(f"✓ Exit recorded!\n"
                      f"Duration: {duration_m} min\n"
                      f"Fee: Rs {fee:.2f}"),
                fg=SUCCESS)
            self.pm_exit_pid_var.set("")
            self._pm_refresh_occupied()
            self._pm_refresh_slots()
        except Error as e:
            self.pm_exit_msg.config(text=str(e), fg=DANGER)

    # ── Occupancy tab ───────────────────────────────────────────────
    def _build_pm_occupancy_tab(self, parent):
        body = tk.Frame(parent, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # Stat cards row
        self.pm_stat_frame = tk.Frame(body, bg=BG)
        self.pm_stat_frame.pack(fill="x", pady=(0, 12))

        hdr_row = tk.Frame(body, bg=BG); hdr_row.pack(fill="x")
        tk.Label(hdr_row, text="All Parking Records", bg=BG, fg=TEXT,
                 font=FONT_H).pack(side="left", pady=(0, 6))
        tk.Button(hdr_row, text="↻ Refresh",
                  command=self._pm_refresh_occupancy,
                  bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=8).pack(side="left", padx=10)

        self.pm_all_tree = make_tree(
            body,
            ["Parking ID", "Vehicle", "Slot", "Type", "Entry", "Exit", "Mins", "Fee", "Mall"],
            height=14)
        self._pm_refresh_occupancy()

    def _pm_refresh_occupancy(self):
        # Stat cards
        for w in self.pm_stat_frame.winfo_children():
            w.destroy()
        try:
            stats = [
                ("Total Slots",
                 "SELECT COUNT(*) FROM PARKING_SLOT",
                 ACCENT, "🅿️"),
                ("Occupied",
                 "SELECT COUNT(*) FROM PARKING_RECORD WHERE Exit_Time IS NULL",
                 DANGER, "🚗"),
                ("Available",
                 """SELECT COUNT(*) FROM PARKING_SLOT WHERE Slot_ID NOT IN
                    (SELECT Slot_ID FROM PARKING_RECORD WHERE Exit_Time IS NULL)""",
                 SUCCESS, "✅"),
                ("Total Revenue",
                 "SELECT COALESCE(SUM(Parking_Fee),0) FROM PARKING_RECORD WHERE Parking_Fee IS NOT NULL",
                 WARNING, "💰"),
            ]
            for label, sql, color, icon in stats:
                val = fetchone(sql)[0]
                disp = f"Rs {float(val):,.0f}" if label == "Total Revenue" else str(val)
                card = tk.Frame(self.pm_stat_frame, bg=CARD2, padx=18, pady=12,
                                highlightthickness=2, highlightbackground=color)
                card.pack(side="left", padx=6, pady=4)
                tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0, 6))
                tk.Label(card, text=icon, bg=CARD2, fg=color,
                         font=("Segoe UI", 16)).pack()
                tk.Label(card, text=disp, bg=CARD2, fg=color,
                         font=("Segoe UI", 18, "bold")).pack()
                tk.Label(card, text=label, bg=CARD2, fg=SUBTEXT,
                         font=("Segoe UI", 9)).pack()

            # All records table
            _, rows = fetch("""
                SELECT PR.Parking_ID, PR.Vehicle_Number, PS.Slot_Number,
                       PS.Slot_Type, PR.Entry_Time, PR.Exit_Time,
                       PR.Duration, PR.Parking_Fee, M.Mall_Name
                FROM PARKING_RECORD PR
                JOIN PARKING_SLOT PS ON PR.Slot_ID = PS.Slot_ID
                JOIN MALL M ON PS.Mall_ID = M.Mall_ID
                ORDER BY PR.Entry_Time DESC
            """)
            load_tree(self.pm_all_tree, rows)
        except Error as e:
            pass

    # ═══════════════════════════════════
    #  SQL QUERIES
    # ═══════════════════════════════════
    SAVED = {
        "1. Employees above avg salary": """
        SELECT Employee_Name, Designation, Salary FROM EMPLOYEE
        WHERE Salary > (SELECT AVG(Salary) FROM EMPLOYEE) ORDER BY Salary DESC""",
        "2. Customers with no purchases": """
        SELECT Name, City, Phone_No FROM CUSTOMER
        WHERE Customer_ID NOT IN (SELECT DISTINCT Customer_ID FROM BILL)""",
        "3. Most expensive item per shop": """
        SELECT S.Shop_Name, I.Item_Name, I.Price FROM ITEM I
        JOIN SHOP S ON I.Shop_ID=S.Shop_ID
        WHERE I.Price=(SELECT MAX(Price) FROM ITEM WHERE Shop_ID=I.Shop_ID)
        ORDER BY I.Price DESC""",
        "4. Bills with discounts": """
        SELECT B.Bill_ID,C.Name,B.Total_Amount,B.Discount,B.Final_Amount
        FROM BILL B JOIN CUSTOMER C ON B.Customer_ID=C.Customer_ID
        WHERE B.Discount>0 ORDER BY B.Discount DESC""",
        "5. Shops per floor": """
        SELECT Floor_No, COUNT(*) AS Shop_Count,
        GROUP_CONCAT(Shop_Name SEPARATOR ', ') AS Shops
        FROM SHOP GROUP BY Floor_No ORDER BY Floor_No""",
        "6. Parking fees per mall": """
        SELECT M.Mall_Name, COUNT(PR.Parking_ID) AS Vehicles,
        SUM(PR.Parking_Fee) AS Total_Fees
        FROM MALL M JOIN PARKING_SLOT PS ON M.Mall_ID=PS.Mall_ID
        JOIN PARKING_RECORD PR ON PS.Slot_ID=PR.Slot_ID
        GROUP BY M.Mall_ID,M.Mall_Name""",
        "7. Full bill item breakdown": """
        SELECT B.Bill_ID,C.Name,I.Item_Name,BI.Quantity,I.Price,
        (BI.Quantity*I.Price) AS Line_Total
        FROM BILL B JOIN CUSTOMER C ON B.Customer_ID=C.Customer_ID
        JOIN BILL_ITEM BI ON B.Bill_ID=BI.Bill_ID
        JOIN ITEM I ON BI.Item_ID=I.Item_ID ORDER BY B.Bill_ID""",
        "8. Employee-customer interactions": """
        SELECT E.Employee_Name,C.Name AS Customer,EC.Interaction_Date
        FROM EMPLOYEE_CUSTOMER EC
        JOIN EMPLOYEE E ON EC.Employee_ID=E.Employee_ID
        JOIN CUSTOMER C ON EC.Customer_ID=C.Customer_ID
        ORDER BY EC.Interaction_Date DESC""",
        "9. Detailed Bill (Invoice View)": """
        SELECT b.Bill_ID,c.Name AS Customer_Name,s.Shop_Name,
        i.Item_Name,bi.Quantity,i.Price,(bi.Quantity*i.Price) AS Item_Total
        FROM BILL b
        JOIN CUSTOMER c ON b.Customer_ID=c.Customer_ID
        JOIN SHOP s ON b.Shop_ID=s.Shop_ID
        JOIN BILL_ITEM bi ON b.Bill_ID=bi.Bill_ID
        JOIN ITEM i ON bi.Item_ID=i.Item_ID
        WHERE b.Bill_ID=503""",
        "10. Total Spending per Customer": """
        SELECT c.Name, SUM(b.Final_Amount) AS Total_Spent
        FROM CUSTOMER c JOIN BILL b ON c.Customer_ID=b.Customer_ID
        GROUP BY c.Customer_ID ORDER BY Total_Spent DESC""",
        "11. Revenue Generated by Each Shop": """
        SELECT s.Shop_Name, SUM(b.Final_Amount) AS Total_Revenue
        FROM SHOP s JOIN BILL b ON s.Shop_ID=b.Shop_ID
        GROUP BY s.Shop_ID ORDER BY Total_Revenue DESC""",
        "12. Most Sold Items (By Quantity)": """
        SELECT i.Item_Name, SUM(bi.Quantity) AS Total_Sold
        FROM ITEM i JOIN BILL_ITEM bi ON i.Item_ID=bi.Item_ID
        GROUP BY i.Item_ID ORDER BY Total_Sold DESC""",
        "13. Number of Bills Handled by Each Employee": """
        SELECT e.Employee_Name, COUNT(b.Bill_ID) AS Bills_Handled
        FROM EMPLOYEE e JOIN BILL b ON e.SSN=b.SSN
        GROUP BY e.Employee_ID ORDER BY Bills_Handled DESC""",
        "14. Total Parking Revenue": """
        SELECT SUM(Parking_Fee) AS Total_Parking_Revenue FROM PARKING_RECORD""",
        "15. Highest Spending Customer": """
        SELECT c.Name, SUM(b.Final_Amount) AS Total_Spent
        FROM CUSTOMER c JOIN BILL b ON c.Customer_ID=b.Customer_ID
        GROUP BY c.Customer_ID ORDER BY Total_Spent DESC LIMIT 1""",
    }

    def _build_queries(self, parent):
        self._page_header(parent, "SQL Queries", "Run saved or custom SELECT queries", ACCENT3)
        body = tk.Frame(parent, bg=BG)
        body.pack(fill="both", expand=True, padx=24)
        left = tk.Frame(body, bg=CARD, width=220, padx=10, pady=10)
        left.pack(side="left", fill="y", padx=(0,12))
        left.pack_propagate(False)
        tk.Label(left, text="Saved Queries", bg=CARD, fg=ACCENT,
                 font=FONT_B).pack(anchor="w", pady=(0,8))
        for name in self.SAVED:
            b = tk.Button(left, text=name, anchor="w", wraplength=190,
                          justify="left",
                          command=lambda n=name: self._run_saved(n),
                          bg=CARD, fg=TEXT, font=("Segoe UI",9),
                          relief="flat", bd=0, padx=6, pady=5, cursor="hand2",
                          activebackground=HDR_BG, activeforeground=ACCENT)
            b.pack(fill="x", pady=1)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Custom SQL (SELECT only)",
                 bg=BG, fg=SUBTEXT, font=FONT).pack(anchor="w", pady=(0,4))
        self.sql_editor = scrolledtext.ScrolledText(
            right, height=5, bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT, font=FONT_MONO, relief="flat")
        self.sql_editor.pack(fill="x", pady=(0,6))
        btn_row = tk.Frame(right, bg=BG); btn_row.pack(fill="x", pady=4)
        b_run = tk.Button(btn_row, text="▶  Run Query", command=self._run_custom)
        style_button(b_run); b_run.pack(side="left", padx=(0,8))
        b_clr = tk.Button(btn_row, text="Clear",
                          command=lambda: self.sql_editor.delete("1.0","end"))
        style_button(b_clr, color=ENTRY_BG, fg=TEXT, hover=HDR_BG)
        b_clr.pack(side="left")
        self.query_status = tk.Label(right, text="", bg=BG, fg=SUBTEXT, font=FONT)
        self.query_status.pack(anchor="w", pady=2)
        self.result_frame = tk.Frame(right, bg=BG)
        self.result_frame.pack(fill="both", expand=True)

    def _run_saved(self, name):
        sql = self.SAVED[name]
        self.sql_editor.delete("1.0","end")
        self.sql_editor.insert("1.0", sql.strip())
        self._run_custom()

    def _run_custom(self):
        sql = self.sql_editor.get("1.0","end").strip()
        if not sql: return
        if not sql.upper().startswith("SELECT"):
            self.query_status.config(text="Only SELECT queries allowed", fg=DANGER)
            return
        for w in self.result_frame.winfo_children():
            w.destroy()
        try:
            hdrs, rows = fetch(sql)
            self.query_status.config(
                text=f"  {len(rows)} row(s) returned", fg=SUCCESS)
            tree = make_tree(self.result_frame, hdrs, height=16)
            load_tree(tree, rows)
        except Error as e:
            self.query_status.config(text=str(e), fg=DANGER)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()