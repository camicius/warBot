#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import math
import random
import sys
import sqlite3
import csv
import os
import argparse



parser = argparse.ArgumentParser(description='Evolvi')

parser.add_argument('--database', '-d', required=True, help='database di lavoro')
parser.add_argument('--debug', '-D', action='store_true', help="attiva il debug")
parser.add_argument('--quiet', '-q', action='store_true', help="Non stampa i dettagli dei passi")
parser.add_argument('--azzera', '-a', action='store_true', help="azzera il database prima di iniziare")
parser.add_argument('--vittoria', '-v', help='percentuale di vittoria (0-100 default 95)')
parser.add_argument('--rivolta', '-r', help='percentuale di rivolta (0-100 default 0.05)')
parser.add_argument('--calcolo', '-c', help="parametro per il calcolo dell'attaccante (LINEARE|COSTANTE|SIGMOIDE|QUADRATONEG|QUADRATOPOS) default LINEARE")
parser.add_argument('--parametro', '-p', help='parametro del calcolo')
parser.add_argument('--passo', '-P', help='passo da cui inziare (default 0)')


args = parser.parse_args()
database=args.database
debug=args.debug
quiet=args.quiet
passo=args.passo
azzera=args.azzera
percentualeVittoria=args.vittoria
percentualeRivolta=args.rivolta
calcolo=args.calcolo
parametro=args.parametro




if passo==None: passo=0
else: passo=int(passo)
if percentualeVittoria==None: percentualeVittoria=95
else: percentualeVittoria=float(percentualeVittoria)
if percentualeRivolta==None:  percentualeRivolta=0.05
else: percentualeRivolta=float(percentualeRivolta)
if calcolo==None: calcolo='LINEARE'
if parametro==None: parametro=1
else: parametro=float(parametro)



#connetto al db
con = None
cur = None
try:

	con = sqlite3.connect(database)
	con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
	cur=con.cursor()
except sqlite3.Error, e:
	print "Error %s:" % e.args[0]
	sys.exit(1)



def calcola(card):
	card01=card/float(territori)
	if calcolo=='LINEARE':   return card*parametro
	if calcolo=='COSTANTE':  return 1
	if calcolo=='SIGMOIDE': 	return int(math.ceil(1/(1+math.pow(math.e,(5.0-10.0*card01)))*(territori/2)))
	if calcolo=='QUADRATONEG': 	
		exp=parametro*2
		razio=-math.pow (card01-1,exp)+1
		gino=razio *(territori/2)
		toreturn= int(math.ceil(gino))
	if calcolo=='QUADRATOPOS':
		exp=1.0/parametro
		razio=math.pow(card01,exp)
		gino=razio * float(territori)
		toreturn= int(math.ceil(gino))
	
	#print "Card=>"+str(card)+" Card01=>"+str(card01)+"Exp=>"+str(exp)+" Razio=>"+str(razio)+" Gino=>"+str(gino)+" toreturn"+str(toreturn)
	return toreturn




# esegui una query dritta sul db
def executeQuery(query):
	try:
		if debug: print query
		cur=con.cursor()
		cur.execute(query)

	except sqlite3.Error, e:

		print "Error %s:" % e.args[0]
		sys.exit(1)

# esegui una query con i parametri
def executeQueryParam(queryy,param):
	try:
		if debug:
			print ">>>executeQueryParam "+ queryy
			print param
		cur=con.cursor()
		cur.execute(queryy,param)

	except sqlite3.Error, e:

		print "Error %s:" % e.args[0]
		sys.exit(1)

# esegui una query con i parametri e restituisce i dati
def executeQueryParamFA(queryy,param):
	try:
		if debug:
			print ">>>executeQueryParamFA "+ queryy
			print param
		cur=con.cursor()
		cur.execute(queryy,param)
		return cur.fetchall()
	except sqlite3.Error, e:

		print "Error %s:" % e.args[0]
		sys.exit(1)


def evolvi ():
	query="select count (distinct proprietario) from territori;"
	rimasti=executeQueryParamFA(query,[])[0][0]
	if rimasti==1: 
		query="select distinct proprietario from territori;"
		vincente=executeQueryParamFA(query,[])[0][0]
		query="update territori set posizione = ? where nome = ?"
		param=[rimasti, vincente]
		executeQueryParam(query,param)
		con.commit()
		print "La guerra e' finita. L'intera nazione e' stata interamente conquistata. Da oggi si chiamera' reame di " + vincente
		con.close()
		sys.exit(0)
	if not quiet and passo%10==0: 
		print "############## "+str(rimasti)+ " territori rimasti"
		query=" select proprietario, count(*) from territori group by 1 order by 2 desc limit 10"
		rimastiArr=executeQueryParamFA(query,[])
		for best in rimastiArr:
			print best[0]+","+str(best[1])+","+str(calcola (best[1]))
	if quiet and passo%10==0: 
		sys.stdout.write('.')
		sys.stdout.flush()
	if quiet and passo%100==0: 
		sys.stdout.write(".>" + str(passo) + '\n')

	query='select proprietario, count(*)  from territori group by 1'
	result=executeQueryParamFA(query,[])	
	listaScelta=[]
	for territorio in result:
		nome=territorio[0]
		card=territorio[1]
		cardCalc=calcola(card)
		for i in range(0,cardCalc):
			listaScelta.append(nome)


	if debug: print listaScelta
	attaccante=random.choice(listaScelta)
	if debug: print "attaccante scelto " + attaccante
	query='select distinct c.t2 from territori t1 join confini c on (t1.nome=c.t1) join territori t2 on t2.nome=c.t2 where t1.proprietario=? and t2.proprietario!=? ;'
	param=[attaccante, attaccante]
	result=executeQueryParamFA(query,param)	
	if len(result)==0: 
		print query
		print param
		sys.exit(127)
	attaccato=random.choice(result)[0]
	if debug: print "attaccato " + attaccato
	query="select proprietario from territori where nome = ?"
	param=[attaccato]
	precedente=executeQueryParamFA(query,param)[0][0]
	punteggio=random.random()*100
	ok=punteggio<percentualeVittoria
	
	if punteggio>(100-percentualeRivolta):
		query='select nome, proprietario from territori where nome!=proprietario ;'
		result=executeQueryParamFA(query,[])	
		rivolta=random.choice(result)[0]
		proprietario=random.choice(result)[1]
		query="update territori set proprietario = ? where nome = ?"
		param=[rivolta,rivolta]
		executeQueryParam(query,param)
		query="insert into storia (passo, attaccante, attaccato, riuscito) values (?,?,?,?)"
		param=[passo,rivolta,rivolta, 'R']
		executeQueryParam(query,param)
		
		con.commit()
		if not quiet: print "Passo "+str(passo)+": RIVOLTA!!!! Gli abitanti del territorio di "+rivolta + " precedentemente posseduto da "+proprietario + " si sono ribellati all'occupazione"
	
	
	elif ok: 
		if debug: print "attacco riuscito"

		query="select proprietario from territori where nome= ? "
		param=[attaccato]
		proprietarioAttaccato=executeQueryParamFA(query,param)[0][0]

		query="update territori set proprietario = ? where nome = ?"
		param=[attaccante,attaccato]
		executeQueryParam(query,param)

		query="select count(*) from territori where proprietario = ? "
		param=[proprietarioAttaccato]
		rimanentiAttaccato=executeQueryParamFA(query,param)[0][0]

		query="insert into storia (passo, attaccante, attaccato, riuscito) values (?,?,?,?)"
		param=[passo,attaccante,attaccato, 'OK']
		executeQueryParam(query,param)

		con.commit()
		if precedente==attaccato:
			if not quiet: print "Passo "+str(passo)+": "+attaccante +" ha conquistato il territorio di "+attaccato
		else:
			if not quiet: print "Passo "+str(passo)+": "+attaccante +" ha conquistato il territorio di "+attaccato + " precedentemente posseduto da "+precedente
		if rimanentiAttaccato==0:
			if not quiet: print "        "+attaccato+" e' stato completamente sconfitto"	
			query="update territori set posizione = ? where nome = ?"
			param=[rimasti, proprietarioAttaccato]
			executeQueryParam(query,param)
			con.commit()	
	else: 
		if debug: print "attacco respinto"
		if not quiet: print "Passo "+str(passo)+": "+attaccante +" ha fallito la conquista di "+attaccato
		query="insert into storia (passo, attaccante, attaccato, riuscito) values (?,?,?,?)"
		param=[passo,attaccante,attaccato, 'KO']
		executeQueryParam(query,param)
		con.commit()



territori=0
query='select count(*) from territori'
territori=executeQueryParamFA(query,[])[0][0]

if azzera: 
	query='update territori set proprietario=nome'
	executeQuery(query)
	query='delete from storia'
	executeQuery(query)
	
while True:
	passo=passo+1
	evolvi()
