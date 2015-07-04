#!/usr/bin/env python
# -*- encoding: utf8 -*-
import requests
import re
import os
import sys

def urlify(s):
	s = re.sub(r"[^\w\s]", '', s)
	s = re.sub(r"\s+", '-', s)
	return s

s = requests.session()


while True:
	URL = raw_input('search_url: ')
	if URL.find('http://arxiv.org/find/')==0:
		break

try:
	os.remove('results.txt')
except Exception:
	pass

filename=urlify(URL.split('/')[6])

ctt_home = s.get(URL).content
# with open('ctt_home.txt','w') as f:
# 	f.write(ctt_home)
tgtb=0
tgte=0

while True:
	tgtb=ctt_home.find('"><a href="/abs/',tgtb)
	tgte=ctt_home.find('" title="Abstract"',tgte)
	if tgtb==-1:
		break
	# print ctt_home[tgtb+16:tgte]
	with open('results.txt','a') as f:
		f.write('http://arxiv.org/abs/'+ctt_home[tgtb+16:tgte]+'\n')
	tgtb+=1
	tgte+=1

with open('results.txt') as f:
	num_lines = sum(1 for _ in f)

print(str(num_lines)+' items total')
count=0

with open(filename+'.md','w') as f:
	f.write('`{'+URL+'}`\n\n')


with open('results.txt') as file_:

	for line in file_:

		ctt = s.get(line).content
		ab=''
		tt=''
		au=''
		ti=''
		cm=''

		# find abstract

		sb=ctt.find('>Abstract:</span> ')
		se=ctt.find('</blockquote>',sb)
		ab = ctt[sb:se]
		ab = ab.replace('</span>','').replace('\n',' ').replace('\r','').replace('<a href="/abs/','<a href="http://arxiv.org/abs/').replace('&lt;','<').replace('&gt;','>').replace('\\bm','\\boldsymbol')[1:]
		# print ab

		# find title

		sb=ctt.find('Title:</span>')
		se=ctt.find('</h1>',sb)
		tt = ctt[sb+14:se]

		# find author

		tmp=ctt.find('Authors:</span>')
		tmp2=ctt.find('<div class="dateline">')
		while True:
			sb=ctt.find('">',tmp)
			se=ctt.find('</a>',sb)
			if se>tmp2:
				break
			au=au+', '+ctt[sb+2:se]
			sb+=1
			tmp=sb
			se+=1
		au=au[2:]

		# find time

		sb=ctt.find('(',tmp2)
		se=ctt.find(')</div>',sb)
		ti = ctt[sb+1:se].replace('<a href="/abs/','<a href="http://arxiv.org/abs/')

		# find comment
		tmp3=ctt.find('<td class="tablecell comments">')
		sb=ctt.find('>',tmp3)
		se=ctt.find('<',sb)
		cm = ctt[sb+1:se].replace('<a href="/abs/','<a href="http://arxiv.org/abs/')

		tt = '['+tt+']('+line[:-1]+')  '
		au = '\n'+'*'+au+'*  '
		ticm = '\n' +'*'+ti+', '+cm+'*  '
		ab = '\n'+ab+'  '
		trk = '\n\n---\n\n'

		piece=tt+au+ticm+ab+trk
		# print (piece)

		with open(filename+'.md','a') as f:
			f.write(piece)

		count+=1
		print('writing '+str(count)+'/'+str(num_lines)+'...')

print(filename+'.md created!')

os.remove('results.txt')

print('converting...')
os.system("pandoc "+filename+'.md -o '+filename+'.pdf --latex-engine=xelatex -V geometry:margin=1.5cm')

print(filename+'.pdf created!')