Program symuluje wyprawę łazika po powierzchni Marsa. Łazik porusza się po dwuwymiarowej siatce, napotyka różne typy terenu i losowe zdarzenia, a celem jest dotarcie do wyznaczonych współrzędnych zanim skończy się energia lub limit kroków.
Uruchomienie
Wymagany Python 3.6 lub nowszy. Program nie wymaga żadnych dodatkowych bibliotek.

Parametry początkowe:
Na starcie program pyta o:

nazwę wyprawy i łazika
rozmiar swiata (siatka od -R do R na obu osiach)
pozycję startową (x, y)
energię startową
współrzędne celu
maksymalną liczbę kroków

Każdy parametr ma wartość domyślną — wystarczy wcisnąć Enter żeby jej użyć.

Typy terenu:
krater, -15 energii
probka, +12 energii
stacja, +30 energii
burza, -20 energii
tunel, -5 energii, teleportuje bliżej celu
pole, -25 energii

Poza tym co krok jest 25% szansy na losowe zdarzenie (rozbłysk słoneczny, deszcz meteorytów, awaria silnika itp.).
Warunki zakończenia:

Sukces — łazik dotrze do celu
Sukces z wyróżnieniem — dotrze do celu i po drodze zbierze 3 lub więcej próbek
Częściowy sukces — skończyły się kroki, ale łazik był bardzo blisko celu
Porażka — energia spadła do 0 albo przekroczono limit kroków

Cały kod znajduje się w pliku main.py. Główne elementy:

Wyprawa — klasa obsługująca całą symulację (setup, kroki, raport)
wczytaj_int / wczytaj_str — wczytywanie danych od użytkownika z obsługą błędów
pasek_energii — tekstowy pasek pokazujący aktualny stan energii
main — pętla główna z możliwością ponownego uruchomienia
