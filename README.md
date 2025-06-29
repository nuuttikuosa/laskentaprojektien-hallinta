# laskentaprojektien-hallinta

## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan käyttäjätunnuksen ja kirjautumaan sisään sovellukseen (TEHTY).
- Käyttäjä pystyy lisäämään sovellukseen laskentaprojekteja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään laskentaprojekteja ja lisäämään tehtäviä laskentaprojekteihin (TEHTY).
- Käyttäjä näkee sovellukseen lisätyt laskentaprojektit (TEHTY).
- Käyttäjä pystyy varaamaan tehtäviä itselleen laskentaprojekteista (TEHTY).
- Käyttäjä pystyy etsimään laskentaprojekteja hakusanalla (TEHTY).
- Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän varaamat tehtävät ja niiden tilan. (TEHTY)
- Käyttäjä pystyy muuttamaan varaamiensa tehtäviensä tilaa (ei aloitettu, kesken, valmis) ja palauttamaan tehtäväänsä liittyviä lokitiedostoja, jotka varmentavat, että tehtävä on valmis. (TEHTY)
- Käyttäjä pystyy panemaan projektin holdiin ja aktivoimaan sen (TEHTY)
- Sovelluksessa on projektikohtaiset sivut, jotka listaavat eri käyttäjien eri projekteille suorittamien tehtävien määrän (TEHTY).
- Käyttäjä voi palauttaa projektiin liittyviä tuloksia ja sovellus varmentaa ne, jos mahdollista (TEHTY).
- Sovelluksessa on sivu, jolta voi nähdä projekteissa löydetyt tulokset (TEHTY).

## Asennus 

Luo tietokanta:
```
$ sqlite3 database.db < schema.sql
```
Alusta tietokanta
```
$ sqlite3 database.db < init.sql
```
Asenna virtuaaliympäristö
```
$ python3 -m venv venv
```
Käynnistä virtuaaliympäristö
```
$ source venv/bin/activate
```
Asenna `flask`-kirjasto:
```
$ pip install flask
```
Sovellus voidaan käynnistää seuraavasti:
```
$ flask run
```

## Sovelluksen käyttö
1. käyttäjä perustaa sovellukseen käyttäjätunnuksen
2. käyttää kirjautuu sisään sovellukseen
3. Jos sovelluksessa ei ole mieluisia projekteja, niin käyttäjä perustaa projektin. Tällä hetkellä projektikohtainen toiminnallisuus on implementoitu "Powersum" tyyppisille projekteille, joilla etsitään ratkaisuja kokonaislukuyhtälöihin.
5. Käyttäjä generoi tehtävät projektille Edit project sivulta (tehtävät voi generoida tällä hetkellä vain kerran).
6. Kaikki käyttäjät voivat varata projektista tehtäviä.
7. Käyttäjä ajaa omalla koneella projektikohtaista brute force tyyppistä client ohjelmaa joka on kirjoitettu C:llä tai assemblerilla. Ajoittain käyttäjä voi uploadata clientin tuottaman lokitiedoston, josta sovellus löytää mahdollisesti löytyneet ratkaisut ja tehdyt tehtävät. Sovellut päivittää tehtyjen tehtävien statukseksi Done.

## Suorituskykytestaus

Tämän hetkinen oletus on, että samanaikaisia projekteja on korkeintaan muutamia kymmeniä, näillä korkeintaan muutamia satoja osallistujia ja projekteissa tehtäviä joitain satoja tuhansia. Varmuuden vuoksi sovellus on suorituskykytestattu seuraavilla lukumäärillä:
- projektien lukumäärä: 1 000
- käyttäjien lukumäärä: 1 000
- tehtävien lukumäärä: 10 000 000

Etusivun lataaminen kesti 60 sekuntia, projektisivun lataaminen kesti 0,4 sekuntia ja käyttäjäsivun lataaminen kesti 0.4 sekuntia. Tämän jälkeen tietokantaan lisättiin käyttöliittymän kautta projekti ja sille 100 000 tehtävää. Projektin tehtävien generointi kesti noin 115 sekuntia. 

Tietokantaan lisättiin indeksejä ja tämän seurauksena käyttö nopeutui hakutoiminnoissa huomattavasti. Etusivu latautui 11 sekunnissa, projektisivun lataaminen kestää samat 0,4 sekuntia ja käyttäjäsivun lataaminen kestää 0,1 sekuntia, mutta projektien ja tehtävien lisääminen hidastui 137 sekuntiin. 
Nämä ovat hyväksyttäviä arvoja, koska käytännössä tietokannassa on vähemmän tietoa.

Indeksit hidastavat tietokantaan lisäämisoperaatioita, mutta tämä näkyy käytännössä vain projektin hallinnointitehtävässä generoi projektin tehtävät.  Vaikka tehtävä kestää kauan ja hidastui indeksien lisäämisen myötä, niin kyseessä on harvinainen, korkeintaan kerran kuussa tehtävä operaatio, joka voi hyvin kestää joitain minuutteja. Hidastuminen on väistämätön seuraus indeksien käytöstä. Jos tulee tilanne, että tehtävien generointi kestää ylläpitäjältä liian kauan, niin voidaan kokeilla tietokannan indeksien poistamista, datan lisäämistä tietokantaan ja indeksien lisäämistä takaisin tietokantaan. Tämä todennäköisesti nopeuttaa operaatiota, mutta pitää suorittaa tietokannan (sqlite) komentotulkista.

Indeksit lisäämällä on haluttu tehdä sovelluksesta nopea projekteihin osallistujille. On ajateltu, että harvoin suoritettavat ylläpito-operaatiot (kuten tehtävien generointi projektille) voivat kestää pidempään. Tämänhetkisissä käyttöskenaarioissa dataa tulee myös olemaan tietokannassa vähemmän kuin suorituskykytestitapauksessa.  

## Sovelluksen käyttäjärooleista.

Sovelluksella on ylläpitäjä, joka on todennäköisesti sellainen käyttäjä joka hallinnoi myös joitain projekteja. Tämän lisäksi voi olla muutama muu käyttäjä, joka on perustanut ja hallinnoi projekteja. Vain muutama käyttäjä käytännössä perustaa ja hallinnoi projekteja.
Kaikki muut käyttäjät ovat projekteihin osallistujia.

Jos halutaan perustaa uudentyyppisiä projekteja, niin tämän sovelluksen kannalta on väliä vain sillä millaisia lokitiedostoja projektien laskenta ohjelmistot tuottavat ja mitä tehtävien sisällöt ovat.

On mahdollista, että lokitiedoston sisältö ja logiikka eroaa niin paljon ainoasta tällä hetkellä tuetusta projektimuodosta ”Powersum”, että sovellukseen joudutaan tekemään muutoksia ja kenties lisäämään uusi moduuli nykyisen powersum.py moduulin lisäksi, joka prosessoi uuden projektityypin lokitiedostot. Tämä on tuskin iso ongelma, koska laskentaohjelmiston kehittäminen vaatii ohjelmointia ja tarvittavat muutokset tämän sovellukseen ovat todennäköisesti pieniä pythonin merkkijonojen käsittelyyn liittyviä tehtäviä. Tällaiset muutokset ovat helppoja kokeneelle ohjelmoijalle.  Keskeinen tehtävä on suunnitella hyvä lokitiedostoformaatti laskentaohjelmistolle riippumatta siitä, miten laskentaohjelmisto sisäisesti toimii. Generoida käsin muutama lokitiedosto ja muuttaa ja testata tätä sovellusta vasten näitä lokitiedostoja. 

Valtaosa käyttäjistä varaa tehtäviä, konfiguroi laskentaohjelmiston projektin parametrien mukaisesti ja palauttaa lokitiedostoja. 

 ## Käyttäjän perustaminen
 Käyttäjätunnuksen pitää olla uniikki. Sähkäpostiosoitteen ei tarvitse olla uniikksi, jotta jotkut käyttäjäy voivat perustaa useita käyttäjärooleja - esim. yhden jokaiselle tietokoneelle jossa he ajavat laskentaohjelmistoa. Salasanalle ei ole kompeksisuusvaatimuksia. 

 ## Projektin perustaminen
 Projektille pakollisia tietoja ovat uniikki nimi, tehtävien miniminumero ja maksiminumero. Tämän pisäksi voidaan ahtaa yhdestä tehtävästä indikatiivinen laskenta-aika ja projektin tyyppi. Tällä hetkellä ainoastaan powersum tyyppisille projekteille voi palauttaa tehtäviä. Lisäksi projektille voi antaa parametreja. Tarkoitus on että tehtäviä varannut käyttäjä käyttää näitä arvoja konfiguroidessaan laskentaohjelmistoa. Parametreja ei voi muuttaa projektin perustamisen jälkeen, koska jos projekteihin osallistuja ovat suorittaneet tehtäviä väärillä parametreilla, niin työ on mennyt hukkaan ja on parempi deletoida virheellinen projekti ja perustaa uusi oikeilla parametreilla (osa tehtävistä on tehty väärin). 

Projektin perustamisen jälkeen projektin perustajan pitää generoida tehtävät projektille. Ajatus on, että generoitavien tehvävien väli on pienempi kuin tehtävien teoreettinen maksimi. jos tarvetta on, niin tehtäviä voidaan generoida myöhemmin lisää esim. yksinkertaisen python skriptin avulla joka lisää tehtäviä suoraan kantaan. Projektin tehtävät generoidaan muokkaa projektia sivulta. Perustettu projekti on tilassa ei aloitettu (Ei aloitettu) ja kun projektille on generoitu tehtävät niin se on tilassa käynnissä (Ongoing). Tämän jälkeen projektin perustaja voi laittaa projektin holdiin ja palauttaa holdista taas aktiiviseksi.

## Projektin osallistuja.
Projektin osallistuja perustaa käyttäjätunnuksen, selaa projekteja, varaa projekteista tehtäviä ja palauttaa lokitiedostoja. Lokitiedostot voivat sisältää ratkaisua tutkittaviin yhtälöihin ja sovellus varmistaa että ratkaisut ovat oikeita ja listaa löydetyt ratkaisut solutions sivulla. Palautetut lokitiedostot ja ratkaisut tallennetaan tietokantaan ja linkitetään käyttäjään ja palautettujen tehtävien tilaksi muutetaan tehty (Done).  
 
 ## Yleistä laskentaprojekteista
Internetissä on joitain luonteeltaan hyvin rinnakkaistuvia lukuteoreettisia etsintäprojekteja (esim. https://www.mersenne.org/). Tyypillisesti näissä etsitään alkulukuja. Esim. muotoa n!+1 olevia alkulukuja. Projektin tehtävät ovat kokonaislukuja. Jos käyttäjä saa tehtävän 20 000, niin hänen pitää laskenta sovelluksella testata onko luku 20000!+1 alkuluku vai ei. Tämän vuoksi projektit ovat lukuvälejä, esim. 1 000 - 100 000 ja käyttäjät varaavat numeroita (tehtäviä) tältä lukuväliltä. Kun käyttäjät ovat validoineet saamansa tehtävät (numerot), niin he palauttavat lokitiedostoja. Serveri osaa näistä tulkita, mitkä tehtävät on tehty ja onko tuloksia löytynyt.

 ## Powersum projekteista
 Powersum projekteissa etsitään ratkaisuja seuraavanlaisiin kokonaislukuyhtälöihin:
 (p,n,m) missä p on potenssi ja n on vasemmanpuoleiset termit ja m oikeanpuoleiset termit. Esimerkiksi:
 (11,6,8) 1106+1056+955+874+794+326=1133+1051+795+536+421+294+238+115  tarkoittaa
 1106^11+1056^11+955^11+874^11+794^11+326^11=1133^11+1051^11+795^11+536^11+421^11+294^11+238^11+115^11. Minulla ja muutamalla muulla on käynnissä tällainen projekti, jonka työtä on koordinoitu manuaalisesti, mutta helpottaakseni elämää tein automatisoidun ratkaisun jota pitää vielä viilata.

Nyt tehtävä on suurin numero yhtälön vasemmalla puolella. Esim. tehtävä 1000 tarkoittaa esim. potenssin 11 tapauksessa, että yhtälön vasen puoli on muotoa 
1000^11 + a^11 + b^11 + c^11+ d^11 + e^11 = ... jossa a,b,c,d,e <=1000. Tämä jakaa etsintäalueet yksikäsitteisesti.

Powersum projektilla voi olla seuraavanlaisia parametreja:
```
Range min: 1 (tehtävien lukualueen absoluuttinen minimi)
Range max:201 (tehtävien lukualueen absoluuttinen maksimi)

Project parameters
power = 7
left_terms = 3
right_terms = 4
```
Kun tehtävät generoidaan, niin niiden pitää olla välillä Range min ja Range max.

Hakemistosta testdata löytyy esimerkki client sovelluksen lokista, jossa on ilmoitettu muutama tehtävä tehdyksi ja muutama löydetty ratkaisu. Tämän voi palauttaa Return tasks toiminnallisuudella. Jos palautetaan sellaiselle projektille, jonka nimi vastaa lokitiedostossa joka rivin alussa olevaa projektin nimeä, niin sovellus kirjaa tehtävät tehdyksi. 

Kannattaa kokeilla sovellusta Powersum7 nimisellä projektilla, koska tätä varten on testitiedosto. Tämä sovelluksen toiminta perustuu täysin lokitiedoston formaattiin.

TODO: Lokitiedosto on allekirjoitettu ja sovellus pystyy verifioimaan, että se on validin laskentasovelluksen tuottama. Vaatii yksinkertaisia muutoksia laskentasovellukseen ja tämän sovelluksen muutokset pitää tehdä käsi kädessä laskentasovelluksen muutosten kanssa.   



 

 
