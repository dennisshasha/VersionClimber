# [x for x in temp if not x[0] in keepfixed]
# May 10, 2015:
# This version can be called as follows 
# python liquidparser.py 2
# which means that the caller and callee at the point of error is always known
# or
# python liquidparser.py 1
# which means that the caller may not be known (the default)
# The interface to works changes in its return value
# 
# [True] -- everything is fine
# [False, 0, callee, caller] -- if you know both; Must be used with option 2
# [False, 1, callee] -- if compilation
# [False, 2, callee] -- if in execution and you don't know the caller.
#
#
# Basic idea is this: False, 0 we handle now.
# False 1 -- just eliminate that version of that package.
# False 2 -- Because we are changing just one package at a time,
# if we have a configuration in which Pj has no error and then 
# we change Pi and Pj has an error, then Pi calls Pj.
# In general, if we have a configuration C that has an error on 
# Pj that has just been pushed 
# and we push Pi where i != j to get configuration C'
# and C' fails on Pk where i != k, then
# Pi must precede Pj in the call stack and
# either Pi calls Pk (Pi --> Pk) or Pi calls Pj and is compatible but Pj
# calls Pk and is not compatible (Pi --> Pj --> Pk).
# Unpush Pj from C' to obtain C''
# If get an error on Pk, then Pi --> Pk.
# If get an error on Pm, then
# We might have prior information about calling relationships.
# In either case, start to push Pk.
# If there is a configuration C'' that is a minimal pair with C except Pj
# C1 that works.
# C2 pushes Pj from C1 and Pk fails, then Pj --> Pk and that is minimal pair
# C2 pushes Pj from C1 and Pj fails, then test each Pq 
#  by pushing from C2 giving C2_q
#  and by pushing Pq from C1 as well giving C1_q
#  If nothing fails in C2_q, then great.
#  If Pq fails in C2_q, then Pq precedes Pj
#  If Pj fails in C2_q, then Pj precedes Pq o test C1_q

# Let's say we optimize in the order P3 then P1 and execution
# order is PA, PB, P1, PC, P3, ...
# Pushing P3 will result in an error. Pushing PA results in an error on PB. 
# Pushing PB results in an error on PB.
#  
#     
# 
# If we now take a case where we keep Pi pushed but unpush Pj and we
# still get an error on Pk, then 
# If we then change Pj and there is still an error, Pi still calls Pj.
# If we change Pj and there is an error on Pk, then Pj is the caller.
# So, remember who the lastcaller and packagechanged are.
# If the error is on packagechanged, then caller is lastcaller.
# If the error is on a different package, then lastpackagechanged becomes 
# the lastcaller
# and the package in error is the callee.
# The problem arises when we are pushing a priority version.
# In that case, if the error occurs on that package P1, we have to test other
# packages that do not precede P1 on the todo list. 
# Test package P2 with respect to the original setting of the given
# package. If you do that and get an error in Px then P2 calls Px
# (this is the only case we know for sure -- start in a good configuration
# and go to a bad one and one package advances and another fails).
# Keep advancing P2. This may give more stuff in memo.
# If you try all versions of other packages and none of them result in
# an error on P1, then advance P1 to the version causing an error and
# one at a time try all versions of other packages on that one
# except for a package Py that is known to cause a problem with the original
# version of package Pz (can use memo as usual for this).
# So, if a package Py.vy' has no problem with Pw.vw initially
# but does after P1.v1 advances to P1.v1', then ...
# If one of those makes P1 work, then  that one calls P1.
# If none does, then advance P1 again.
# There are cases where we are indeterminate: P1 has been pushed on the
# original configuration causing an error. Then P2 pushes and finds an
# error on package P3 -- did that error precede the error on P1 or follow it.
# If it preceded, then we don't know if P2 is compatible with P1 but maybe
# Scenario: All versions start at 1 and work.
# P3.2 with all others at version 1 and P3 fails as callee.
# P1.2 with all others at version 1.
# If Px fails for x != 1, then P1 calls Px.
#     add P1.2, Px.1 to memo
#    if x == 3, then advance P3 to P3.2 and try again
# If P1 fails, then we don't know anything other than this has failed.
# Let's see if we can find a cross-product based algorithm.
# Advance in descending order of priority and each time, try the cross-product
# of possibilities of other packages. If advancing a version of Px to i+1
# causes a failure in Py.j and when the identical configuration with Px with i
# worked, then Px.i+1 to Py.j goes into memo.
# If we later try Px.i+2 and Py.j and it fails on Py.j, but some other
# configuration worked identical except we had Px.i and instead of Px.i+2, then
# again we can add Px.i+2, Py.j to memo.
# So, we advance in descending order of priority. If we fail on some Py,
# then we apply this rule.
# Always take the cross-product of downstream in priority.
# If we start to get ideas about who calls whom, then we can 
# at least use the following heuristic: if I fail on Pw that I have
# just pushed, then first
# look at configurations in which some caller of package Pw changes. 
# So we need functions that push from successful configurations
# and others that look at likely callers and evaluate the 
# cross-product of those.
# Can we do better than this?
# A) P1.1., P2.1, P3.1 ... works
# B) P1.1., P2.1, P3.2 ... fails on P3
# Cannot conclude anything about caller.
# C) P1.2., P2.1, P3.1 ... fails on P3
# P1 calls P3.
# D) P1.2, P2.1, P3.2, P4... fails on P4
# P1.2 is compatible with P3.2 and P3 calls P4.
# So we should remember who calls whom (so if we get a failure we have 
# an idea what to do). And we should remember where there are compatibilities
# If we know who calls whom and a package can be called from several
# calling packages, then when the package fails after being pushed,
# we should play this game.
# Procedure: if we push Px and get an error on Px, then play with 
# potential callers of Px and see what you can do.
# First look at callers of Px denoted Py and push those. See if you get 
# an error on Px in which case you'll add that to memo.
# Try pushed Py with pushed Px and see if you go beyond Px say to Pz.
# 
# The reason we can't stay with the version of P1 that didn't work is that
# we may never find out what calls P1.
# May 5, 2015 version: includes strong monotonicity code
# What we want: reprozip runs. 
# packages are discovered.
# user is asked any restrictions -- can click.
# which to maximize
# go
# This code is nearly ready for integration with Christophe.
# It must fill the variable sourcemap based on versions of each relevant
# package

# Eventually, we have to get a configuration file that holds (i) the constraints
# (ii) the packages that we want to maximize in descending order of priority
# (iii) the default configuration.
# For now, please look at constraints = ... and  todolist = 
# and default =

# To run this file simply run it without any further arguments, i.e.
# python liquidparser.py
# If you want to see how it works, then change the simulator by
# changing the parts labeled DATA



# The program:
# 
# Simulator of acceptable versions.
# (package1, versionlow1, versionhigh1, package2, versionlow2, versionhigh2)
# Semantics are that any version 
# between versionlow1 and versionhigh1
# of package 1 will work with any version 
# between versionlow2 and versionhigh2 of package 2.
# 
# Some random ordering of package/version pairs in an execution.
# 
# If the next package/version is incompatible with the 
# package/versions already seen then we have a failure with 
# an announcement of where bad.



import sys
import math
import csv
import os
import copy
import operator
import doctest
import itertools
import collections
import datetime
import random
from operator import itemgetter, attrgetter
sys.setrecursionlimit(30000) 


now = datetime.datetime.now()
currentyear = now.year

#####################################
# global variables Global GLOBAL
#####################################

memory = {} # we will remember here the versions of package
    # combinations that don't work, so we don't redo them
    # we just keep exploring higher versions

axiom = {} # we use the historicity and failure monotonicity axioms
 # each element is keyed by two packages and has the format
 # (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)
 # Will no longer be used once we have the monotonicity code.

successful = [] # configurations that have been tried and worked at any time

failedconfigs = [] # configurations that have failed

nocompile = [] 
   # package-versions that don't compile, so should not be considered further

knowcaller = False # if you'll always know the caller, then set to True
# can override with a command line argument
if 1 < len(sys.argv):
  if (sys.argv[1] == "False") or (sys.argv[1] == "1") or (sys.argv[1] == "false") or (sys.argv[1] == "FALSE"):
     knowcaller = False
  else:
     knowcaller = True



###################################################################


# Simulator code


# is ver1 of pack1 compatible with ver2 of pack2
# If the packages are the same then return true
# Could be compatible if there is no mention of the two versions
# or if there is a match
# This is based on symmetric compatibilities
def compatible(packver1, packver2):
  pack1 = packver1[0]
  ver1 = packver1[1]
  pack2 = packver2[0]
  ver2 = packver2[1]
  bydefault = True
  if pack1 == pack2:
	return True
  for c in compatibilities:
    if (c[0] == pack1) and (c[3] == pack2): 
	bydefault = False # the two packages are in the list of compatibilities
    	if (ver1 >= c[1]) and (ver1 <= c[2]) and (ver2 >= c[4]) and (ver2 <= c[5]):
		return True
    if (c[0] == pack2) and (c[3] == pack1): 
	bydefault = False # the two packages are in the list of compatibilities
    	if (ver1 >= c[4]) and (ver1 <= c[5]) and (ver2 >= c[1]) and (ver2 <= c[2]):
		return True
  return bydefault # if we've never encountered these packages, we'll return
	# true, but if we have found the packages but no compatible versions,
	# then we'll return False
		

# is ver1 of pack1 compatible with ver2 of pack2
# If the packages are the same then return true
# Could be compatible if there is no mention of the two versions
# or if there is a match
# This is based on CUDF style compatibilities -- caller can call
# a callee having version x or better
def cudftest(packver1, packver2):
  pack1 = packver1[0]
  ver1 = packver1[1]
  pack2 = packver2[0]
  ver2 = packver2[1]
  bydefault = True
  if pack1 == pack2:
	return True
  for c in cudf:
    if (c[0] == pack1) and (c[3] == pack2): 
	bydefault = False # the two packages are in the list of cudfs
    	if (ver1 >= c[1]) and (ver1 <= c[2]) and (ver2 >= c[4]):
		return True
  return bydefault # if we've never encountered these packages, we'll return
	# true, but if we have found the packages but no compatible versions,
	# then we'll return False
		
# Given a new package-version pair newpackver,
# is it compatible with the ones that are already there?
def decidepackage(historyofpackversions, newpackver):
   print "decidepackage: historyofpackversions, newpackver:", historyofpackversions, newpackver
   if 0 == len(historyofpackversions):
	return [True, newpackver[0]]
   h = historyofpackversions[-1] # only worry about the very last one
   if compatible(h, newpackver) == False: # ??? Changed for CUDF
   # if cudftest(h, newpackver) == False:
	print "decidepackage: call for config from ", h, " to ", newpackver, " has return value False."
	return [False, h[0]]
   else:
	# print "decidepackage: call on compatible from ", h, " to ", newpackver, " has return value True."
   	return [True, newpackver[0]]

# Does an execution work? If so return an empty list. 
# If not, return the package that failed.
def works(listofpackversions):
   history = []
   for p in orderofpackages:
	x = decidepackage(history, [p,listofpackversions[p]])
	if x[0]:
		history.append([p,listofpackversions[p]])
	else:
		print "  Success up to: ", history
		print "  Failure on: ", p, listofpackversions[p]
		if knowcaller:
			return [False, 0, p, x[1]] 
		else: # if you know callee then state it, but if not, can replace p by -1
			return [False, 2, p] 
			# ??? changed the 0 to 2 to test out callee only
   return [True, 0, -1, -1] # -1 indicates all ok only use the True part


# APPLICATION-SPECIFIC (outside of simulator)

# given that we have just pushed package P,
# find a minimal pair of current configuration with
# a successful configuration, meaning a configuration in 
# successful that is identical to current in pack-ver except in P.
def findminimalpair(P, currentconf):
   i = 0
   print "findminimal currentconf: ", currentconf
   print "  findminimal P: ", P
   while i < len(successful):
      s = successful[i]
      print "  findminimal s: ", s
      flag = True
      for c in currentconf:
        if (not c == P) and (not currentconf[c] == s[c]):
             flag = False # no minmal pair
      print "  findminimal flag: ", flag
      if flag:
        return True
      i+= 1
   return False

# filter the source based on constraints and output the result
def filtermap(sourcemap, constraints):
	out = {}
	for s in sourcemap.viewkeys():
		vals = sourcemap[s]
		if s in constraints.viewkeys():
			vals = [v for v in vals if (v >= constraints[s][0]) and (v <= constraints[s][1])]
		out[s] = copy.deepcopy(vals)
	return out


# flatten takes a list and creates a string with underbars
def flatten(list):
  out = ""
  for x in list:
	out+= (str(x))
	out+= '_'
  return out

# testaxiom looks at the various axioms to see
# whether a given call on newpackver from the last element of history
# has already been determined to be incompatible
# returns True if incompatibility else False if no trouble found
# element of axiomlist has format 
# (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)
def testaxiom(axiomlist, h, new):
    for a in axiomlist:
	if (h[0] == a[0]) and (new[0] == a[3]):
		hver = a[1]
		horientation = a[2]
		newpackver = a[4]
		newpackorientation = a[5]
	elif (h[0] == a[3]) and (new[0] == a[0]):
		hver = a[4]
		horientation = a[5]
		newpackver = a[1]
		newpackorientation = a[2]
	hsat = ((h[1] == hver) and (horientation == 'eq'))
	hsat = hsat or ((h[1] <= hver) and (horientation == 'lesseq'))
	hsat = hsat or ((h[1] >= hver) and (horientation == 'greatereq'))
	newpacksat  = ((new[1] == newpackver) and (newpackorientation == 'eq'))
	newpacksat  = newpacksat or ((new[1] <= newpackver) and (newpackorientation == 'lesseq'))
	newpacksat  = newpacksat or ((new[1] >= newpackver) and (newpackorientation == 'greatereq'))
	if hsat and newpacksat:
		return True
    return False


# Given a new package-version pair newpackver,
# is it compatible with the ones that are already there?
# Here we don't execute, but rather use memory
# and the axiom datastructures
def memorydecidepackage(historyofpackversions, newpackver):
   if 0 == len(historyofpackversions):
	return [True, newpackver[0]]
   for h in historyofpackversions:
	if flatten(h) in memory.viewkeys():
	   if newpackver in memory[flatten(h)]:
		print "memorydecidepackage: memory call from  ", h, " to ", newpackver, " has return value False."
		return [False, h[0]]
	   else:
		print "memorydecidepackage: memory call from  ", h, " to ", newpackver, " has return value True."
   print "+++ memorydecidepackage -- position 2"
   h = historyofpackversions[-1]
   x = flatten([h[0], newpackver[0]])
   if x in axiom.viewkeys():
	if testaxiom(axiom[x], h, newpackver):
		print "axiom call for  ", h, " with ", newpackver, " has return value False because of ", axiom[x]
		return [False, h[0]]
   return [True, newpackver[0]]

# is newconfig in list of configs?
def inconfig(newconfig, listofconfigs):
   if 0 == len(listofconfigs):
	return False
   for s in listofconfigs:
	if s == newconfig:
		return True
   return False

# output a unique set of configs
def finduniqs(inputconfigs):
   out = []
   for s in inputconfigs:
	if not inconfig(s,out):
		out.append(s)
   return out

# is newconfig in list of configs?
def inconfigfail(newconfig, listofconfigs_packs):
   if 0 == len(listofconfigs_packs):
	return [False, -3, -3]
   for s in listofconfigs_packs:
	if s[0] == newconfig:
		return [True, s[1], s[2]]
   return [False, -2, -2]

# see whether both the caller with this version and the callee with this
# version are in memory
def inmem(callpackver, calleepackver, memory):
   x = flatten(callpackver)
   if x not in memory.viewkeys():
	return False
   for e in memory[x]:
	if ((e[0] == calleepackver[0]) and (e[1] == calleepackver[1])):
		return True
   return False

# see whether there is a caller having a smaller version that calls
# a callee with a greater version. If so, return true (meaning
# that in the strong monotonic assumption, this will fail).
def inmemstrong(callpackver, calleepackver, strongmemory):
   for s in strongmemory:
	if (s[0] == callpackver[0]) and (s[1] <= callpackver[1]) and (s[2] == calleepackver[0]) and (s[3] >= calleepackver[1]):
		return True
   return False

# First see whether we can determine that this won't work because
# of what we remember. If we can, then return False, 
# identify the offending package
# combinations and return a False indicating we did not need to to a real
# execution.
# latestpackchanged is the package that was most recently changed
# Otherwise, return False, identify the offending package combinations
# when possible
# and return a True indicating we DID a real execution.
def checkworks(listofpackversions, latestpackchanged):
   print "--- checkworks listofpackversions, lastpackchanged:", listofpackversions, latestpackchanged
   if inconfig(listofpackversions, successful):
	print "listofpackversions: ", listofpackversions
	print "matching successful run: ", listofpackversions
	return [True, -1, -1, False] # already good. Didn't execute
   zz = inconfigfail(listofpackversions, failedconfigs)
   if zz[0]:
	print "listofpackversions: ", listofpackversions
	print "matching failedconfigs run: ", listofpackversions
	return [False, zz[1], zz[2], False] # already known to be bad. Didn't execute
   for x in listofpackversions:
	if x in nocompile:
		print "this pack-version doesn't compile:", x
		return [False, x[0], x[0], False] # doesn't compile
   history = []
   for p in listofpackversions:
   	print "--- checkworks package before : ", history, p
	x = memorydecidepackage(history, [p,listofpackversions[p]])
   	print "--- checkworks package after : ", p
	if x[0]:
		history.append([p,listofpackversions[p]])
	else:
		print "Have avoided an execution."
		return [False, p, x[1], False]
   # using memory did not exclude the possibility that this would work
   x = works(listofpackversions)
   print "Tested configuration in works: ", listofpackversions
   y = copy.deepcopy(listofpackversions)
   if (x[0]):
   	print "  Test successful!"
   	successful.append(y)
	z = -1
	return [True, -1, -1, True]
   else: # config did not work
     if (x[1] == 0):
	failedconfigs.append([y, x[2], x[3]])
	addtomemory(y, x[2], x[3])
	return [x[0], x[2], x[3], True]
     if (x[1] == 1):
	nocompile.append([x[2], y[x[2]]])
	failedconfigs.append([y, x[2], x[3]])
	return [x[0], x[2], x[2], True]
     if (x[1] == 2):
	if (not latestpackchanged == x[2]) and findminimalpair(latestpackchanged, y): 
	   # found minimal pair with respect to a successful configuration
	   # that differs only in latestpackchanged
	   # and callee is not the same as latestpackchanged
	   failedconfigs.append([y, x[2], latestpackchanged])
	   addtomemory(y, x[2], latestpackchanged)
	   return [x[0], x[2], latestpackchanged, True]
	elif x[2] > -1: # we know the package that crashed
	   return [x[0], x[2], -1, True]
	else:
	   return [x[0], x[2], -1, True]
        


# whichever version of badcallee is in temp is incompatible with
# the version of badcaller in temp
# We are storing package version pairs and indexing by package version pairs.
# In strongmemory, [badcaller, vercaller, badcallee, vercallee]
def addtomemory(temp, badcallee, badcaller):
   vercallee = temp[badcallee]
   vercaller = temp[badcaller]
   print "caller: ", badcaller, vercaller, " and callee: ", badcallee, vercallee
   x = flatten([badcaller, vercaller])
   if x not in memory.viewkeys():
	memory[x] = []
   memory[x].append([badcallee, vercallee])
   strongmemory.append([badcaller, vercaller, badcallee, vercallee])

def mymed(mylist):
   return mylist[len(mylist) / 2]

# hunter method of finding best configuration.
# This method can degenerate into a cross-product method if we 
# are not careful. However we can try.
def hunter(searchedpackage, temp, newsourcemap, phase, previouscaller, lastpackchanged):
   # First we try just pushing all packages except those in todo list 
   # that either precede or equal searchedpackage
   # until we get something that works.
   i = todolist.index(searchedpackage)
   keepfixed = todolist[:i+1] # don't change these
   packagestopush = [x for x in temp if not x in keepfixed]
   print "hunter: packagestopush ", packagestopush
   print "hunter: newsourcemap ", newsourcemap
   found = False
   temp2 = copy.deepcopy(temp)
   temp2_max = copy.deepcopy(temp2)
   for p in packagestopush:
	temp2_max[p] = max(newsourcemap[p])
   allconfigs = []
   allconfigs.append(temp2)
   # allconfigs.append(temp2_max)
   while not found:
	returnnow = True
	newallconfigs = copy.deepcopy(allconfigs)
	print "hunter: newsourcemap: ", newsourcemap
	for c in allconfigs: 
	 keepgoing = True
	 while keepgoing:
	   keepgoing = False
	   # for each configuration, push within packagestopush but give
	   # priority to ones that just had an error
	   newstack = [] # used when we want to focus on some package
	   mystack = copy.deepcopy(packagestopush)
	   while (0 < len(mystack)) or (0 < len(newstack)):
		if 0 == len(newstack):
		   temp3 = copy.deepcopy(c)
		   p = mystack.pop() # takes from the end
		else:
		   p = newstack.pop() # take from reserve of newstack items
			# adjust already updated temp3
		# print "temp3", temp3
		# print "temp3[p]", temp3[p]
		# print "newsourcemap[p]", newsourcemap[p]
		if temp3[p] < max(newsourcemap[p]):
		   newver = min([v for v in newsourcemap[p] if v > temp3[p]])
		   temp3[p] = newver
		   print "hunter: temp3:", temp3
		   if not  inconfig(temp3,newallconfigs):
		     print "hunter: temp3 past inconfig"
		     returnnow = False
		     keepgoing = True
		     t = copy.deepcopy(temp3)
		     newallconfigs.append(t)
		     ret = checkworks(temp3, p)
		     # print "ret is: ", ret
		     if ret[0]:
			print "xxx successful config: ", temp3
			return temp3
		     # elif ret[1] in packagestopush:
			# newstack.append(ret[1])
	allconfigs = finduniqs(newallconfigs)
	if returnnow:
	   return {}
	print "xxx len(allconfigs): ", len(allconfigs)
	# temp2 = copy.deepcopy(allconfigs[-1])
   return {}


# by advancing versions as needed, try to make a compatible set of
# package-version pairs
# Side effect to memory in order to avoid unnecessary executions
# temp is the configuration of package-versions we are trying
# searchedpackage is the package that was pushed
# Works well when we get caller and callee
def trytomakework(searchedpackage, temp, newsourcemap, phase, previouscaller, lastpackchanged):
  print "        "
  print "+++ Within trytomakework, on configuration ", temp
  x = checkworks(temp, lastpackchanged) 
	# searchedpackage acts both the role of previous caller and
	# currently changed package
	# we simulate this now, but in general
	# this involves the creation of a frozen virtual machine
  print "++ Return value of: ", x
  if x[0] == False:
     badcallee = x[1] # callee
     badcaller = x[2] # caller
     previouscaller = badcaller
     i = todolist.index(searchedpackage)
     keepfixed = todolist[:i+1] # don't change these
     # if (x[3]) and (not badcallee == badcaller): 
	# x[3] is true if we really did execute
	# baddcallee == baddcaller if compile error
	# Those have been added to nocompile already
     	# addtomemory(temp, badcallee, badcaller)
     if badcaller in keepfixed:
	posscallerversions = [temp[badcaller]]
     else:
	posscallerversions = (sorted(newsourcemap[badcaller]))
     if badcallee in keepfixed:
	posscalleeversions = [temp[badcallee]]
     else:
	posscalleeversions = (sorted(newsourcemap[badcallee]))
     print "calling package: ", badcaller, " with possible versions: ", posscallerversions
     print "called package: ", badcallee, " with possible versions: ", posscalleeversions
     for c_er in posscallerversions:
     	for c_ee in posscalleeversions:
	   if ((phase == 1) and (not inmemstrong([badcaller,c_er], [badcallee,c_ee], strongmemory))) or ((phase == 2) and (not inmem([badcaller,c_er], [badcallee,c_ee], memory))):
		newtemp = copy.deepcopy(temp)
		newtemp[badcaller] = c_er
		newtemp[badcallee] = c_ee
		if (not newtemp[badcaller] == temp[badcaller]):
			lastpackchanged = badcaller
		elif (not newtemp[badcallee] == temp[badcallee]):
			lastpackchanged = badcallee
  	  	print "        "
  	  	print "+++ Within trytomakework deep, on configuration ", newtemp
		print "inconfig(newtemp,successful):", inconfig(newtemp,successful)
		print "inconfigfail(newtemp,failedconfigs):", inconfigfail(newtemp,failedconfigs)
		zz = inconfigfail(newtemp,failedconfigs)
		if (not inconfig(newtemp,successful)) and (not zz[0]):
		  x = trytomakework(searchedpackage, newtemp, newsourcemap, phase, previouscaller, lastpackchanged)
  	  	  print "++ Return value of: ", x
		  if 0 < len(x):
			return x  
     return {}
  else:
     return temp
  
	


	

# This implements the algorithm against our simulator, but eventually
# against a real system
# todolist gives the order of packages that must be maximized
# When the global phase is 1 then we use strong monotonicity.
# When the global phase is 2, we go to the conservative approach.
def liquidclimber(constraints, todolist):
  newsourcemap = filtermap(sourcemap, constraints)
  y = copy.deepcopy(default)
  if 0 < len(default):
    successful.append(y) # initially, we have a working configuration
  if knowcaller:
    print "newsourcemap before monotonicity filtering: ", newsourcemap
    bestmonoconfig = liquidclimberworker(constraints, todolist, newsourcemap, 1)
    print "best configuration after  monotonicity filtering: ", bestmonoconfig
    newsourcemap = adjustsource(newsourcemap, bestmonoconfig, todolist)
    print "newsourcemap after monotonicity filtering: ", newsourcemap
    print "failed configurations: ", failedconfigs
  # if knowcaller is false, come straight to here
  return liquidclimberworker(constraints, todolist, newsourcemap, 2)


# This implements the algorithm against our simulator, but eventually
# against a real system
# todolist gives the order of packages that must be maximized
# When the global phase is 1 then we use strong monotonicity.
# When the global phase is 2, we go to the conservative approach.
def liquidclimberworker(constraints, todolist, newsourcemap, phase):
  current = copy.deepcopy(default)
  if (0 == len(current)):
	for p in newsourcemap:
		x = min(sourcemap[p]) - 1
		current[p] = x
  for m in todolist: # todolist gives the packages to maximize
	# in descending order of priority
	maxmyversions = max(newsourcemap[m])
	print "liquidclimberworker: current is: ", current, "phase is: ", phase
	if (current[m] < maxmyversions):
		versionstodo = [v for v in newsourcemap[m] if v > current[m]]
		versionstodo.sort(reverse=True)
		print "liquidclimberworker: package is: ",m
		print "liquidclimberworker: versionstodo is: ",versionstodo
		# versions still to try
		found = False
		for v in versionstodo:
		   if not found:
			print "liquidclimberworker pack-ver: ", m, v
			temp = copy.deepcopy(current)
			temp[m] = v
			if knowcaller:
				ret = trytomakework(m, temp, newsourcemap, phase, m, m)
			else:
				print "liquidclimberworker calling hunter"
				ret = hunter(m, temp, newsourcemap, phase, m, m) # don't know the caller always
			print "return value: ", ret, " for config: ", temp
			if 0 < len(ret):
				current = copy.deepcopy(ret) 
				found = True
  return current 



# In the order of the todolist, we have achieved
# the maximum out of the first L <= K,
# take those as fixed and call liquidparser. Note that
# the configuration in which those are at their maxima and the others
# aren't may not actually work.
# Start the next one with those first sources at their maximum values.
def adjustsource(newsourcemap, bestmonoconfig, todolist):
 i = 0
 flag = True
 while(i < len(todolist)) and flag:
	p = todolist[i]
	if max(newsourcemap[p]) == bestmonoconfig[p]:
		newsourcemap[p] = [bestmonoconfig[p]]
	else: 
		flag = False
	i+= 1
 return newsourcemap

	
	

'''  # When transferring to Christophe
# DATA

# For simulator
	
	

# compatibilities= []
# compatibilities.append([1, 11, 13, 2, 21, 23])
# compatibilities.append([1, 11, 13, 3, 31, 33])
# compatibilities.append([1, 11, 13, 4, 41, 43])
# compatibilities.append([1, 16, 19, 2, 27, 29])
# compatibilities.append([1, 16, 19, 3, 37, 39])
# compatibilities.append([1, 16, 19, 4, 47, 49])
# compatibilities.append([2,21,24, 3, 31, 34])
# compatibilities.append([2,27,29, 3, 36, 39])
# compatibilities.append([2,21,24, 4, 41, 44])
# compatibilities.append([2,27,29, 4, 46, 49])
# compatibilities.append([3,31,34, 4, 41, 45])
# compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 18, 19, 2, 28, 29])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 18, 19, 3, 38, 39])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 18, 19, 4, 48, 49])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,28,29, 4, 48, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,38,39, 4, 48, 49])


compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 15, 15, 2, 24, 24])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 15, 15, 3, 34, 34])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 15, 15, 4, 44, 44])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 24, 24, 3, 34, 34])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 24, 24, 4, 44, 44])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 34, 34, 4, 44, 44])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 14, 17, 2, 25, 26])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 14, 17, 3, 35, 38])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 14, 17, 4, 45, 46])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,26,28, 4, 45, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 13, 2, 21, 24])
compatibilities.append([1, 14, 17, 2, 25, 26])
compatibilities.append([1, 11, 13, 3, 31, 34])
compatibilities.append([1, 14, 17, 3, 35, 38])
compatibilities.append([1, 11, 13, 4, 41, 44])
compatibilities.append([1, 14, 17, 4, 45, 46])
compatibilities.append([2,21,29, 3, 31, 39])
compatibilities.append([2,21,24, 4, 41, 44])
compatibilities.append([2,26,28, 4, 45, 49])
compatibilities.append([3,31,34, 4, 41, 45])
compatibilities.append([3,36,37, 4, 46, 49])

compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 19, 19, 2, 28, 28])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 19, 19, 3, 38, 38])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 19, 19, 4, 48, 48])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 28, 28, 3, 38, 38])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 28, 28, 4, 48, 48])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 38, 38, 4, 48, 48])

compatibilities= []
compatibilities.append([1, 11, 11, 2, 21, 21])
compatibilities.append([1, 12, 12, 2, 22, 22])
compatibilities.append([1, 15, 15, 2, 28, 28])
compatibilities.append([1, 11, 11, 3, 31, 31])
compatibilities.append([1, 12, 12, 3, 32, 32])
compatibilities.append([1, 15, 15, 3, 38, 38])
compatibilities.append([1, 11, 11, 4, 41, 41])
compatibilities.append([1, 12, 12, 4, 42, 42])
compatibilities.append([1, 15, 15, 4, 48, 48])
compatibilities.append([2, 21, 21, 3, 31, 31])
compatibilities.append([2, 22, 22, 3, 32, 32])
compatibilities.append([2, 28, 28, 3, 38, 38])
compatibilities.append([2, 21, 21, 4, 41, 41])
compatibilities.append([2, 22, 22, 4, 42, 42])
compatibilities.append([2, 28, 28, 4, 48, 48])
compatibilities.append([3, 31, 31, 4, 41, 41])
compatibilities.append([3, 32, 32, 4, 42, 42])
compatibilities.append([3, 38, 38, 4, 48, 48])

cudf= []
cudf.append([1, 11, 12, 2, 21])
cudf.append([1, 13, 15, 2, 24])
cudf.append([1, 16, 19, 2, 27])
cudf.append([1, 11, 12, 3, 31])
cudf.append([1, 13, 19, 3, 36])
cudf.append([1, 11, 12, 4, 41])
cudf.append([1, 13, 19, 4, 46])
cudf.append([2, 21, 22, 3, 31])
cudf.append([2, 23, 29, 3, 36])
cudf.append([2, 21, 24, 4, 41])
cudf.append([2, 25, 29, 4, 47])
cudf.append([3, 31, 34, 4, 41])
cudf.append([3, 35, 39, 4, 47])
cudf.append([4, 41, 42, 3, 31])
cudf.append([4, 43, 49, 3, 36])




orderofpackages = [1, 3, 4, 1, 2, 3, 4, 3, 2, 4]


# outside of the simulator


memory = {} # we will remember here the versions of package
	# combinations that don't work, so we don't redo them
	# we just keep exploring higher versions

strongmemory = [] # these will be in the form 
		# [callpack, callver, calleepack, calleever]

axiom = {} # we use the historicity and failure monotonicity axioms
 # each element is keyed by two packages and has the format
 # (pack1, version1, lesseq/eq/greatereq, pack2, version2, lesseq/eq/greatereq)



sourcemap = { 1: [11, 12, 13, 14, 15, 16, 17, 18, 19],
2: [21, 22, 23, 24, 25, 26, 27, 28, 29],
3: [31, 32, 33, 34, 35, 36, 37, 38, 39],
4: [41, 42, 43, 44, 45, 46, 47, 48, 49]}

default = {1:11,2:21, 3:31, 4:41} # configuration that works
default = {} # configuration that works

# constraints indicate low and high versions
# if no constraints, then take every one
# constraints = { 1: [12, 15], 2:[21,27]}
# map from package to low allowed version to high version inclusive
constraints = { 1: [11, 19], 2:[21,29]}
# constraints = { 1: [11, 15], 2:[21,21], 3:[38,38], 4:[40,49]}
# ok when True and 1: [11,14]
todolist = [3,1]

# EXECUTION

print "Start with this: ",default

endconfig = liquidclimber(constraints, todolist)
print "End with this: ",endconfig
print "successful: ",successful


''' # When transferring to Christophe
