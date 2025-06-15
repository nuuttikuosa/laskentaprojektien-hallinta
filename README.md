# laskentaprojektien-hallinta

## Sovelluksen toiminnot

- Käyttäjä pystyy luomaan käyttäjätunnuksen ja kirjautumaan sisään sovellukseen (TEHTY).
- Käyttäjä pystyy lisäämään sovellukseen laskentaprojekteja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään laskentaprojekteja ja lisäämään tehtäviä laskentaprojekteihin (TEHTY).
- Käyttäjä näkee sovellukseen lisätyt laskentaprojektit (TEHTY).
- Käyttäjä pystyy varaamaan tehtäviä itselleen laskentaprojekteista (TEHTY).
- Käyttäjä pystyy etsimään laskentaprojekteja hakusanalla (TEHTY).
- Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän varaamat tehtävät ja niiden tilan. (TEHTY)
- Käyttäjä pystyy muuttamaan varaamiensa tehtäviensä tilaa (ei aloitettu, kesken, valmis, luovu tehtävästä) ja palauttamaan tehtäväänsä liittyviä lokitiedostoja, jotka varmentavat, että tehtävä on valmis. (TEHTY)
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

 ## Yleistä laskentaprojekteista
Internetissä on joitain luonteeltaan hyvin rinnakkaistuvia lukuteoreettisia etsintäprojekteja. Tyypillisesti näissä etsitään alkulukuja. Esim. muotoa n!+1 olevia alkulukuja. Projektin tehtävät ovat kokonaislukuja. Jos käyttäjä saa tehtävän 20 000, niin hänen pitää client sovelluksella testata onko luku 20000!+1 alkuluku vai ei. Tämän vuoksi projektit ovat lukuvälejä, esim. 1 000 - 100 000 ja käyttäjät varaavat numeroita (tehtäviä) tältä lukuväliltä. Kun käyttäjät ovat validoineet saamansa tehtävät (numerot), niin he palauttavat lokitiedostoja. Serveri osaa näistä tulkita, mitkä tehtävät on tehty ja onko tuloksia löytynyt.

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

Kannattaa kokeilla sovellusta Powersum7 nimisellä projektilla, koska tätä varten on testitiedosto. 



 

 
