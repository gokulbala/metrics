from geopy.distance import great_circle
from numpy import loadtxt, concatenate


# given a point and an offset, calculate range keeping in mind wraparound

data = loadtxt('/home/spark/JourneyFiles/MNJourneysEven_20130101-20130131.csv', delimiter=',', dtype='str')

def get_nearest_point(src_coord, points):
        """
        src_coord: one points
        points: grid of points
        """
        x = int(round(src_coord[0].astype('float')*300))
        y = int(round(src_coord[1].astype('float')*300))
        nearby_points = []
        offset = 0
        max_offset = 5000

        # only search for the points in the nearby grid cells, in a square which "radius" is "offset"
        while offset <= max_offset:
#                print "Offset: " + str(offset)
                # check a square around the data point
		x_r = range (x-offset, x+offset+1)
                for i in x_r:
			y_r = range (y-offset, y+offset+1)
                        for j in y_r:
                                if i != x+offset and i != x-offset and j != y-offset and j != y+offset:
                                        # only consider the borders of the square
                                        continue
                                try:
#                                        print "Trying " + str(i) + "," + str(j) + ": "
                                        nearby_points.extend(points[i][j])
                                        if 5000 == max_offset:
                                                # +1 to round up
                                                # +1 to compensate for the initial point being far from the grid point
                                                max_offset = min (int (offset * 1.5 + 2), 5000)
#                                                print "New max offset: " + str(max_offset)
                                except KeyError:
#                                        print "--"
                                        pass
                offset = offset + 1
        
        distances = [great_circle(src_coord, (point[1],point[2])).meters for point in nearby_points]
        distance = min(list(enumerate(distances)), key=lambda x:x[1])
        return nearby_points[distance[0]]


def join_files(ucrs, data):
        data_points = zip(data[:,10].astype('float'), data[:, 11].astype('float'))

        for data_ind in xrange(len(data_points)):
                data_point = data_points[data_ind]
                nearest_point = get_nearest_point(data_point, points)

                print ",".join(concatenate((data[data_ind], [nearest_point[0]], nearest_point[4:6])))

def make_tuple (p):
        return (p[0], p[1], p[2], p[3], p[4], p[5])

if __name__ == '__main__':
        data = loadtxt('/home/spark/data.csv', delimiter=',', dtype='str')
        ucrs = loadtxt('/home/gokul/tasks/ucrs.txt', delimiter='|', dtype='str')
        points={}
    
        for p in ucrs:
                x = int(round(p[1].astype('float')*300))
                y = int(round(p[2].astype('float')*300))
                try:
                        points[x][y].append(make_tuple(p))
                except KeyError:
                        try:
                                points[x][y] = []
                                points[x][y].append(make_tuple(p))
                        except KeyError:
                                points[x]={}
                                points[x][y] = []
                                points[x][y].append(make_tuple(p))

        join_files(points, data)
