#!/usr/bin/env python
# -*- coding: utf-8 -*-
import colorsys
import sys
import sqlite3
import csv
import argparse

parser = argparse.ArgumentParser(description='Evolvi')
parser.add_argument('--database', '-d', required=True, help='database da creare')
parser.add_argument('--confini', '-c', required=True, help='file csv dei confini')
parser.add_argument('--debug', '-D', action='store_true', help="attiva il debug")
args = parser.parse_args()

database=args.database
confini=args.confini
debug=args.debug


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

# esegui una query dritta sul db
def executeQuery(query):
	try:
		if debug: print query
		cur=con.cursor()
		cur.execute(query)
		con.commit()
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

executeQuery("create table territori (nome text, proprietario text, posizione numeric)")
executeQuery("create table confini (t1 text,t2 text)")
executeQuery("create table confini_appoggio (t1 text, t2 text)")
executeQuery("create table storia (passo numeric, attaccante text, attaccato text, riuscito text)")

reader = csv.reader(open(confini,'rb'), delimiter=',')

for row in reader:
	t1=row[0]
	t2=row[1]
	if t1=='t1': continue
	if t1=='': continue
	query="insert into confini_appoggio (t1, t2) values (?,?)"
	print t1 + "-"+t2
	param=[t1,t2]
	executeQueryParam(query,param)
	param=[t2,t1]
	executeQueryParam(query,param)
	con.commit()


executeQuery("insert into confini select distinct t1,t2 from confini_appoggio ")
executeQuery("drop table confini_appoggio")
executeQuery("insert into territori (nome, proprietario) select distinct t1, t1 from confini ")

con.commit()
con.close()
