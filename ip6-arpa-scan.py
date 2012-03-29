#!/usr/bin/env python
from dns import message, query, exception
import sys

queries=0
l=[]
progress=[0]*3
progressperc=0

def tryquery(q, server):
	while 1:
		try:
			return query.udp(q, server, timeout=2)
		except exception.Timeout:
			pass

def drilldown(base, server, limit, depth=0):
	global queries, l, progress, progressperc
	if depth == len(progress):
		progressperc = 0 
		for i in range(len(progress)):
			progressperc = progressperc + (progress[i] / (16.0**(i+1)))*100

	print >> sys.stderr, '\r%*s, %s queries done, %s found, %.2f%% done' % (limit, base, queries, len(l), progressperc),

	q = message.make_query(base, 'PTR')
	r = tryquery(q, server)
	queries = queries + 1
	# print '%s: %s' % (base, r.rcode())
	if r.rcode() == 0:
		if len(base) == limit:
			l.append(base)
		if len(base) < limit:
	 		for c in '0123456789abcdef':
				if depth < len(progress):
					progress[depth]=int(c, 16)
				#print "progress[%s]=%s" % (depth, progress[depth])
				drilldown(c+'.'+base, server, limit, depth+1)
			

(base, server) = sys.argv[1:3]
if len(sys.argv) == 4:
	limit = int(sys.argv[3])/4*2+len('ip6.arpa.')
else:
	limit = 32*2+len('ip6.arpa.')

print 'base %s server %s limit %s' % (base, server, limit)

if base.endswith('ip6.arpa'):
	base = base + '.'

if not base.endswith('ip6.arpa.'):
	print 'please pass an ip6.arpa name'
	sys.exit(1)

try:
	drilldown(base, server, limit)
except KeyboardInterrupt:
	print >> sys.stderr, '\naborted, partial results follow'

print >> sys.stderr, '\nnames found: %s' % len(l)
print >> sys.stderr, 'queries done: %s' % queries
print '\n'.join(l)
