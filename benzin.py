import os
import sys
import tkinter.font
from datetime import date
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *

from scrollframe import ScrollFrame

curyear = date.today().year
startfiledir = '.'
pad = 5
rows = 0
listrows = []
root = Tk()
root.title('Benzin')
popup = None
ent = None
chbutval = 0
gridwin = None
calendar = {
    '01': 31,
    '02': 29,
    '03': 31,
    '04': 30,
    '05': 31,
    '06': 30,
    '07': 31,
    '08': 31,
    '09': 30,
    '10': 31,
    '11': 30,
    '12': 31,
}
tfont = tkinter.font.Font(
    family='Times New Roman', size=20, slant='italic', weight='bold'
)
helptext = """Benzin - это программа для рассчета расхода бензина 
на основании предыдущих заправок и пробега.
Выберите файл c данными для рассчета 
или введите данные вручную 
для сохранения их в файл и последующего рассчета.
Даты вводятся в формате ДД/ММ/ГГГГ"""


class MyButton(Button):
    def __init__(self, parent=None, **config):
        Button.__init__(self, parent, **config)
        bfont = tkinter.font.Font(family='Times New Roman', size=20)
        self.config(
            font=bfont,
            bg='beige',
            activebackground='black',
            activeforeground='white',
            bd=5,
            cursor='hand2',
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        self.config(bg='orange')

    def on_leave(self, event):
        self.config(bg='beige')


class LabeledCheckbutton(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.checkbutton = Checkbutton(self)
        self.label = Label(self)
        self.label.grid(row=0, column=0)
        self.checkbutton.grid(row=0, column=1)


class Benzcounter:
    def __init__(self, file=None):
        self.ifile = file
        self.set_file_name(None)
        self.openDialog = None
        self.saveDialog = None
        self.totalfuel = 0
        self.date = 0
        self.data = []
        self.db = {}
        self.probeg = 0
        self.fuelcost = 0
        self.gui_builder()

    def gui_builder(self):
        global ent
        global chbutval
        win1 = Frame(root, padx=pad, pady=pad)
        win1.pack(side=BOTTOM)
        win2 = Frame(root, padx=pad, pady=pad)
        win2.pack(side=TOP)
        win4 = Frame(root, padx=pad, pady=pad)
        win4.pack(side=TOP)
        win3 = Frame(root, padx=pad, pady=pad)
        win3.pack(side=TOP)
        Label(
            win2,
            text='Выберите файл для рассчета\n или введите данные вручную',
            pady=30,
            font=tfont,
        ).pack()
        MyButton(win2, text='Открыть файл', command=self.on_open).pack(
            side=LEFT, padx=pad, pady=pad
        )
        MyButton(
            win2,
            text='Ввести вручную',
            command=lambda: [self.manual_input(), self.add_row()],
        ).pack(side=RIGHT, padx=pad, pady=pad)
        MyButton(win1, text='Выход', command=root.quit).pack(
            side=RIGHT, padx=pad, pady=pad
        )
        MyButton(win1, text='?', command=on_help).pack(
            side=LEFT, padx=pad, pady=pad
        )
        Label(
            win4, font=14, text='Цена одного литра бензина\n(опционально)'
        ).pack(side=LEFT)
        ent = Entry(win4, width=10, bd=4, font=14)
        ent.pack(side=RIGHT)
        chbut = LabeledCheckbutton(win3)
        chbutval = IntVar()
        chbut.checkbutton.config(variable=chbutval, cursor='hand2', padx=pad)
        chbut.label.config(text='Отображать расход бензина\nна 100км', font=14)
        chbut.pack(side=TOP, pady=pad)
        MyButton(win3, text='Рассчитать', command=self.printer).pack(
            side=TOP, pady=pad
        )
        MyButton(win3, text='Редактировать', command=self.on_edit).pack(
            side=BOTTOM, pady=pad
        )

    def my_askopenfilename(self):
        if not self.openDialog:
            self.openDialog = Open(initialdir=startfiledir)
        return self.openDialog.show()

    def my_asksaveasfilename(self):
        if not self.saveDialog:
            self.saveDialog = SaveAs(initialdir=startfiledir)
        return self.saveDialog.show()

    def get_file_name(self):
        return self.ifile

    def set_file_name(self, name):
        self.ifile = name

    def on_open(self):
        file = self.my_askopenfilename()
        if not file:
            return
        if not os.path.isfile(file):
            showerror('Benzin', 'Невозможно открыть файл ' + file)
            return
        self.set_file_name(file)

    def manual_input(self):
        root.withdraw()
        global listrows
        listrows = []
        global popup
        global gridwin
        popup = Toplevel(root)
        popup.iconbitmap(default=resource_path('icon.ico'))
        popup.resizable(width=False, height=True)
        popup.lift()
        popup.focus_force()
        win1 = Frame(popup, padx=pad, pady=pad)
        win1.pack(side=BOTTOM)
        canv = Canvas(popup, bd=0, width=600, height=150)
        canv.pack(side=TOP)
        win2 = Frame(canv)
        canv.create_window((0, 0), window=win2, anchor=NW)
        gridwin = ScrollFrame(popup)
        gridwin.pack(fill=BOTH, expand=True)
        MyButton(win1, text='Готово', command=self.on_done).pack(
            side=RIGHT, padx=pad, pady=pad
        )
        MyButton(win1, text='Добавить', command=self.add_row).pack(
            side=LEFT, padx=pad, pady=pad
        )
        Label(
            win2,
            font=tfont,
            text='Ведите данные о предыдущих заправках',
            pady=30,
        ).grid(column=0, row=0, columnspan=4)
        Label(win2, text='Дата заправки', font=14, width=18).grid(
            column=0, row=1
        )
        Label(win2, text='Количество литров', font=14, width=18).grid(
            column=1, row=1
        )
        Label(win2, text='Пробег\nна дату заправки', font=14, width=18).grid(
            column=2, row=1
        )
        delbut = MyButton(
            win2,
            text='Удалить\nстроку(-и)',
            command=remove_row,
            font=('Times New Roman',),
        )
        delbut.grid(column=3, row=1)
        delbut.config(
            bg='beige', activebackground='red', bd=3, cursor='hand2', font=14
        )
        popup.protocol(
            'WM_DELETE_WINDOW', lambda: [root.deiconify(), popup.destroy()]
        )

    def add_row(self):
        global rows
        gridrow = []
        e1 = Entry(gridwin.viewPort, width=25, bd=4)
        gridrow.append(e1)
        e1.grid(column=0, row=rows + 1, padx=pad)
        e1.focus_set()
        e2 = Entry(gridwin.viewPort, width=25, bd=4)
        gridrow.append(e2)
        e2.grid(column=1, row=rows + 1, padx=pad)
        e3 = Entry(gridwin.viewPort, width=25, bd=4)
        gridrow.append(e3)
        e3.grid(column=2, row=rows + 1, padx=pad)
        var = IntVar()
        cbut = Checkbutton(gridwin.viewPort, variable=var, cursor='hand2')
        cbut.val = var
        gridrow.append(cbut)
        cbut.grid(column=3, row=rows + 1, padx=30)
        listrows.append(gridrow)
        rows += 1

    def on_done(self):
        emp = False
        nonint = False
        baddate = False
        result = []
        self.data = []
        if not listrows:
            showerror('Ошибка', 'Нет данных для сохранения', parent=popup)
            return
        for gridrow in listrows:
            for item in gridrow[:1]:
                val = item.get()
                if not val:
                    emp = True
                val = val.replace('.', '/')
                val = val.replace(',', '/')
                if len(val) != 10:
                    baddate = True
                for i in val.split('/'):
                    if not i.isnumeric():
                        nonint = True
                d = val[:2]
                m = val[3:5]
                y = val[6:]
                try:
                    day = int(d)
                    month = int(m)
                    year = int(y)
                    if 1900 > year or year > curyear or day < 1 or month < 1:
                        baddate = True
                    if m in calendar:
                        if calendar[m] < day:
                            baddate = True
                    else:
                        baddate = True
                except ValueError:
                    baddate = True
                val = y + '/' + m + '/' + d
                result.append(val)
            for item in gridrow[1:2]:
                val = item.get()
                val = val.replace(',', '.')
                if not val:
                    emp = True
                if not val.replace('.', '', 1).isnumeric():
                    nonint = True
                result.append(val)
            for item in gridrow[2:3]:
                val = item.get()
                if not val:
                    emp = True
                if not val.isnumeric():
                    nonint = True
                result.append(val)
            if emp:
                showerror('Ошибка', 'Заполнены не все поля', parent=popup)
                return
            if nonint:
                showerror(
                    'Ошибка', 'Введены некорректные данные', parent=popup
                )
                return
            if baddate:
                showerror('Ошибка', 'Дата указана неверно', parent=popup)
                return
            self.data.append(result)
            self.data.sort()
            result = []
        prevprobeg = None
        for alist in self.data:
            if not prevprobeg:
                prevprobeg = 0
            lastprobeg = int(alist[2])
            if lastprobeg < prevprobeg:
                showerror(
                    'Ошибка',
                    'Пробег не может быть меньше предыдущего',
                    parent=popup,
                )
                self.data.pop(self.data.index(alist))
                return
            prevprobeg = lastprobeg
        self.on_save_as()

    def on_save_as(self):
        results = []
        strings = ''
        filename = self.my_asksaveasfilename()
        if not filename:
            return
        ofile = open(filename, 'w')
        for alist in self.data:
            results.append('==>'.join(alist))
            strings = '\n'.join(results)
        ofile.write(strings)
        ofile.close()
        self.set_file_name(filename)
        self.data = []
        popup.destroy()
        root.deiconify()

    def on_edit(self):
        ifile = self.get_file_name()
        if not ifile:
            showerror('Ошибка', 'Файл не выбран')
            return
        ifile = open(ifile)
        self.manual_input()
        for line in ifile.readlines():
            global rows
            gridrow = []
            e1 = Entry(gridwin.viewPort, width=25, bd=4)
            gridrow.append(e1)
            e1.grid(column=0, row=rows + 1, padx=pad)
            e1.focus_set()
            d = line.split('==>')[0][-2:]
            m = line.split('==>')[0][5:7]
            y = line.split('==>')[0][:4]
            adate = d + '/' + m + '/' + y
            e1.insert(0, adate)
            e2 = Entry(gridwin.viewPort, width=25, bd=4)
            gridrow.append(e2)
            e2.grid(column=1, row=rows + 1, padx=pad)
            e2.insert(0, line.split('==>')[1])
            e3 = Entry(gridwin.viewPort, width=25, bd=4)
            gridrow.append(e3)
            e3.grid(column=2, row=rows + 1, padx=pad)
            e3.insert(0, line.split('==>')[2].rstrip())
            var = IntVar()
            cbut = Checkbutton(gridwin.viewPort, variable=var, cursor='hand2')
            cbut.val = var
            gridrow.append(cbut)
            cbut.grid(column=3, row=rows + 1, padx=30)
            listrows.append(gridrow)
            rows += 1
        ifile.close()

    def counter(self):
        try:
            self.fuelcost = ent.get()
        except AttributeError:
            pass
        ifile = open(self.get_file_name())
        lastprobeg = startprobeg = int(ifile.readline().split('==>')[2])
        ifile.seek(0)
        for line in ifile.readlines():
            self.date = line.split('==>')[0][:8]
            if self.date not in self.db:
                self.totalfuel = 0
                startprobeg = lastprobeg
            lastprobeg = int(line.split('==>')[2])
            fuel = float(line.split('==>')[1])
            self.totalfuel += fuel
            self.probeg = lastprobeg - startprobeg
            self.db[self.date] = (self.totalfuel, self.probeg)
        return self.db

    def printer(self):
        val = chbutval.get()
        l = []
        try:
            self.counter()
            if self.fuelcost and val:
                for key in self.db:
                    text = (
                        'За %s месяц %s года общий расход бензина: %sл, расход'
                        ' на 100км: %sл, пробег: %sкм, затраты: %sр\n'
                    )
                    spent = round(
                        float(self.fuelcost.replace(',', '.', 1))
                        * float(self.db[key][0]),
                        2,
                    )
                    rashod100km = round(
                        (self.db[key][0] / self.db[key][1] * 100), 2
                    )
                    l.append(
                        text
                        % (
                            key.split('/')[1],
                            key.split('/')[0],
                            self.db[key][0],
                            rashod100km,
                            self.db[key][1],
                            spent,
                        )
                    )
                showinfo('Результаты рассчета', '\n'.join(l))
            elif self.fuelcost and not val:
                for key in self.db:
                    text = (
                        'За %s месяц %s года расход бензина: %sл, пробег:'
                        ' %sкм, затраты: %sр\n'
                    )
                    spent = round(
                        float(self.fuelcost.replace(',', '.', 1))
                        * float(self.db[key][0]),
                        2,
                    )
                    l.append(
                        text
                        % (
                            key.split('/')[1],
                            key.split('/')[0],
                            self.db[key][0],
                            self.db[key][1],
                            spent,
                        )
                    )
                showinfo('Результаты рассчета', '\n'.join(l))
            elif val and not self.fuelcost:
                for key in self.db:
                    text = (
                        'За %s месяц %s года общий расход бензина: %sл, расход'
                        ' на 100км: %sл, пробег: %sкм\n'
                    )
                    rashod100km = round(
                        (self.db[key][0] / self.db[key][1] * 100), 2
                    )
                    l.append(
                        text
                        % (
                            key.split('/')[1],
                            key.split('/')[0],
                            self.db[key][0],
                            rashod100km,
                            self.db[key][1],
                        )
                    )
                showinfo('Результаты рассчета', '\n'.join(l))
            else:
                for key in self.db:
                    text = (
                        'За %s месяц %s года расход бензина: %sл, пробег:'
                        ' %sкм\n'
                    )
                    l.append(
                        text
                        % (
                            key.split('/')[1],
                            key.split('/')[0],
                            self.db[key][0],
                            self.db[key][1],
                        )
                    )
                showinfo('Результаты рассчета', '\n'.join(l))
        except (TypeError, FileNotFoundError):
            showerror('Ошибка', 'Не выбран файл для рассчета')
        except (IndexError, UnicodeDecodeError):
            showerror(
                'Ошибка',
                (
                    'Неверный формат файла. Выберите файл созданный программой'
                    ' Benzin'
                ),
            )
        except ValueError:
            showerror('Ошибка', 'Неверно указана цена бензина')
        self.db = {}


def remove_row():
    for rowno, row in reversed(list(enumerate(listrows))):
        if row[3].val.get() == 1:
            for item in row:
                item.destroy()
            listrows.pop(rowno)


def on_help():
    showinfo('О программе Benzin', helptext)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


root.iconbitmap(default=resource_path('icon.ico'))

if __name__ == '__main__':
    Benzcounter()
    mainloop()
