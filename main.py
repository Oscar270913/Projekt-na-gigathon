import random
import math
import sys


# kierunki ruchu - (dx, dy, nazwa)
KIERUNKI = {
    "N": (0, 1, "polnoc"),
    "S": (0, -1, "poludnie"),
    "E": (1, 0, "wschod"),
    "W": (-1, 0, "zachod"),
}

# co można napotkać w terenie i jaki ma efekt na energię
TEREN = {
    "krater":   (-15, "Krater meteorytu - uszkodzenie podwozia"),
    "probka":   (+12, "Probka skalna - cenne mineraly"),
    "stacja":   (+30, "Stacja naprawcza - regeneracja systemow"),
    "burza":    (-20, "Burza pylowa - panele sloneczne zasypane"),
    "tunel":    (-5,  "Tunel lawowy - skrot przez podziemia"),
    "pole_em":  (-25, "Pole elektromagnetyczne - zaklucenia"),
}

# losowe zdarzenia
ZDARZENIA = [
    (+20, "Rozblysk sloneczny! Panele naladowane."),
    (-20, "Deszcz meteorytow! Uszkodzenia oslon termicznych."),
    (+15, "Odkryto podzemny lod! Chlodzenie reaktora poprawione."),
    (-10, "Ekstremalne zimno. Systemy grzewcze przeciazone."),
    (+10, "Sygnal z bazy. Trasa zoptymalizowana."),
    (-15, "Awaria silnika napedowego. Naprawa w toku."),
]


def wczytaj_int(tekst, min_v=None, max_v=None, domyslna=None):
    while True:
        try:
            odp = input(tekst).strip()
            if odp == "" and domyslna is not None:
                return domyslna
            n = int(odp)
            if min_v is not None and n < min_v:
                print(f"Podaj wartosc co najmniej {min_v}.")
                continue
            if max_v is not None and n > max_v:
                print(f"Podaj wartosc co najwyzej {max_v}.")
                continue
            return n
        except ValueError:
            if domyslna is not None:
                print(f"Nieprawidlowa wartosc, przyjmuje {domyslna}.")
                return domyslna
            print("Wpisz liczbe calkowita.")


def wczytaj_str(tekst, domyslna=None):
    odp = input(tekst).strip()
    if not odp and domyslna:
        return domyslna
    return odp if odp else (domyslna or "Nieznany")


def odleglosc(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def pasek_energii(aktualna, max_en):
    ile = int((aktualna / max(1, max_en)) * 20)
    return "[" + "#" * ile + "-" * (20 - ile) + f"] {aktualna}/{max_en}"


class Wyprawa:

    def __init__(self):
        self.nazwa = ""
        self.lazik = ""
        self.x = 0
        self.y = 0
        self.start_x = 0
        self.start_y = 0
        self.energia = 100
        self.energia_start = 100
        self.rozmiar = 15
        self.max_krokow = 50
        self.cel_x = 0
        self.cel_y = 0

        self.krok = 0
        self.probki = 0
        self.stacje = 0
        self.kratery = 0
        self.zdarzenia_losowe = 0

        self.log = []
        self.mapa = {}

        self.koniec_powod = ""
        self.wynik = ""

    def setup(self):
        print("\n=== SYMULATOR WYPRAWY LAZIKA MARSJAŃSKIEGO ===\n")
        print("Twoim zadaniem jest dotrzec lazikiemdo wyznaczonego celu.")
        print("Po drodze mozesz napotykac przeszkody i zdarzenia losowe.")

        self.nazwa = wczytaj_str("Nazwa wyprawy [Misja Ares]: ", "Misja Ares")
        self.lazik = wczytaj_str("Nazwa lazika [Perseverance]: ", "Perseverance")

        print()
        self.rozmiar = wczytaj_int(
            "Rozmiar swiata - polowa boku siatki (np. 15 oznacza X,Y od -15 do 15) [5-30]: ",
            5, 30, 15
        )
        print(f"Swiat: x od {-self.rozmiar} do {self.rozmiar}, y od {-self.rozmiar} do {self.rozmiar}")

        print()
        self.start_x = wczytaj_int(
            f"Pozycja startowa X [{-self.rozmiar}..{self.rozmiar}]: ",
            -self.rozmiar, self.rozmiar, 0
        )
        self.start_y = wczytaj_int(
            f"Pozycja startowa Y [{-self.rozmiar}..{self.rozmiar}]: ",
            -self.rozmiar, self.rozmiar, 0
        )
        self.x = self.start_x
        self.y = self.start_y

        print()
        self.energia_start = wczytaj_int(
            "Energia startowa lazika [20-200]: ",
            20, 200, 100
        )
        self.energia = self.energia_start

        print()
        print("Podaj wspolrzedne celu - lazik musi tam dotrzec.")
        domyslny_cel = self.rozmiar // 2
        self.cel_x = wczytaj_int(
            f"Cel X [{-self.rozmiar}..{self.rozmiar}]: ",
            -self.rozmiar, self.rozmiar, domyslny_cel
        )
        self.cel_y = wczytaj_int(
            f"Cel Y [{-self.rozmiar}..{self.rozmiar}]: ",
            -self.rozmiar, self.rozmiar, domyslny_cel
        )

        if self.cel_x == self.start_x and self.cel_y == self.start_y:
            self.cel_x = min(self.rozmiar, self.start_x + 3)
            self.cel_y = min(self.rozmiar, self.start_y + 3)
            print(f"Cel byl taki sam jak start, przesuwam cel na ({self.cel_x}, {self.cel_y}).")

        print()
        self.max_krokow = wczytaj_int(
            "Maksymalna liczba krokow [10-200]: ",
            10, 200, 50
        )

        self._generuj_mape()

    def _generuj_mape(self):
        self.mapa = {}
        self.mapa[(self.cel_x, self.cel_y)] = "cel"

        typy = ["krater", "probka", "stacja", "burza", "tunel", "pole_em"]
        n = max(8, self.rozmiar * 2)

        for _ in range(n):
            for proba in range(200):
                px = random.randint(-self.rozmiar, self.rozmiar)
                py = random.randint(-self.rozmiar, self.rozmiar)
                if (px, py) not in self.mapa and (px, py) != (self.start_x, self.start_y):
                    self.mapa[(px, py)] = random.choice(typy)
                    break

    def _info_przed_startem(self):
        print("\n--- PARAMETRY WYPRAWY ---")
        print(f"Nazwa:           {self.nazwa}")
        print(f"Lazik:           {self.lazik}")
        print(f"Start:           ({self.start_x}, {self.start_y})")
        print(f"Cel:             ({self.cel_x}, {self.cel_y})")
        print(f"Odleglosc:       {odleglosc(self.start_x, self.start_y, self.cel_x, self.cel_y):.1f}")
        print(f"Energia:         {self.energia_start}")
        print(f"Maks. krokow:    {self.max_krokow}")
        print(f"Granice swiata:  od {-self.rozmiar} do {self.rozmiar} na obu osiach")
        print()
        print("Typy terenu:")
        print("  krater   -15 energii  (uszkodzenie podwozia)")
        print("  probka   +12 energii  (cenne mineraly)")
        print("  stacja   +30 energii  (stacja naprawcza)")
        print("  burza    -20 energii  (burza pylowa)")
        print("  tunel     -5 energii  (skrot, teleportuje blizej celu)")
        print("  pole_em  -25 energii  (pole elektromagnetyczne)")
        print()
        print("Koniec gry gdy:")
        print(f"  - lazik dotrze do celu ({self.cel_x}, {self.cel_y}) - SUKCES")
        print(f"  - energia spadnie do 0 - PORAZKA")
        print(f"  - zostanie wykonanych {self.max_krokow} krokow - PORAZKA")
        print()
        input("Nacisnij Enter zeby zaczac wyprawa...")

    def _kierunek_reczny(self):
        while True:
            k = input("Kierunek (N/S/E/W): ").strip().upper()
            if k in KIERUNKI:
                return k
            print("Wpisz N, S, E lub W.")

    def _teren(self, pos):
        if pos not in self.mapa:
            return

        typ = self.mapa[pos]

        if typ == "cel":
            return

        efekt, opis = TEREN[typ]

        print(f"  >> Napotkano: {typ.upper()} - {opis}")

        if typ == "stacja":
            efekt = min(efekt, self.energia_start - self.energia)
            self.stacje += 1
        elif typ == "krater":
            self.kratery += 1
        elif typ == "probka":
            self.probki += 1
            del self.mapa[pos]
        elif typ == "tunel":
            skok = random.randint(3, 5)
            if self.cel_x > self.x:
                self.x = min(self.rozmiar, self.x + skok)
            elif self.cel_x < self.x:
                self.x = max(-self.rozmiar, self.x - skok)
            if self.cel_y > self.y:
                self.y = min(self.rozmiar, self.y + skok)
            elif self.cel_y < self.y:
                self.y = max(-self.rozmiar, self.y - skok)
            print(f"  >> Tunel wyrzucil lazika na ({self.x}, {self.y})")

        self.energia += efekt
        znak = "+" if efekt >= 0 else ""
        print(f"  >> Energia: {znak}{efekt}")
        self.log.append(f"krok {self.krok}: {typ} na ({self.x},{self.y}) -> {znak}{efekt} energii")

    def _zdarzenie_losowe(self):
        if random.random() > 0.25:
            return

        efekt, opis = random.choice(ZDARZENIA)
        znak = "+" if efekt >= 0 else ""
        print(f"  [ZDARZENIE] {opis} ({znak}{efekt} energii)")
        self.energia += efekt
        self.zdarzenia_losowe += 1
        self.log.append(f"krok {self.krok}: zdarzenie losowe - {opis} ({znak}{efekt})")

    def _krok(self):
        self.krok += 1

        print(f"\n--- Krok {self.krok}/{self.max_krokow} ---")
        print(f"Pozycja: ({self.x}, {self.y})  |  Cel: ({self.cel_x}, {self.cel_y})  |  Odleglosc: {odleglosc(self.x, self.y, self.cel_x, self.cel_y):.1f}")
        print(f"Energia: {pasek_energii(self.energia, self.energia_start)}")

        kierunek = self._kierunek_reczny()

        dx, dy, nazwa_kier = KIERUNKI[kierunek]
        nx = self.x + dx
        ny = self.y + dy

        przy_scianie = False
        if nx < -self.rozmiar or nx > self.rozmiar:
            nx = max(-self.rozmiar, min(self.rozmiar, nx))
            print(f"  >> Granica swiata na osi X! Lazik zatrzymany.")
            przy_scianie = True
        if ny < -self.rozmiar or ny > self.rozmiar:
            ny = max(-self.rozmiar, min(self.rozmiar, ny))
            print(f"  >> Granica swiata na osi Y! Lazik zatrzymany.")
            przy_scianie = True

        koszt = 1 if przy_scianie else 3
        self.energia -= koszt
        self.x = nx
        self.y = ny

        print(f"Ruch: {kierunek} ({nazwa_kier}) -> ({self.x}, {self.y})  (koszt: -{koszt} energii)")

        self._teren((self.x, self.y))
        self._zdarzenie_losowe()

        self.energia = max(0, self.energia)

        print(f"Energia po kroku: {pasek_energii(self.energia, self.energia_start)}")

    def sprawdz_koniec(self):
        if self.x == self.cel_x and self.y == self.cel_y:
            self.koniec_powod = "Lazik dotarl do celu!"
            self.wynik = "sukces_plus" if self.probki >= 3 else "sukces"
            return True

        if self.energia <= 0:
            self.koniec_powod = "Lazik wyczerpał energię i unieruchomil sie."
            self.wynik = "porazka_energia"
            return True

        if self.krok >= self.max_krokow:
            self.koniec_powod = f"Osiagnieto limit {self.max_krokow} krokow."
            d = odleglosc(self.x, self.y, self.cel_x, self.cel_y)
            d0 = odleglosc(self.start_x, self.start_y, self.cel_x, self.cel_y)
            self.wynik = "czesciowy" if d < d0 * 0.3 else "porazka_kroki"
            return True

        return False

    def _oblicz_punkty(self):
        d = odleglosc(self.x, self.y, self.cel_x, self.cel_y)
        d0 = odleglosc(self.start_x, self.start_y, self.cel_x, self.cel_y)
        punkty = 0

        if self.wynik in ("sukces", "sukces_plus"):
            punkty += 1000
            punkty += max(0, (self.max_krokow - self.krok) * 5)
            punkty += self.energia * 2
        elif self.wynik == "czesciowy":
            punkty += 300

        punkty += self.probki * 100
        punkty -= self.kratery * 20
        postep = max(0.0, 1.0 - d / max(1.0, d0))
        punkty += int(postep * 200)

        return max(0, punkty)

    def raport(self):
        d = odleglosc(self.x, self.y, self.cel_x, self.cel_y)
        punkty = self._oblicz_punkty()

        print("\n========== RAPORT KOŃCOWY ==========\n")
        print(f"Nazwa wyprawy:     {self.nazwa}")
        print(f"Lazik:             {self.lazik}")
        print()
        print("-- Parametry startowe --")
        print(f"Pozycja startowa:  ({self.start_x}, {self.start_y})")
        print(f"Energia startowa:  {self.energia_start}")
        print(f"Cel:               ({self.cel_x}, {self.cel_y})")
        print(f"Maks. krokow:      {self.max_krokow}")
        print(f"Rozmiar swiata:    {self.rozmiar} (od -{self.rozmiar} do {self.rozmiar})")
        print()
        print("-- Wyniki --")
        print(f"Koncowa pozycja:   ({self.x}, {self.y})")
        print(f"Odleglosc od celu: {d:.1f}")
        print(f"Liczba krokow:     {self.krok}")
        print(f"Pozostala energia: {self.energia}")
        print(f"Zebrane probki:    {self.probki}")
        print(f"Stacje naprawcze:  {self.stacje}")
        print(f"Wpadniecte w krater: {self.kratery}x")
        print(f"Zdarzenia losowe:  {self.zdarzenia_losowe}")
        print()
        print("-- Wazniejsze zdarzenia --")
        if self.log:
            for wpis in self.log[-10:]:
                print(f"  {wpis}")
        else:
            print("  brak istotnych zdarzen")
        print()
        print(f"Przyczyna zakonczenia: {self.koniec_powod}")
        print(f"Wynik punktowy:        {punkty} pkt")
        print()

        if self.wynik == "sukces_plus":
            print("WYNIK: SUKCES Z WYROZNIEM (zebrano 3 lub wiecej probek)!")
        elif self.wynik == "sukces":
            print("WYNIK: SUKCES - lazik dotarl do celu!")
        elif self.wynik == "czesciowy":
            print("WYNIK: CZESCIOWY SUKCES - lazik byl bardzo blisko celu.")
        else:
            print("WYNIK: PORAZKA - lazik nie dotarl do celu.")

        print("\n====================================\n")

    def uruchom(self):
        self.setup()
        self._info_przed_startem()

        print(f"\nStart! {self.lazik} wyrusza z ({self.start_x}, {self.start_y}) w kierunku ({self.cel_x}, {self.cel_y}).")
        print(f"Odleglosc do celu: {odleglosc(self.start_x, self.start_y, self.cel_x, self.cel_y):.1f}\n")

        while True:
            self._krok()
            if self.sprawdz_koniec():
                break

        self.raport()


def main():
    print("Symulator wyprawy lazika marsjańskiego")
    print()

    while True:
        wyprawa = Wyprawa()
        wyprawa.uruchom()

        znowu = input("Zagrac jeszcze raz? (t/n,): ").strip().lower()
        if znowu == "t":
            print()
        else:
            print("Do widzenia!")

if __name__ == "__main__":
    main()
    sys.exit(0)