import shapefile
import os, sys

separator=','

if len(sys.argv)<2:
    print 'geen args'
    sys.exit()
if len(sys.argv)<3:
    f=sys.stdout
else:
    fname=sys.argv[2]
    f=open(fname,'w')

sf = shapefile.Reader(sys.argv[1])

varnames=[]
for fld in sf.fields[1:]:
    varnames.append(fld[0])

l=[ '"'+v+'"'  for v in varnames]
header=separator.join(l)
f.write(header+'\n')

records=sf.records()
nr=0
for r in records:
    if (nr % 1000)==0:
        print nr
    txt=''
    for col in r:    
        if type (col)==str:
            txt+='"'+col+'"'+separator
        else:
            txt+=str(col)+separator
    f.write(txt[:-1]+'\n')
    nr+=1
