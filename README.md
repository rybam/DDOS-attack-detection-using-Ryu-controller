# DDOS attack detection using Ryu controller
 
Projekt polegający na wykrywaniu ataków typu flood w sieci SDN z wykorzystaniem sterownika Ryu oraz oprogramowania Mininet. Sieć użyta w projekcie składa się z 4 hostów, 3 przełączników OpenFlow oraz sterownika Ryu. W celu wykrywania ataków sterownik cyklicznie odpytuje przełączniki o statystyki przepływów i na podstawie tych statystyk wykrywa atakującego oraz jego ofiarę. Poprawny ruch użytkowników taki jak ping czy zapytania http, a także ataki typu flood są generowane w skrypcie 'customTopology.py', który wykorzystywany jest również do zestawienia sieci. 

W celu uruchomienia projektu wykonaj następujące kroki:
1. Należy zainstalować oprogramowanie Mininet oraz sterownik Ryu, np. https://ernie55ernie.github.io/sdn/2019/03/25/install-mininet-and-ryu-controller.html lub https://shantoroy.com/sdn/sdn-mininet-ryu/
2. Pobierz repozytorium oraz upewnij się, że pliki znajdują się w tym samym katalogu. Następne kroki wykonuj z katalogu, w którym znajdują się pliki.
3. Uruchom sterownik Ryu komendą: `sudo ryu-manager controller.py`
4. W osobnej konsoli, za pomocą skryptu uruchom sieć w Mininecie oraz generowanie ruchu między hostami: `sudo python customTopology.py`.
5. Typ generowanego ruchu można obserwować w konsoli z uruchomionym Mininetem, a rezultat działania systemu wykrywającego ataki można obserwować w konsoli z uruchomionym sterownikiem.
