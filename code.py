from geopy.distance import great_circle
from numpy import loadtxt, concatenate

granularity = 1;
degrees_around = 1 # Change me to even 11!!

def get_nearest_point(src_coord, points):
        """
        src_coord: one points
        points: grid of points
        """
#       print ""
#	print "Data point " + str(src_coord)
        x = int(round(src_coord[0].astype('float') * granularity)) # x = center latitude
        y = int(round(src_coord[1].astype('float') * granularity)) # y = center longitude
        nearby_points = []
        offset = 0
	offset_limit = granularity * degrees_around # This is where it should look
        max_offset = offset_limit # This is where it is willing to look
# offset is not in grid, but in sqaures of grid

        # only search for the points in the nearby grid cells, in a square in which "radius" is "offset"
        while offset <= offset_limit:
#                print "Offset: " + str(offset)
                # check a square around the data point
		x_r = range (x-offset, x+offset+1) # x_r is latitude range 
#		print x_r
#range function doesnt include last point, hence we add 1 (range 9 = 0 - 9)
#x+1 is never returned.. so its just x
		for i in x_r: # i is latitude
#range only 
			if not i in points:
				continue # whole latitude empty, look in another one
# for x latitude , there is no longtitude
			if (i == x-offset or i == x+offset):
				y_r = range (y-offset, y+offset+1) # y_r is longitude range
#				print y_r
#29 and 6
#offset is 1
#bottom fo range is 28 (5, 6, 7)
#29 (5,7)
#30 (5,6,7)

#29 16
#radius/offset is 10
#start at 19 (6 to 26)
#20 (6, 26)
#21 (6 to 26)
#entire range
			else:
				y_r = [y-offset, y+offset]
#				print y_r
#else just the 2 extreme points (the 1st and the last)
#only check the borders, not the sqaure..
#explain:start 29,6 - no point in center box
#expand offset by 1
#now check for all 8 boxes
#Summary:constructed a list on this latitude

                        for j in y_r: # j is longitude
# Check all longitudes for each of the latitudes..
				if not j in points[i]:
					continue # this grid position is empty, 
#                                        print "Trying " + str(i) + "," + str(j) + ": "
                                nearby_points.extend(points[i][j]) #add to list of candidates of nearby points
#                                print points[i][j];
                                if offset_limit == max_offset: # this is the first box which was not empty
#					print offset_limit
					offset_limit = min (int (offset * 1.5 + 2), max_offset)
#offset * sqrt2 (adjust for sin45)
#					+1 to round up
#					+1 to compensate for the initial point being far from the grid point
#actually 1 is enough, but 2 for safety, for super optimality, make it 1.
#the extra 1 is to make up for the odd points.
#However, cannot compensate for a point like 90,6...
#                                        print "New limit: " + str(offset_limit)
                offset = offset + 1
#make the offset bigger
        if 0 == len (nearby_points): # check if bucket is zero, (just in case).....
		print "Point " + str (src_coord) + " does not have any neighbor in " + str (degrees_around) + " degrees around it"
		return ("ERROR", 0, 0)
	distances = [great_circle(src_coord, (point[1],point[2])).meters for point in nearby_points]
# create list of distances
	distance = min(list(enumerate(distances)), key=lambda x:x[1])
# select the minimun of those distances, key = lambda--> how we extract the index for the list
	return nearby_points[distance[0]]


def join_files(ucrs, data):
    for data_ind in xrange(len(data)):
	data_point = data[data_ind]
	coords = (data_point[10], data_point[11])
#data_ind is data index

#expensive tasks - lot of points or empty (hence search time is more)
#	if 20 <= data_point[0] <= 45: 
	if data_point[3] == "Spain":     
#dont refer as data, maybe a conflict !!  
            nearest_point = get_nearest_point(coords, points)
#28.5, 5.5
#check 29,6
#build a list of nearby points to check
	    print ",".join(concatenate((data[data_ind], [nearest_point[0]], nearest_point[1:3])))
	else:
	    print ",".join(concatenate((data[data_ind], ["GPS location outside Spain"])))

def make_tuple (p):
        return (p[0], p[4], p[5])
#put smaller boxes for each point inside the box (each point is a tuple)

def print_points (points):
	for x in points:
	    print x
	    for y in points[x]:
		print "   " + str (y) + ": " + str(points[x][y])

#Can be removed if required, shows the grid structure, uncomment it..

if __name__ == '__main__':
	data = loadtxt('data.csv', delimiter=',', dtype='str')
	ucrs = loadtxt('ref.txt', delimiter='|', dtype='str')
	points={}
#Dictionary - data structure (like an array, index can be any type of data, in this case integers) - contains the long (each column has a lat)
#Eg: 44,0)  - take 44 first, get all long data (columns) of lat 44
#    if granularity 10, 44,0 - 440,0
#		to have a limited no of points in each grid location.
#more dense, more granularity to add.
        for p in ucrs:
                x = int(round(p[4].astype('float')*granularity))
                y = int(round(p[5].astype('float')*granularity))
#Add the granularity to the grid
                if not x in points:
			points[x] = {} # No point on that latitude yet
		if not y in points[x]:
			points[x][y] = [] # create a grid
		points[x][y].append(make_tuple(p))
#insert the point in the grid
#Basically, spread the reference points, search for a limited area 
#	print_points (points) 
        join_files(points, data)
#	print_points(points)
