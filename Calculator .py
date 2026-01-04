import tkinter as tk
from tkinter import messagebox, colorchooser
import math
from datetime import datetime

def safe_eval(expr):
    """
    ارزیابی ایمن عبارات ریاضی.
    فقط به نام‌های مجاز دسترسی دارد تا از اجرای کد ناامن جلوگیری شود.
    """
    if expr is None:
        raise ValueError("عبارت نامعتبر است.")
    expr = expr.strip()
    if not expr:
        raise ValueError("عبارت خالی است.")
    # نام‌های مجاز
    allowed_names = {
        # اعداد و ثابت‌ها
        "pi": math.pi,
        "e": math.e,
        # توابع پایه
        "abs": abs,
        "round": round,
        # از math هرآنچه مفید و بی‌خطر است
        "ceil": math.ceil,
        "floor": math.floor,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pow": pow,
        # اگر کاربر خودش sin(...) بنویسد با رادیان محاسبه می‌شود
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "degrees": math.degrees,
        "radians": math.radians,
    }
    try:
        return eval(expr, {"__builtins__": {}}, allowed_names)
    except ZeroDivisionError:
        raise
    except Exception as e:
        # پیام خواناتر
        raise ValueError(f"عبارت نامعتبر: {e}")

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ماشین حساب پیشرفته")
        self.geometry("420x580")
        self.expression = ""
        self.history = []
        self.widgets = []

        # منو
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="تغییر رنگ پس‌زمینه", command=self.change_background)
        settings_menu.add_separator()
        settings_menu.add_command(label="خروج", command=self.quit)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="درباره ما", command=self.show_about)

        menubar.add_cascade(label="تنظیمات", menu=settings_menu)
        menubar.add_cascade(label="راهنما", menu=about_menu)

        # نمایشگر
        display_frame = tk.Frame(self)
        display_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        self.widgets.append(display_frame)

        self.display = tk.Entry(display_frame, font=("Arial", 18), justify="right")
        self.display.pack(fill=tk.BOTH, ipady=10)
        self.widgets.append(self.display)

        # نکته راهنما
        hint = tk.Label(
            display_frame,
            text="راهنما: با کیبورد هم می‌تونی تایپ کنی. Enter = مساوی، Backspace = حذف، Esc = پاک‌کردن.",
            anchor="e",
            fg="#666"
        )
        hint.pack(fill=tk.X, pady=(4, 0))
        self.widgets.append(hint)

        # بارگذاری آیکون‌ها
        self.load_images()

        # ساخت دکمه‌ها
        self.create_buttons()

        # میانبرهای کیبورد
        self.bind_all("<Key>", self.key_input)
        self.bind_all("<Return>", lambda e: self.handle_button('='))
        self.bind_all("<KP_Enter>", lambda e: self.handle_button('='))
        self.bind_all("<BackSpace>", self.backspace)
        self.bind_all("<Escape>", lambda e: self.clear_all())

    def load_images(self):
        """
        تلاش برای بارگذاری آیکون‌ها. اگر فایلی نبود، جایگزین None می‌شود
        تا از ارور جلوگیری شود و متن دکمه نمایش داده شود.
        """
        self.images = {}
        icon_names = [
            '7', '8', '9', '/', 'sin',
            '4', '5', '6', '*', 'cos',
            '1', '2', '3', '-', 'tan',
            '0', '.', '=', '+', 'sqrt',
            '(', ')', 'log', '^', 'clear',
            'history', 'algorithm'
        ]
        for name in icon_names:
            try:
                self.images[name] = tk.PhotoImage(file=f"icons/{name}.png")
            except Exception:
                self.images[name] = None  # جایگزین متنی استفاده خواهد شد

    def create_buttons(self):
        # چیدمان دکمه‌ها
        buttons = [
            ('7', '8', '9', '/', 'sin'),
            ('4', '5', '6', '*', 'cos'),
            ('1', '2', '3', '-', 'tan'),
            ('0', '.', '=', '+', 'sqrt'),
            ('(', ')', 'log', '^', 'clear'),
            ('history', 'algorithm')
        ]

        for row in buttons:
            frame = tk.Frame(self)
            frame.pack(expand=True, fill="both")
            self.widgets.append(frame)
            for btn in row:
                # اگر آیکون بود، نمایش با تصویر؛ در غیراینصورت متن
                if self.images.get(btn):
                    b = tk.Button(frame, image=self.images[btn], command=lambda x=btn: self.handle_button(x))
                else:
                    # متن دکمه به فارسیِ قابل فهم‌تر برای برخی کلیدها
                    text_map = {
                        '/': '÷', '*': '×', '-': '−', '+': '+',
                        'sqrt': '√', 'clear': 'پاک',
                        'history': 'تاریخچه', 'algorithm': 'الگوریتم'
                    }
                    b = tk.Button(frame, text=text_map.get(btn, btn), font=("Arial", 12),
                                  command=lambda x=btn: self.handle_button(x))
                b.pack(side="left", expand=True, fill="both")
                self.widgets.append(b)

    def handle_button(self, btn):
        try:
            if btn.isdigit() or btn in ('.', '(', ')'):
                self.expression += btn

            elif btn in ('+', '-', '*', '/'):
                # جلوگیری از دو عملگر پیاپی
                if self.expression and self.expression[-1] in '+-*/':
                    self.expression = self.expression[:-1] + btn
                else:
                    self.expression += btn

            elif btn == '^':
                # تبدیل به توان پایتونی
                if self.expression and self.expression[-1] == '^':
                    pass
                else:
                    self.expression += '**'

            elif btn == 'clear':
                self.clear_all()

            elif btn == '=':
                if not self.expression.strip():
                    return
                result = safe_eval(self.expression)
                if isinstance(result, float):
                    # گرد کردن ملایم برای جلوگیری از نویز اعشاری
                    result = round(result, 10)
                self.history.append(f"{datetime.now().strftime('%H:%M:%S')} | {self.expression} = {result}")
                self.expression = str(result)

            elif btn in ('sin', 'cos', 'tan'):
                self._apply_trig(btn)

            elif btn == 'sqrt':
                if not self.expression.strip():
                    raise ValueError("لطفاً عدد وارد کنید.")
                value = safe_eval(self.expression)
                if value < 0:
                    raise ValueError("ریشه دوم عدد منفی تعریف نشده است.")
                self.expression = str(round(math.sqrt(value), 10))

            elif btn == 'log':
                if not self.expression.strip():
                    raise ValueError("لطفاً عدد وارد کنید.")
                value = safe_eval(self.expression)
                if value <= 0:
                    raise ValueError("ورودی لوگاریتم باید بزرگ‌تر از صفر باشد.")
                self.expression = str(round(math.log10(value), 10))

            elif btn == 'history':
                history_text = "\n".join(self.history[-10:])
                messagebox.showinfo("تاریخچه", history_text if history_text else "هیچ محاسبه‌ای وجود ندارد.")

            elif btn == 'algorithm':
                self.show_algorithm()

            self._refresh_display(self.expression)

        except ZeroDivisionError:
            self._show_error("تقسیم بر صفر مجاز نیست.")
        except Exception as e:
            self._show_error(str(e))

    def _apply_trig(self, func_name):
        # تریگونومتری بر حسب درجه
        if not self.expression.strip():
            raise ValueError("لطفاً عدد وارد کنید.")
        value = safe_eval(self.expression)
        func = getattr(math, func_name)
        self.expression = str(round(func(math.radians(value)), 10))

    def _refresh_display(self, text):
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, text)

    def _show_error(self, msg):
        self._refresh_display(f"خطا: {msg}")
        # پس از نمایش خطا، عبارت را پاک می‌کنیم تا آماده ورودی جدید باشد
        self.expression = ""

    def clear_all(self):
        self.expression = ""
        self._refresh_display("")

    # کیبورد
    def key_input(self, event):
        ch = event.char
        if ch in "0123456789.+-*/()":
            self.expression += ch
            self._refresh_display(self.expression)
        elif ch == "^":
            self.expression += "**"
            self._refresh_display(self.expression)
        elif ch == "\r":
            self.handle_button("=")

    def backspace(self, event):
        if self.expression:
            self.expression = self.expression[:-1]
            self._refresh_display(self.expression)

    def change_background(self):
        color = colorchooser.askcolor(title="انتخاب رنگ پس‌زمینه")
        if color and color[1]:
            for widget in self.widgets:
                try:
                    widget.configure(bg=color[1])
                except Exception:
                    pass
            try:
                self.configure(bg=color[1])
            except Exception:
                pass

    def show_about(self):
        messagebox.showinfo(
            "درباره ما",
            "ماشین حساب پیشرفته نسخه 1 \n"
            "ساخته شده توسط sepehr-tech \n"
            "امکانات: دکمه‌های تصویری (با جایگزین متنی در صورت نبود آیکون)، محاسبات علمی، تاریخچه، تغییر رنگ کامل بک‌گراند، دکمه الگوریتم، پشتیبانی از کیبورد"
        )

    def show_algorithm(self):
        messagebox.showinfo(
            "الگوریتم چیست؟",
            "الگوریتم مجموعه‌ای از دستورالعمل‌های مرحله‌به‌مرحله برای حل یک مسئله است.\n"
            "مثال: پیدا کردن عدد بزرگ‌تر بین دو عدد:\n"
            "1. دو عدد را بگیر\n"
            "2. اگر اولی بزرگ‌تر بود → نمایش عدد اول\n"
            "3. وگرنه → نمایش عدد دوم"
        )

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()