import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpinBox, QTextEdit
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont

#klasa rura
class Rura:
    def __init__(self, punkty, grubosc=10):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = QColor(100, 100, 100)
        self.kolor_cieczy = QColor(0, 120, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, stan, kolor_cieczy=None):
        self.czy_plynie = stan
        if kolor_cieczy:
            self.kolor_cieczy = kolor_cieczy

    def draw(self, painter):
        if len(self.punkty) < 2: return
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]: path.lineTo(p)

        #rysowanie rury
        painter.setPen(QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        #rysowanie cieczy
        if self.czy_plynie:
            painter.setPen(QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)

#klasa pompa
class Pompa:
    def __init__(self, x, y, nazwa=""):
        self.x = x
        self.y = y
        self.nazwa = nazwa
        self.r = 15
        self.aktywna = False

    def draw(self, painter):

        kolor = QColor(50, 200, 50) if self.aktywna else QColor(200, 50, 50)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(kolor)
        painter.drawEllipse(int(self.x - self.r), int(self.y - self.r), self.r * 2, self.r * 2)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(int(self.x - 5), int(self.y + 4), "P")


class Zbiornik:
    def __init__(self, x, y, w=80, h=100, nazwa="", pokarz_termometr=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.temperatura = 20.0
        self.pokarz_termometr = pokarz_termometr
        self.kolor_cieczy = QColor(0, 120, 255, 200)

    def poziom(self):
        return self.aktualna_ilosc / self.pojemnosc

    def dodaj(self, ilosc, kolor=None, temp_dodawana=None):
        wolne = self.pojemnosc - self.aktualna_ilosc
        realnie_dodano = min(ilosc, wolne)

        #obliczanie nowej temperatury - srednia
        if temp_dodawana is not None and self.aktualna_ilosc > 0:
            masa_calkowita = self.aktualna_ilosc + realnie_dodano
            temp_nowa = (self.temperatura * self.aktualna_ilosc + temp_dodawana * realnie_dodano) / masa_calkowita
            self.temperatura = temp_nowa
        elif temp_dodawana is not None:
            self.temperatura = temp_dodawana

        self.aktualna_ilosc += realnie_dodano
        return realnie_dodano

    def usun(self, ilosc):
        realnie_usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= realnie_usunieto
        return realnie_usunieto

    def pt_dol(self):
        return (self.x + self.w / 2, self.y + self.h)

    def pt_gora(self):
        return (self.x + self.w / 2, self.y)

    def draw(self, painter):
        #rysowanie cieczy
        h_cieczy = self.h * self.poziom()
        if h_cieczy > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.kolor_cieczy)
            painter.drawRect(int(self.x + 2), int(self.y + self.h - h_cieczy), int(self.w - 4), int(h_cieczy))

        #obrys zbiornika
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.w), int(self.h))

        #nazwa
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

        #temperatura
        temp_text = f"{self.temperatura:.1f} °C"
        painter.setPen(QColor(255, 80, 80))


        font_temp = QFont("Arial", 12, QFont.Bold)
        painter.setFont(font_temp)

        fm = painter.fontMetrics()
        szer_txt = fm.width(temp_text)
        painter.drawText(int(self.x + self.w + 30 - szer_txt), int(self.y - 8), temp_text)

        #Procent wypełnienia
        proc_text = f"{int(self.poziom() * 100)}%"

        #tlo pod napisem
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 150))
        bg_rect = QRectF(self.x + 10, self.y + self.h / 2 - 15, self.w - 20, 30)
        painter.drawRoundedRect(bg_rect, 5, 5)

        #napis procentowy
        painter.setPen(QColor(255, 255, 0))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(bg_rect, Qt.AlignCenter, proc_text)

        #termometr
        if self.pokarz_termometr:
            bar_x = self.x + self.w + 8
            bar_w = 12
            painter.setPen(Qt.gray)
            painter.setBrush(Qt.black)
            painter.drawRect(int(bar_x), int(self.y), bar_w, int(self.h))
#kolorowy termoometr
            proc_temp = min(self.temperatura / 100.0, 1.0)
            h_temp = self.h * proc_temp
            c_red = int(255 * proc_temp)
            c_blue = int(255 * (1 - proc_temp))
            painter.setBrush(QColor(c_red, 0, c_blue))
            painter.drawRect(int(bar_x + 1), int(self.y + self.h - h_temp), bar_w - 2, int(h_temp))


class operator (QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mieszadło")
        self.setFixedSize(950, 600)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")

        #zbiornikk
        self.zb1 = Zbiornik(50, 80, nazwa="Składnik nr.1")
        self.zb1.aktualna_ilosc = 100

        self.zb2 = Zbiornik(650, 80, nazwa="Składnik nr.2")
        self.zb2.aktualna_ilosc = 100

        self.zb_mix = Zbiornik(300, 250, w=200, h=150, nazwa="Mieszadło", pokarz_termometr=True)
        self.zb_prod = Zbiornik(300, 480, w=200, h=80, nazwa="Produkt koncowy")

        self.zbiorniki = [self.zb1, self.zb2, self.zb_mix, self.zb_prod]

        #pompy
        self.pompa1 = Pompa(180, 210, "P1")
        self.pompa2 = Pompa(600, 210, "P2")
        self.pompa3 = Pompa(400, 430, "P3")
        self.pompy = [self.pompa1, self.pompa2, self.pompa3]

        #rury
        p1 = self.zb1.pt_dol()
        self.rura1 = Rura([p1, (p1[0], 210), (320, 210), (320, 250)])

        p2 = self.zb2.pt_dol()
        self.rura2 = Rura([p2, (p2[0], 210), (480, 210), (480, 250)])

        p_mix = self.zb_mix.pt_dol()
        p_prod = self.zb_prod.pt_gora()
        self.rura3 = Rura([p_mix, p_prod], grubosc=14)

        self.rury = [self.rura1, self.rura2, self.rura3]

        #wyglad
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_procesu)

        #start
        self.btn = QPushButton("START", self)
        self.btn.setGeometry(20, 500, 150, 40)
        self.btn.setStyleSheet("background-color: #444; border: 1px solid gray; font-weight: bold; font-size: 14px;")
        self.btn.clicked.connect(self.start_symulacji)

        #reset
        self.btn_reset = QPushButton("RESET", self)
        self.btn_reset.setGeometry(180, 500, 100, 40)
        self.btn_reset.setStyleSheet(
            "background-color: #800000; border: 1px solid gray; font-weight: bold; font-size: 14px;")
        self.btn_reset.clicked.connect(self.reset_symulacji)

        #oproznij
        self.btn_oproznij = QPushButton("OPRÓŻNIJ", self)
        self.btn_oproznij.setGeometry(180, 550, 100, 40)
        self.btn_oproznij.setStyleSheet(
            "background-color: #555500; border: 1px solid gray; font-weight: bold; font-size: 14px;")
        self.btn_oproznij.clicked.connect(self.oproznij_produkt)


        style_box = "color: black; background: white; border-radius: 3px; padding: 2px;"

        #ciecz 1
        self.lbl_t1 = QLabel("Temp A:", self);
        self.lbl_t1.move(50, 40)
        self.spin_tempA = QSpinBox(self);
        self.spin_tempA.setGeometry(110, 35, 60, 25)
        self.spin_tempA.setRange(0, 100);
        self.spin_tempA.setValue(20)
        self.spin_tempA.setStyleSheet(style_box)

        #ciecz 2
        self.lbl_t2 = QLabel("Temp B:", self);
        self.lbl_t2.move(650, 40)
        self.spin_tempB = QSpinBox(self);
        self.spin_tempB.setGeometry(710, 35, 60, 25)
        self.spin_tempB.setRange(0, 100);
        self.spin_tempB.setValue(40)
        self.spin_tempB.setStyleSheet(style_box)

        #pozadana temp
        self.lbl_cel = QLabel("Temp Cel:", self);
        self.lbl_cel.move(340, 20)
        self.spin_cel = QSpinBox(self);
        self.spin_cel.setGeometry(420, 15, 60, 25)
        self.spin_cel.setRange(20, 100);
        self.spin_cel.setValue(80)
        self.spin_cel.setStyleSheet(style_box)

        #log
        self.lbl_log = QLabel("Log systemowy:", self)
        self.lbl_log.setGeometry(600, 250, 150, 20)

        self.pole_logu = QTextEdit(self)
        self.pole_logu.setGeometry(600, 275, 300, 250)
        self.pole_logu.setReadOnly(True)
        self.pole_logu.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 11px; border: 1px solid gray;")

        self.dodaj_log("System gotowy. Ustaw temperatury.")

        self.faza = 0
        self.zadana_temperatura = 0.0

    #obsluga oproznij
    def oproznij_produkt(self):
        if self.zb_prod.aktualna_ilosc > 0:
            self.zb_prod.aktualna_ilosc = 0.0
            self.dodaj_log("Opróżniono zbiornik końcowy.")
            self.update()
        else:
            self.dodaj_log("Zbiornik końcowy jest pusty.")

    def dodaj_log(self, tresc):
        godzina = datetime.datetime.now().strftime("%H:%M:%S")
        wpis = f"[{godzina}] {tresc}"
        self.pole_logu.append(wpis)
        scrollbar = self.pole_logu.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def reset_symulacji(self):
        self.timer.stop()
        self.faza = 0

        #reset wszystkiego
        self.zb1.aktualna_ilosc = 100.0
        self.zb2.aktualna_ilosc = 100.0
        self.zb_mix.aktualna_ilosc = 0.0
        self.zb_mix.temperatura = 20.0
        self.zb_prod.aktualna_ilosc = 0.0
        self.zb_prod.temperatura = 20.0

        for p in self.pompy: p.aktywna = False
        for r in self.rury: r.ustaw_przeplyw(False)

        self.pole_logu.clear()
        self.dodaj_log("RESET SYSTEMU")
        self.update()

    def start_symulacji(self):
        if self.faza == 0:
            t1 = self.spin_tempA.value()
            t2 = self.spin_tempB.value()
            self.zadana_temperatura = float(self.spin_cel.value())

            self.zb1.temperatura = t1
            self.zb2.temperatura = t2

            self.dodaj_log(f"START. Cel nagrzewania: {int(self.zadana_temperatura)}°C")
            self.faza = 1
            self.timer.start(30)

    def logika_procesu(self):
        #nalewanie
        if self.faza == 1:
            akcja = False
            if self.zb1.aktualna_ilosc > 0 and self.zb_mix.poziom() < 0.9:
                ilosc = self.zb1.usun(0.5)
                self.zb_mix.dodaj(ilosc, temp_dodawana=self.zb1.temperatura)
                if not self.pompa1.aktywna:
                    self.pompa1.aktywna = True
                    self.rura1.ustaw_przeplyw(True)
                akcja = True
            else:
                self.pompa1.aktywna = False
                self.rura1.ustaw_przeplyw(False)
            if self.zb2.aktualna_ilosc > 0 and self.zb_mix.poziom() < 0.9:
                ilosc = self.zb2.usun(0.5)
                self.zb_mix.dodaj(ilosc, temp_dodawana=self.zb2.temperatura)
                if not self.pompa2.aktywna:
                    self.pompa2.aktywna = True
                    self.rura2.ustaw_przeplyw(True)
                akcja = True
            else:
                self.pompa2.aktywna = False
                self.rura2.ustaw_przeplyw(False)

            if (not akcja or self.zb_mix.poziom() >= 0.9) and self.zb_mix.poziom() > 0.1:
                self.faza = 2
                self.dodaj_log(f"Wymieszano. Temp: {self.zb_mix.temperatura:.1f}°C")
                self.dodaj_log(f"Grzanie do: {self.zadana_temperatura}°C")

        #otrzymywaniei temp
        elif self.faza == 2:
            obecna = self.zb_mix.temperatura
            cel = self.zadana_temperatura
            margin = 0.5

            if abs(obecna - cel) <= margin:
                self.zb_mix.temperatura = cel
                self.faza = 3
                self.dodaj_log(f"Cel osiągnięty! ({obecna:.1f}°C).")
                self.dodaj_log("Spuszczanie produktu.")

            elif obecna < cel:
                self.zb_mix.temperatura += 0.3
            elif obecna > cel:
                self.zb_mix.temperatura -= 0.3


        #wylewanie
        elif self.faza == 3:
            if self.zb_mix.aktualna_ilosc > 0 and self.zb_prod.poziom() < 1.0:
                ilosc = self.zb_mix.usun(0.7)
                self.zb_prod.dodaj(ilosc, temp_dodawana=self.zb_mix.temperatura)
                if not self.pompa3.aktywna:
                    self.pompa3.aktywna = True
                    self.rura3.ustaw_przeplyw(True)
            else:
                self.pompa3.aktywna = False
                self.rura3.ustaw_przeplyw(False)
                self.faza = 0
                self.timer.stop()
                self.dodaj_log("Cykl zakończony.")

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for r in self.rury: r.draw(painter)
        for z in self.zbiorniki: z.draw(painter)
        for p in self.pompy: p.draw(painter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = operator()
    window.show()
    sys.exit(app.exec())