from geopy.distance import great_circle
from numpy import loadtxt, concatenate

#data = loadtxt('/home/spark/JourneyFiles/MNJourneysEven_20130101-20130131.csv', delimiter=',', dtype='str')

granularity = 300;
degrees_around = 11 # HEY! Change me to 11!!

def get_nearest_point(src_coord, points):
        """
        src_coord: one points
        points: grid of points
        """
#        print ""
#	print "Data point " + str(src_coord)
        x = int(round(src_coord[0].astype('float') * granularity))
        y = int(round(src_coord[1].astype('float') * granularity))
        nearby_points = []
        offset = 0
	offset_limit = granularity * degrees_around
        max_offset = offset_limit

        # only search for the points in the nearby grid cells, in a square which "radius" is "offset"
        while offset <= offset_limit:
#                print "Offset: " + str(offset)
                # check a square around the data point
		x_r = range (x-offset, x+offset+1)
                for i in x_r:
			if not i in points:
				continue # whole latitude empty, look in another one
			if (i == x-offset or i == x+offset):
				y_r = range (y-offset, y+offset+1)
			else:
				y_r = [y-offset, y+offset]
                        for j in y_r:
				if not j in points[i]:
					continue # this grid position is empty, 
#                               print "Trying " + str(i) + "," + str(j) + ": "
                                nearby_points.extend(points[i][j])
#                               print points[i][j];
                                if offset_limit == max_offset:
					offset_limit = min (int (offset * 1.5 + 2), max_offset)
#					+1 to round up
#					+1 to compensate for the initial point being far from the grid point
#                                       print "New limit: " + str(offset_limit)
                offset = offset + 1
        if 0 == len (nearby_points):
		print "Point " + str (src_coord) + " does not have any neighbor in " + str (degrees_around) + " degrees around it"
		return ("ERROR", 0, 0)

        distances = [great_circle(src_coord, (point[1],point[2])).meters for point in nearby_points]
        distance = min(list(enumerate(distances)), key=lambda x:x[1])
        return nearby_points[distance[0]]


def join_files(ucrs, data):
        data_points = zip(data[:,1].astype('float'), data[:, 2].astype('float'))

        for data_ind in xrange(len(data_points)):
                data_point = data_points[data_ind]
                nearest_point = get_nearest_point(data_point, points)

                print ",".join(concatenate((data[data_ind], [nearest_point[0]], nearest_point[1:6])))

def make_tuple (p):
        return (p[0], p[1], p[2])

def print_points (points):
	for x in points:
	    print x
	    for y in points[x]:
		print "   " + str (y) + ": " + str(points[x][y])

if __name__ == '__main__':
        data = loadtxt('data.csv', delimiter=',', dtype='str')
	ucrs = loadtxt('ref.txt', delimiter='|', dtype='str')
        points={}
    
        for p in ucrs:
                x = int(round(p[1].astype('float')*granularity))
                y = int(round(p[2].astype('float')*granularity))
                if not x in points:
			points[x] = {}
		if not y in points[x]:
			points[x][y] = []
		points[x][y].append(make_tuple(p))

#	print_points (points) 
        join_files(points, data)
