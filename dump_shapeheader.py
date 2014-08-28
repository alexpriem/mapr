import shapefile
import os, sys




separator=';'


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

print varnames
