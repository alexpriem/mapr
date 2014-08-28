
def Convert_RDToLatLong (x,y):
    # The city "Amsterfoort" is used as reference "Rijksdriehoek"
    # and WGS84 coordinate.
    referenceWgs84X=52.15517440
    referenceWgs84Y=5.38720621
    referenceRdX = 155000.0;
    referenceRdY = 463000.0;

    dX = (x - referenceRdX) * 10**-5
    dY = (y - referenceRdY) * 10**-5

    sumN = (3235.65389 * dY) + \
        (-32.58297 * dX**2) + \
        (-0.2475 * dY**2) + \
        (-0.84978 * dX**2 * dY) + \
        (-0.0655 * dY**3) + \
        (-0.01709 * dX**2) * dY**2 + \
        (-0.00738 * dX) + \
        (0.0053 * dX**4) + \
        (-0.00039 * dX**2 * dY**3) + \
        (0.00033 * dX**4 * dY) + \
        (-0.00012 * dX * dY)
    sumE = (5260.52916 * dX) + \
        (105.94684 * dX * dY) + \
        (2.45656 * dX * dY**2) + \
        (-0.81885 * dX**3) + \
        (0.05594 * dX * dY**3) + \
        (-0.05607 * dX**3 * dY) + \
        (0.01199 * dY) + \
        (-0.00256 * dX**3 * dY**2) + \
        (0.00128 * dX * dY**4) + \
        (0.00022 * dY**2) + \
        (-0.00022 * dX**2) + \
        (0.00026 * dX**5)

    latitude = referenceWgs84X + (sumN / 3600.0)
    longitude = referenceWgs84Y + (sumE / 3600.0)       
    return latitude, longitude



def Convert_LatLongToRD (latitude,longitude):
    # The city "Amsterfoort" is used as reference "Rijksdriehoek"
    # and WGS84 coordinate.
    referenceWgs84X=52.15517440
    referenceWgs84Y=5.38720621
    referenceRdX = 155000.0;
    referenceRdY = 463000.0;

    dX = (latitude - referenceWgs84X) * 0.36
    dY = (longitude - referenceWgs84Y) * 0.36

    sumN = (190094.945 * dY) + \
        (-11832.228 * dX*dY) + \
        (-114.221 * dX**2*dY) + \
        (-32.391 * dY**3) + \
        (-0.705 * dX) + \
        (-2.340 * dX**3 *dY) + \
        (-0.608 * dX* dY**3) + \
        (-0.008 * dY**2) + \
        (0.148 * dX**2 * dY**3)
     
    sumE = (309056.544 * dX) + \
        (3638.893 *  dY**2) + \
        (73.077 * dX**2) + \
        (-157.984 * dX * dY**2) + \
        (59.788 * dX**3) + \
        (0.433 * dY) + \
        (-6.439 * dX**2 * dY**2) + \
        (-0.032 * dX* dY) + \
        (0.092 * dY**4) + \
        (-0.054 * dX*dY**4) 

    x = referenceRdX + sumN 
    y = referenceRdY + sumE 
    return x, y



print Convert_RDToLatLong(122202,487250)
print Convert_LatLongToRD(52.372143838117,4.90559760435224)
print
print Convert_RDToLatLong(120700.723, 487525.501)
print Convert_LatLongToRD(52.37453253, 4.88352559)

print Convert_LatLongToRD(52.1158988,4.278153)
print Convert_LatLongToRD(51.8986194,4.4608443)


