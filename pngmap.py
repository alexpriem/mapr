import matplotlib as mp
mp.use('TkAgg') # speedup matplotlib
from matplotlib import pyplot
from math import log, log10, sqrt
from pylab import axes
import argparse, sys, datetime, math, time
import shpUtils
import datetime



class mapmaker():
    def __init__(self, args):

        args=self.check_args(args)
        
        for k,v in args.items():
            setattr(self,k,v)
                
        self.shaperecords=None
        self.minx=None
        self.maxx=None
        self.miny=None
        self.maxy=None


    def check_args(self, args):    # alleen defaults zetten.

        defaults=[
            ['csvfile',';',True,''],                
            ['recordinfo','',True,''],
            ['sep',';',False,''],
            ['outfile','',True,''],

            ['datesel','',False,''],
            
            ['shapefile','',True,''],
            ['shape_key','',True,''],
            ['shape_normalize',None,False,''],
            ['shape_borderwidth',0.5,False,''],
            ['shape_bordercolor',(0x50,0x50,0x50),False,''],
            
            
            ['outline_shapefile','',True,''],
            ['outline_key','',True,''],
            ['outline_borderwidth',1.5,False,''],
            ['outline_bordercolor',(0x28,0x28,0x28),False,''],

            ['width',8,False,''],
            ['height',8,False,''],
            ['offset_x',0.0,False,''],
            ['offset_y',0.0,False,''],
            ['zoom',None,False,''],
            ['backgroundcolor','#dedede',False,''],        

            ['colorbar_x', 0.86,False,''],
            ['colorbar_y', 0.70,False,''],
            ['xlabel',None,False,''],
            ['ylabel',None,False,''],
            ['title',None,False,''],
            ['ticks',None,False,''],
            ['ticklabels',None,False,''],
                    
            ['gradient_transform','log10',False,''],            
            ['gradient_min',0,False,''],
            ['gradient_max','max',False,''],
            ['gradient_steps',40,False,''],
            ['missing_color',(1,1,1),False,''],

            ['movie',False,False,''],
            ['movie_start',None,False,''],
            ['movie_end',None,False,''],
        ]


        default_colormaps=['blue','gray',
                           'cbs_blue','cbs_green', 'cbs_red', 'cbs_hot',
                            'terrain', 'coolwarm',
                            'hot', 'hot2','ygb']
        colormap=args.get('colormap','cbs_blue')
        if colormap not in default_colormaps:
            raise RuntimeError ('allowed colormaps: %s' % default_colormaps)

        default_transforms=['linear','sqrt','log2','log10']
        transform=args.get('transform','linear')
        if transform not in default_transforms:
            raise RuntimeError ('allowed colormaps: %s' % default_transforms)


                           
        for varinfo in defaults:
            varname=varinfo[0]
            defaultval=varinfo[1]
            required=varinfo[2]
            helptxt=varinfo[3]
            
            if not (varname in args):
                if required:
                    raise RuntimeError('Missing %s' % varname)
                args[varname]=defaultval
        return args 


    

    def load_shapefile(self,infile):
        self.shaperecords=shpUtils.loadShapefile(infile)
        return self.shaperecords


    def autoscale (self, zoom=None):
        if zoom is not None:
            minx=zoom[0][0]
            miny=zoom[0][1]
            maxx=zoom[1][0]
            maxy=zoom[1][1]
        else:
            minx=None
            maxx=None
            miny=None
            maxy=None

            shpRecords=self.shaperecords
            for i in range(0,len(self.shaperecords)):
                polygons=shpRecords[i]['shp_data'].get('parts',{})
                for poly in polygons:
                    for point in poly['points']:
                        tempx=float(point['x'])
                        tempy=float(point['y'])
                        if minx is None or tempx<minx:
                            minx=tempx
                        if miny is None or tempy<miny:
                            miny=tempy
                        if maxx is None or tempx>maxx:
                            maxx=tempx
                        if maxy is None or tempy>maxy:
                            maxy=tempy
                            
        self.dx=maxx-minx
        self.dy=maxy-miny
        self.minx=minx
        self.maxx=maxx
        self.miny=miny
        self.maxy=maxy
        dxy=(self.dx-self.dy)/2.0
        if dxy<0:
            self.minx+=dxy
            self.maxx-=dxy
        else:            
            self.miny-=dxy
            self.maxy+=dxy


    def transform_val (self, val):
        transform=self.gradient_transform        
        transform_val=val
        if transform=='log':
            if val>0:
                transform_val=log(val)
            if val<0:
                transform_val=log(-val)
                
        if transform=='log10':        
            if val>0:
                transform_val=log10(val)
            if val<0:
                transform_val=log10(-val)

        if transform=='sqrt':
            if val>0:
                transform_val=sqrt(val)
            if val<0:
                transform_val=sqrt(-val)
        val=transform_val
        return val

    def rescale_color (self, val, debug=False):

        transform=self.gradient_transform
        minval=self.gradient_min
        maxval=self.gradient_max
        if debug and val!=0:
            print val,minval,maxval, transform
            
        if val is None:
            return self.missing_color

        
        transform_val=val
        if transform=='log':
            if val>0:
                transform_val=log(val)
            if val<0:
                transform_val=-log(-val)

        if transform=='log10':         
            if val>0:
                transform_val=log10(val)                
            if val<0:
                transform_val=-log10(-val)

        if transform=='sqrt':
            if val>0:
                transform_val=sqrt(val)
            if val<0:
                transform_val=-sqrt(-val)
        val=transform_val

        if val<minval:
            val=minval
        if val>maxval:
            val=maxval
                    
        if debug and val!=0:
            print 'transform:', val
        val=(val-minval)/(1.0*(maxval-minval))   # range van 0 tot 1
        if debug and val!=0:
            print 'preranged val:', val
        val=int(self.gradient_steps*val)/(self.gradient_steps*1.0)
        if debug and val!=0:
            print 'ranged val:', val
        colorval=(1-val,1-val,1)
        return colorval


    def plot_shapefile (self, shpRecords, mapdata, field_id, graph, bordercolor, borderwidth, fill=True):

        #print bordercolor, borderwidth, fill
        if shpRecords is None:
            shpRecords=self.shaperecords            
        if self.minx is None:
            self.autoscale(shpRecords)
        normalize=self.shape_normalize                    
            

        bordercolor=[c/255.0 for c in bordercolor]        
        for i in range(0,len(shpRecords)):
            dbfdata=shpRecords[i]['dbf_data']            
            shape_id=dbfdata.get(field_id)
            
            colorval=None
            if shape_id is not None:
                val=mapdata.get(int(shape_id),0)
                if normalize:
                    normalize_val=dbfdata.get(normalize)
                    val=val/normalize_val
               # print shape_id,val
                colorval=self.rescale_color(val,False)
            #    print shape_id, mapdata[shape_id], colorval
            polygons=shpRecords[i]['shp_data'].get('parts',{})
            for shape_nr, poly in enumerate(polygons): 

                #print i,shape_nr
                xList = []
                yList = []                  
                point=poly['points'][0]        
                tempx = float(point['x']) # + self.offsetx
                tempy = float(point['y']) # + self.offsety
                xList.append(tempx)
                yList.append(tempy)
                for point in poly['points']:
                    tempx = float(point['x']) # + self.offsetx 
                    tempy = float(point['y']) # + self.offsety
                    xList.append(tempx)
                    yList.append(tempy)
                if (colorval is not None) and (fill==True):
                   # print 'fill',colorval                    
                    h=graph.fill(xList, yList, facecolor=colorval, edgecolor=bordercolor, linewidth=borderwidth)
                  #  print xList[1], yList[1]
                else:
                    l=graph.plot(xList, yList, color=bordercolor, linewidth=borderwidth)
    












    # csv-file inlezen.
    # afhankelijk van args/date keuzes maken:
    # movie ->  serie maps maken, op basis van alle in data aanwezige datums
    # geen movie, wel datum: selecteer map op basis van 'datesel', of anders
    #                           eerste datum
    # 
    # zet maxdata
    # zet geselecteerde datum

    def read_csvfile(self):

        print 'reading data'
        datadict={}
        regiodict={}
        csvfile=self.csvfile
        recordinfo=self.recordinfo
        f=open (csvfile)
        f.readline()
        
        
        recs=recordinfo.strip().split(',')
        regiocol=recs.index('regio')
        datacol=recs.index('data')
        datecol=None
        if 'date' in recs:
            datecol=recs.index('date')
        
        
        maxval=None
        minval=None
        for line in f.readlines():        
            cols=line.strip().split(',')
            val=int(cols[datacol])
            if maxval is None or val>maxval:
                maxval=val
            if minval is None or val<minval:
                minval=val
                
            regio=int(cols[regiocol])   # aanname: regio is int.
            if datecol is None:
                regiodict[regio]=float(cols[datacol])
            else:
                date=cols[datecol]            
                regiodict=datadict.get(date,{})
                regiodict[regio]=float(cols[datacol])    
                datadict[date]=regiodict

        # loop done


        if self.movie==True:
            if self.gradient_max=='min':                
                self.gradient_min=niceround(minval)
            if self.gradient_max=='max':
                self.gradient_max=self.niceround(maxval)
            return datadict
        
        # geen movie, geen datumcol        
        if datecol is None:
            if self.gradient_max=='min':
                minval=min(regiodict.values())
                self.gradient_min=niceround(minval)
            if self.gradient_max=='max':
                maxval=max(regiodict.values())
                self.gradient_max=self.niceround(maxval)
            return regiodict
        # wel datumcol, evt. datumselectie; geen datumselectie, 1e datum
        if self.datesel is None:
            self.date=datadict.keys()[0]
        else:
            self.date=self.datesel
            
        mapdata=datadict[self.date]             
        if self.gradient_max=='min':
            minval=max(mapdata.vals())
            self.gradient_min=niceround(minval)
        if self.gradient_max=='max':
            maxval=max(mapdata.vals())
            self.gradient_max=niceround(maxval)

        return datadict
        





    def save_map (self, mapdata):


        t0=datetime.datetime.now()        
        map_shp=self.load_shapefile(self.shapefile)
        self.autoscale(self.zoom)
        
        fig = pyplot.figure(figsize=(8, 8), dpi=self.resolution )    
        ax = fig.add_subplot(1,1,1)
        
        ax.set_xlim (self.minx, self.maxx)
        ax.set_ylim (self.miny, self.maxy)
        ax.axis('off')
        
        title=self.title
        date=self.dateselection
        if date is not None:
        
            dt=time.strptime(date,self.date_input_format)
            movie_txt=time.strftime(self.date_print_format,dt)    
        
            movie_x=float(self.label_x)
            movie_y=float(self.label_y)
            fig.text (movie_x,movie_y,movie_txt)
        
        title_x=getattr(self,'title_x',0.5-len(self.title)*0.0075)
        title_y=getattr(self,'title_x',0.95)
        
        fig.text (title_x,title_y,self.title)

        self.data_max=self.gradient_max
        self.data_min=self.gradient_min
        self.gradient_max=self.transform_val(self.gradient_max)
        self.gradient_min=self.transform_val(self.gradient_min)
        
        #colormap toevoegen            
        self.plot_shapefile(map_shp,mapdata, self.shape_key, ax, self.shape_bordercolor, self.shape_borderwidth, fill=True)

        outline_shp=self.load_shapefile(self.outline_shapefile)
        borderwidth=self.outline_borderwidth
        bordercolor=self.outline_bordercolor
        self.plot_shapefile(outline_shp,mapdata, self.outline_key, ax, self.outline_bordercolor, self.outline_borderwidth, fill=False)

        
        colorbar_x=self.colorbar_x
        colorbar_y=self.colorbar_y
                
    # colorbar
        colorsteps=self.gradient_steps
        ax1 = axes([colorbar_x, colorbar_y, 0.05, 0.20], axisbg='y')        
        colorlist=[]
        maxdata=self.data_max
        logstep=math.log10(maxdata)/(colorsteps*1.0)    
        for i in range (0,colorsteps):
            val=pow(10,i*logstep)    
            colorlist.append(self.rescale_color (val, debug=False))    
        cmap = mp.colors.ListedColormap(colorlist,'grad',colorsteps)
        norm = mp.colors.LogNorm(vmin=1, vmax=maxdata)


        ticks=self.ticks
        if ticks is None:        
            if maxdata==1000:
                ticks=[1,5,10,250,1000]
            if maxdata==5000:
                ticks=[1,5,50,500,5000]
            if maxdata==10000:
                ticks=[1,10,100,1000,10000]    
            if maxdata==50000:
                ticks=[1,5,50,500,5000,50000]    
            if maxdata==100000:
                ticks=[1,100,10000,100000]    
            if maxdata==500000:
                ticks=[1,50,5000,500000]    
            if maxdata==1000000:
                ticks=[1,100,10000,1000000]    
            if maxdata==5000000:
                ticks=[1,500,50000,5000000]    

        
        cb=mp.colorbar.ColorbarBase(ax1,
                                        cmap=cmap,
                                        norm=norm,
                                        ticks=ticks,
                                        format='%.0f',
                                        spacing='proportional',
                                        orientation='vertical')        
                     
        if self.ticklabels is not None:
            cb.set_ticklabels(self.ticklabels)    

        plot_ts=getattr(self,'plot_ts',None)
        if  plot_ts==True:
            ax2 = axes([0.1, 0.05, 0.80, 0.15], axisbg='white', frameon=0)
    #http://matplotlib.org/users/recipes.html     voor datess


            t_axis=[]
            y_axis=[]
            for date in sorted(ts.iterkeys()):        
                y=int(date[:4])
                m=int(date[4:6])
                d=int(date[6:8])
                t_axis.append(datetime.date(y,m,d))
                y_axis.append(ts[date])
            pyplot.locator_params(axis = 'y', nbins = 4)
            pyplot.plot(t_axis, y_axis, color='blue')

        # highlight current date point in ts
        
            currentdate=self.dateselection
            pointx=[dt]
            pointy=[ts[currentdate]]
            pyplot.plot(pointx, pointy, color='red', marker='o',fillstyle='full', markersize=5)

            if self.movie==True:
                self.outfile+='_'+currentdate
            print 'save:',self.outfile, maxdata
            
        pyplot.savefig(self.outfile+'.png', dpi=self.resolution, facecolor=self.backgroundcolor)
        pyplot.close()
        





    def niceround(self, val):
        upper_lim=[0,5,10,50,100,500,1000,5000,10000,50000,100000,500000,1000000]
        prev=upper_lim[0]
        for v in upper_lim[1:]:
           # print v, prev
            if val>=prev and val<v:
                return v
            prev=v
            
        return None




    def makemap(self):
                
        mapdata=self.read_csvfile()
        if self.movie==False:
            self.save_map (mapdata)    
        else:        
            self.nr=0
            for date,mapdata_day in mapdata.items():
                self.nr+=1
                self.date=date                
                self.save_map(day_mapdata)
            
        

        

