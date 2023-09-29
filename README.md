# Four-Color-Map-For-GIS

The four-color graph theorem, when applied to GIS data, states that for any distribution of adjacent polygons there exists a solution such that all polygons can be colored with not more than four colors, and no two polygons with adjacent edges share the same color.  This tool applies the four-color theorem for GIS data.


This tool accepts a shapefile, geopackage, or a file geodatabase feature class and returns a CSV file.  The CSV file can be joined to the spatial data using your data's FID/OID with the CSV column called row_num.  A column in the CSV called color can be used to symbolized polygons with the returned four-color theorem solution.


 Special thanks to Ali Assaf of McGill University for the four-color Python code as posted to StackOverflow.  GIS adaption by GB Gabrisch, Lummi GIS.


There will be multiple solutions to any polygon distribution, and some solutions may be skewed towards a few color choices.  Since Ari’s code can return an unfathomable number of solutions to the four-color theorem I sift through a subset of the solutions and pick a solution with the most equal distribution of colors for a nicer cartographic effect.


This tool requires the OSGEO - GDAL/OGR Python Library which is included with ArcGIS Pro and a standard installation of QGIS.  This tool is not GIS software, nor operating system specific and should work on any platform with OGR and a standard Python 3 installation.


Gotchas:

-No multi-part polygon geometries allowed.

-Geometries must share verticies to determin adjaceny so no sloppy data with gaps between polygons allowed.

-Self intersecting polygons throw errors but running a Repair Geometry in ArcGIS Pro solved that issue with test data.

-QGIS cares not for shapefile FID columns like ArcGIS.  If you are using QGIS you will need to build  some OID data in your shapefile attribute table for the final join.

-The possible solutions can be extensive so some processing power is required.

-There are too may possibilites to test.  Let me know if you encounter oddites or errors.  There is a test dataset included that is working.

-See here to install osgeo (gdal and ogr) for a non QGIS/ArcGIS pro installation of Python:  https://pypi.org/project/GDAL/

-The solution limit argument shown below was choosen arbitrarily.  IF you are unhappy with your four-color distribution I suggest increasing that number to 1,000 and rerun.

-I make no attempt to sort out CSV files overwriting, etc.  Choose your output names wisely.

To run -

Open in your favorite Python IDE.  Change the arguments as shown below.  Execute and wait.

        ################   set arguments below ##############
        
        #this is the path to the polygon data.....
        
        in_fc = r"C:\gTemp\fourcolortestdata\states.shp"
        
        #this is the path to the out csv file.
        
        out_csv = r"C:\gTemp\fourcolortestdata\statesArcGIS.csv"
        
        #driver choices are  'GKPG', 'ESRI Shapefile', or 'FileGDB'
        
        driver = 'ESRI Shapefile'
        
        #There can be unfathomable solutions to a 30 polygon distribution.  Limit the number of solutions to prevent endless processing.
        
        solution_limit = 100
        
         ##############################################
