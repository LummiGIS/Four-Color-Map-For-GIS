#!/usr/bin/env python3
import traceback
import sys
from itertools import product
import numpy
from osgeo import ogr
from itertools import count

try:
    
    def solve(X, Y, solution):
        if not X:
            yield list(solution)
        else:
            c = min(X, key=lambda c: len(X[c]))
            Xc = list(X[c])
    
            for r in Xc:
                solution.append(r)
                cols = select(X, Y, r)
                for s in solve(X, Y, solution):
                    yield s
                deselect(X, Y, r, cols)
                solution.pop()
    def select(X, Y, r):
        cols = []
        for j in Y[r]:
            for i in X[j]:
                for k in Y[i]:
                    if k != j:
                        X[k].remove(i)
            cols.append(X.pop(j))
        return cols
    
    
    def deselect(X, Y, r, cols):
        for j in reversed(Y[r]):
            X[j] = cols.pop()
            for i in X[j]:
                for k in Y[i]:
                    if k != j:
                        X[k].add(i)
    def exact_cover(X, Y):
        newX = dict((j, set()) for j in X)
        for i, row in Y.items():
            for j in row:
                newX[j].add(i)
        return newX
    
    
    def colour_map(nodes, edges, ncolours=4):
        colours = range(ncolours)
        #The edges that meet each node
        node_edges = dict((n, set()) for n in nodes)
        for e in edges:
            n0, n1 = e
            node_edges[n0].add(e)
            node_edges[n1].add(e)
    
        for n in nodes:
            node_edges[n] = list(node_edges[n])
        #Set to cover
        coloured_edges = list(product(colours, edges))
        X = nodes + coloured_edges
        #Subsets to cover X with
        Y = dict()
        #Primary rows
        for n in nodes:
            ne = node_edges[n]
            for c in colours:
                Y[(n, c)] = [n] + [(c, e) for e in ne]
        #Dummy rows
        for i, ce in enumerate(coloured_edges):
            Y[i] = [ce]
        X = exact_cover(X, Y)
        #Set first two nodes
        partial = [(nodes[0], 0), (nodes[1], 1)]
        for s in partial:
            select(X, Y, s)
        
        
        for s in solve(X, Y, []):
            s = partial + [u for u in s if not isinstance(u, int)]
            s.sort()
            yield s
            
        
    
    
    
    def get_adjacent_polygons(inFC, driver):
        '''returns a list of tuples where for each tuple element 0 = fid of the record
        and element 1 is the fid of an adjacent polygon that shares an edge.'''
        #set the ogr driver as text...
        #geopackages have different start values for their FIDs so set that here.
        if driver == "GPKG":
            fid_start = 1
        if driver == "ESRI Shapefile":
            fid_start = 0
        if driver == "FileGDB":
            fid_start = 0
            
        #set the ogr driver and open the file    
        driver = ogr.GetDriverByName(driver)
        dataSource = driver.Open(inFC, 0)
        layer = dataSource.GetLayer()
        #create lists to store the well-known text representation of the data and the adjacent fids
        wkt = []
        adjacent_list = []
        #get WKT
        for feature in layer:
            geom = feature.GetGeometryRef()
            wkt.append(geom.ExportToWkt())
        #count the number of records
        total_polygon_count = len(wkt)-1
        start_index = fid_start
        end_index = start_index + 1
        
        #use ogr to test for adjacenty by returning/determining the intersecting nodes for each record
        while start_index != total_polygon_count:
            print("working on  ", start_index, " ", end_index)
            
            poly1 = ogr.CreateGeometryFromWkt(wkt[start_index])
            poly2 = ogr.CreateGeometryFromWkt(wkt[end_index])
            intersection = poly1.Intersection(poly2)
            intersection2 = intersection.ExportToWkt()
            geom = ogr.CreateGeometryFromWkt(intersection2)
            #a returned linestring means adjaceny as opposed to a single point.
            print(geom.GetGeometryName())
            if geom.GetGeometryName() =='LINESTRING' or geom.GetGeometryName() == "MULTILINESTRING":
                adjacent_list.append((start_index, end_index))
            end_index  +=1
            if end_index == total_polygon_count + 1:
                start_index +=1
                end_index = start_index + 1
        #full_list = []
        #print(adjacent_list)
        #for item in adjacent_list:
            #full_list.append(item)
            #full_list.append((item[1], item[0]))
        return adjacent_list    
    
    def write_csv(out_csv, in_list):
        '''converts the best four color solution to a csv file...
        where in_csv is a path to a new csv file and the in_list looks like this
        [('FID', 'COLOR'), (0,1), (1,3), (2,4), (3,3)]'''
        #convert the list to a numpy array...
        rows = numpy.array(in_list)
        numpy.savetxt(out_csv, rows, delimiter =", ",fmt ='% s')    
    
    def get_row_count(in_fc):
        '''returns the number of rows in a feature class'''
        openfc = ogr.Open(in_fc)
        row_count = openfc.GetLayerCount()
        for fcIdx in range(0, row_count):
            fc = openfc.GetLayer(fcIdx)
        row_count = fc.GetFeatureCount()
        return row_count    
    
    
    def build_input_polygons(row_count, driver):
        '''Ari's four-color theorem code requires a list of tuples for each input polygon 
        of the form [(0, none),(1, None)...] so build that'''
        if driver == 'GKPG':
            counter = 1
            row_count +=1
        else:
            counter = 0
        
        input_polygons = []
        while counter < row_count:
            input_polygons.append((counter, None))
            counter +=1
        return input_polygons
    def choose_best_distribution(all_solutions):
        '''Given a list of a list of tuples find 
        that item that has the lowest standard deviation
        in the second item in each tuple.
        Then return that item'''
        #make a placeholder to identify the lowest standard deviation
        #make an empty list to store the final solution
        best_distribution = []
        best_std = 2
        #iterate all of the solutions one at a time.
        for i in all_solutions:
            #Use list comprehension to get a new list of only the second tuple elements
            result =[item[1] for item in i]
            #cast to a numpy array and build the 4 bins and the related histogram
            result = numpy.array(result)
            hist1,bins = numpy.histogram(result, 4)
            #get the standard deviation for this solution
            std = numpy.std(hist1)
            #check to see if this solution is more evenly distributed
            #if so, save as a possible best solution
            if std <= best_std:
                best_std = std
                best_distribution = i
        return best_distribution    
    
    
    
    
    def build_list_for_conversion(in_list, driver):
        '''add the necessary csv first row information to the 
        best solution list...'''
        #geopackages FIDs index starting at 1 so add 1 to the FID element in the list...
        if driver == "GPKG":
            in_list = [(a + 1, b) for a, b in in_list]
        print(in_list)
        #Add the CSV first row to allow for joining and symbolizing in ArcGIS or QGIS...
        first_item = ('row_num', 'COLOR')
        in_list.insert(0, first_item)
        return in_list    
    
    
    def get_enough_solutions(all_solutions, solution_limit):
        enough_solutions = []
        solution_count = 0
        for solution in all_solutions:
                solution_count +=1
                if solution_count ==solution_limit:
                    break
                else:
                    enough_solutions.append(solution)        
        return enough_solutions



    def main (in_fc, out_csv, driver, solution_limit):
        print('Running Four Color Map Tool for GIS by Gerry Gabrisch, GISP.  geraldg@lummi-nsn.gov')
        
        print('Get adjacenct polygons list...')
        adjacent_polygons_graph = get_adjacent_polygons(in_fc, driver)
    
        print("Counting records in input data...")
        row_count = get_row_count(in_fc)
        
        print("Build input polygons list...")
        input_polygons = build_input_polygons(row_count, driver)
    
        print("Extracting the nodes list...") 
        nodes = [t[0] for t in input_polygons]
    
        print("Getting all solutions...this could take a while so hold on!")
        all_solutions = colour_map(nodes, adjacent_polygons_graph, ncolours=4)
    
        print("Getting a subset of all the possible solutions..." )
        #A few dozen polygons can return tens of thousands of possible solutions.  
        enough_solutions = get_enough_solutions(all_solutions, solution_limit)
        
        print("Converting all solutions to Python list...")
        solution_list = list(enough_solutions)
        
        print("Choosing the best distribution from all solutions...")
        best_solution = choose_best_distribution(solution_list)
        
        print("Build list for conversion...")
        best_solution = build_list_for_conversion(best_solution, driver)
        
        print("Writing the CSV file...")
        write_csv(out_csv, best_solution)
        
        print('Four Color Mapping finished without error')
        
    if __name__ == "__main__":
        
        ############################################   set arguments below #####################################################
        
        #this is the path to the polygon data.....
        in_fc = r"C:\gTemp\fourcolortestdata\states.shp"
        #this is the path to the out csv file.
        out_csv = r"C:\gTemp\fourcolortestdata\statesArcGIS.csv"
        #driver choices are  'GKPG', 'ESRI Shapefile', or 'FileGDB'
        driver = 'ESRI Shapefile'
        #There can be unfathomable solutions to a 30 polygon distribution.  Limit the number to prevent endless processing.
        solution_limit = 100
        
        ########################################################################################################################
        
        main (in_fc, out_csv, driver, solution_limit)  
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    print ("PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1]))