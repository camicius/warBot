# warBot
codice python per creare una guerra casuale tra territori


Il progetto è composto da due file:

popolaDb.py -> serve per creare il database, partendo da un file csv di due colonne che definisce i territori che confinano. I confini sono sepmpre bidirezionali 

evolvi.py -> serve per generare una storia. Chiamare il programma senza parametri fornisce dettagli sul suo utilizzo.

Due dettagli sugli algoritmi di scelta del territorio attaccante. 
Il programma crea un array di proprietari inserendo tutti i proprietari un numero di volte così calcolato:
- COSTANTE: ogni proprietario è inserito una volta sola. In questo caso non c'è nessun vantaggio per un proprietario che ha molti territori
- LINEARE: ogni proprietario è inserito un numero di volte pari ai territori che possiede. 
- SIGMOIDE: il numero di volte in cui viene inserito segue la curva sigmoide (https://it.wikipedia.org/wiki/Equazione_logistica). Il parametro definisce la ripidezza della curva
- QUADRATONEG: il numero di volte in cui viene inserito ogni proprietario cresce molto all'inizio, poi viene calmierato
- QUADRATOPOS: il numero di volte in cui viene inserito ogni proprietario cresce poco all'inizio poi cresce in maniera polinomiale


Tutti i programmi sono rilasciati secondo i termini della GPL version 2.0
