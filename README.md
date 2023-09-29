# Four-Color-Map-For_GIS

Accepts a shapefile, geopackage, or a file geodatabase feature class and returns a CSV file.  The CSV file can be joined to the spatial data using your data's FID/OID with the CSV column row_num.  A column in the CSV called color can be used to symbolized polygons the returned four-color theorem solution.

The four-color graph theorem, when applied to GIS data, states that for any distribution of adjacent polygons there exists a solution such that all polygons can be colored with not more than four colors, and no two polygons with adjacent edges share the same color.

Four-color Python code thanks to Ali Assaf of McGill University as posted to StackOverflow.  GIS adaption by GB Gabrisch, Lummi GIS.

This geoprocessing tool  will accept a geopackage, shapefile, or a file geodatabase feature class and return a CSV file that satisfies the four-color theorem.  The CSV file can be joined back with the polygon data FID (or OID).  The resulting color attribute holds values of 0 - 3.  These attributes can be used to symbolize your data unique values with four colors.  

There will be multiple solutions to any polygon distribution, and some solutions may be skewed towards a few color choices.  Since Ari’s code can return an unfathomable number of solutions to the four-color theorem I sift through a subset of the solutions and pick a solution with the most equal distribution of colors for a nicer cartographic effect.

This tool requires the OSGEO - OGR Python Library which is included with ArcGIS Pro and a standard installation of QGIS.  This tool is not GIS software, nor operating system specific and should work on any platform with OGR and a standard Python 3 installation.

Gotchas:
-No multi-part polygons allowed.
-Geometries must share verticies to determin adjaceny so no sloppy data with gaps between polygons allowed.
-Self intersecting polygons throw errors but running a Repair Geometry in ArcGIS Pro solved that issue.
-QGIS cares not for shapefile FID columns like ArcGIS does.  If you are using QGIS you will need to build a some OID data for the final join.
-The possible solutions can be extensive so some processing power is required.

To run -
Open in your favorite Python IDE.  Change the arguments as shown below.  Execute and wait.

 ############################################   set arguments below #####################################################
        
        #this is the path to the polygon data.....
        in_fc = r"C:\gTemp\fourcolortestdata\states.shp"
        #this is the path to the out csv file.
        out_csv = r"C:\gTemp\fourcolortestdata\statesArcGIS.csv"
        #driver choices are  'GKPG', 'ESRI Shapefile', or 'FileGDB'
        driver = 'ESRI Shapefile'
        #There can be unfathomable solutions to a 30 polygon distribution.  Limit the number of solutions to prevent endless processing.
        solution_limit = 100
        
        ########################################################################################################################
