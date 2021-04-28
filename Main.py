# Literally Clouded.ipynb but as a python file and not a notebook

from circle_fit import least_squares_circle, plot_data_circle
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import math

# Read in data:
# Cloud_Sections
cloud_sections = pd.read_csv(
    'Cleaned/CLOUD_SECTIONS_Cleaned.csv', delimiter=',', encoding='latin1')

# Designed_Pipe_Center
designed_centers = pd.read_csv(
    'Cleaned/DESIGNED_Pipe_Centers_Cleaned.csv', delimiter=',', encoding='latin1')

# Planes_Local_Global_Cleaned
p_info = pd.read_csv('Cleaned/Planes_Local_Global_Cleaned.csv',
                     delimiter=',', encoding='latin1')

# A List of sections, where each section is a list of tuples, and each tuple is the XY coordinates of a point on the point cloud
TuplePairsBySection = []

# A list of the Designed Center points and radius, each object in the list is a panda dataframe where there are as many rows as pipes
CenterList = []

# For n in the number of distinct sections
for n in range(cloud_sections.Section.nunique()):

    # Grabs all dataframe rows in each distinct section
    grab = cloud_sections[cloud_sections['Section']
                          == 'Section-{' + str(n) + '}']

    # Adds the individual X and Y points in each point cloud pair for the nth section
    TuplePairsBySection.append(list(zip(grab.X, grab.Y)))

    # Adds the dataframe rows in each distinct section
    CenterList.append(
        designed_centers[designed_centers['Section'] == 'Section-{' + str(n) + '}'])

# Arbitrary radius multiplier
N = 1.4

# A List of points in the point cloud, by section and pipe, that pass the first noise test
PassesFirstNoiseTestBySection = []

# A List of points in the point cloud, by section, that fail the first noise test
FailsFirstNoiseTestBySection = []

count = 0
for section in TuplePairsBySection:
    D, E, F = [], [], []

    # Intialize the radius for both pipes
    r1, r2 = CenterList[count].iloc[0, 4], CenterList[count].iloc[1, 4]

    # Intialize the center XY coordinate tuple for both pipes
    c1, c2 = tuple(CenterList[count].iloc[0, 1:3]), tuple(
        CenterList[count].iloc[1, 1:3])

    for point in section:

        # Test first pipe
        if math.dist(c1, point) < (r1 * N):
            D.append(point)

        # Test second pipe
        elif math.dist(c2, point) < (r2 * N):
            E.append(point)
        else:
            F.append(point)

    PassesFirstNoiseTestBySection.append(D)
    PassesFirstNoiseTestBySection.append(E)
    FailsFirstNoiseTestBySection.append(F)
    count += 1

# Arbitrary IQR multiplier
M = 1.3


def findOutVals(rlist):
    P, F = {}, {}
    P_index = []
    sortedList = sorted(rlist)
    L = len(rlist)
    Q1 = np.median(sortedList[:(L//2 + 2)])
    Q3 = np.median(sortedList[(L//2 + 1):])
    IQR = Q3 - Q1
    L_out = Q1 - IQR*M
    R_out = Q3 + IQR*M
    count = 0
    for n in rlist:
        if (n > L_out) and (n < R_out):
            P[count] = n
        count += 1
    for a in P:
        P_index.append(a)
    return P_index


# A List of points in the point cloud, by section and pipe, that pass the first noise test
PassesSecondNoiseTestBySection = []

# A List of points in the point cloud, by section, that fail the first noise test
FailsSeconNoiseTestBySection = []

count = 0
for circle in PassesFirstNoiseTestBySection:
    passPoints, failPoints = [], []
    if len(circle) == 0:
        count += 1
    else:
        ResList = []
        if count % 2 == 0:
            r = CenterList[count // 2].iloc[0, 4]
            c = tuple(CenterList[count // 2].iloc[0, 1:3])
            for p in circle:
                ResList.append((math.dist(p, c) - r))
            Pass_index = findOutVals(ResList)
            for n in range(len(circle)):
                if n in Pass_index:
                    passPoints.append(circle[n])
                else:
                    failPoints.append(circle[n])
        else:
            r = CenterList[count // 2].iloc[1, 4]
            c = tuple(CenterList[count // 2].iloc[1, 1:3])
            for p in circle:
                ResList.append((math.dist(p, c) - r))
            findOutVals(ResList)
            Pass_index = findOutVals(ResList)
            for n in range(len(circle)):
                if n in Pass_index:
                    passPoints.append(circle[n])
                else:
                    failPoints.append(circle[n])
            count += 1
    PassesSecondNoiseTestBySection.append(passPoints)
    FailsSeconNoiseTestBySection.append(failPoints)

#----- graphing section would go here -----#


def printInfo(radius, Xcp, Ycp, secNum, pipeCount):
    # round values
    roundList = [radius, Xcp, Ycp]
    roundList = [round(i, 6) for i in roundList]
    radius = roundList[0]
    Xcp = roundList[1]
    Ycp = roundList[2]
    FCP = (Xcp, Ycp)
    givenR = CenterList[secNum].iloc[pipeCount, 4]
    givenC_tuple = tuple(CenterList[secNum].iloc[pipeCount, 1:3])
    print("The fitted center point is: (" + str(Xcp) + "," + str(Ycp) + ")")
    print("The as-designed center point is: (" +
          str(givenC_tuple[0]) + "," + str(givenC_tuple[1]) + ")")
    print("The distance between them is: " +
          str(round(math.dist(givenC_tuple, FCP), 7)))
    print("The fitted radius is: " + str(radius) +
          " and the actual radius is: " + str(givenR))
    print("The difference between them is: " +
          str(round(abs(givenR - radius), 7)))


pipe_point = []
sec_count = 0
for n in range(50):
    a = PassesSecondNoiseTestBySection[2 * n:2 * n + 2]
    if len(a[0]) > 0:
        xc, yc, r, CI = least_squares_circle(a[0], 8)
        plot_data_circle((list(zip(*a[0]))[0]),
                         (list(zip(*a[0]))[1]), xc, yc, r)
        plt.title("Section " + str(sec_count) + " Pipe " + str(sec_count*2))
        plt.show()
        printInfo(r, xc, yc, sec_count, 0)
        pipe_point.append({xc, yc})
    else:
        pass
    if len(a[1]) > 0:
        xc, yc, r, CI = least_squares_circle(a[1], 4.375)
        plot_data_circle((list(zip(*a[1]))[0]),
                         (list(zip(*a[1]))[1]), xc, yc, r)
        plt.title("Section " + str(sec_count) +
                  " Pipe " + str(sec_count*2 + 1))
        plt.show()
        printInfo(r, xc, yc, sec_count, 1)
        pipe_point.append({xc, yc})
    else:
        pass
    sec_count += 1

with open('eggs.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    for i in range(len(pipe_point)):
        writer.writerow(pipe_point[i])
