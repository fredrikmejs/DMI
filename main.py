import csv
import os
import matplotlib.pyplot as plt
import statistics
import scipy.stats as st
from operator import itemgetter


class AnalyzeDMI:
    def __init__(self):

        self.rows = []
        self.stationList = {}
        self.dates = {}
        self.countryMeans = 0
        self.means = []

    '''
    A function to control the flow of the program
    '''

    def main(self):
        self.openFile()
        self.cleanFile()
        self.plot()
        self.countryMean()
        self.hypothesisTestData()
        self.sameAmountOfData()

    '''
    Opens the file cleanedCVS.cvs or GRADDAGE_TAL.cvs
    '''

    def openFile(self):
        # Checks if it should use the cleaned file or not
        if os.path.exists('cleanedCVS.csv'):
            fileName = "cleanedCVS.csv"
        else:
            fileName = "GRADDAGE_TAL.csv"

        file = open(fileName, 'r')

        csvreader = csv.reader(file)
        header = next(csvreader)

        for row in csvreader:
            self.rows.append(row)

        file.close()
        self.createNewCVS(header)

    '''
    Create a new CVS file which will make it faster to load the program 
    the next time you are running it 
    '''

    def createNewCVS(self, header):
        with open('cleanedCVS.csv', 'w', encoding='UTF8') as newCVS:
            writer = csv.writer(newCVS)

            writer.writerow(header)
            writer.writerows(self.rows)

            print('file created\n')
            newCVS.close()

    '''
    Cleans the file for outliners and set the values 
    stationList and dates
    '''

    def cleanFile(self):
        for row in list(self.rows):
            if float(row[2]) < 1 or float(row[2]) > 27:
                self.rows.remove(row)

            keys = self.stationList.keys()

            # Creates a Map structure for the stations '[stationId] = [date, degree_day, Sigma(degree_day)]'
            if keys.__contains__(row[0]):
                self.stationList[row[0]].append([row[5], row[2], row[3]])
            else:
                self.stationList[row[0]] = [[row[5], row[2], row[3]]]

            # Creates the Map of the different dates '[date] = [station, degree_day]'
            if self.dates.keys().__contains__(row[5]):
                self.dates[row[5]].append([row[0], float(row[2])])
            else:
                self.dates[row[5]] = [[row[0], float(row[2])]]

        keysToRemove = []
        for key in self.dates.keys():
            if len(self.dates[key]) < 18:
                keysToRemove.append(key)

        for item in keysToRemove:
            self.dates.pop(item)

    '''
    Plots the accumulated for all the stations
    '''

    def plot(self):

        for key in self.stationList.keys():
            x = []
            y = []

            if len(self.stationList[key]) < 10000:
                continue

            for row in self.stationList[key]:
                y.append(float(row[2]))
                x.append(float(row[0]))
            plt.plot(x, y, label=key)

        plt.xscale('linear')
        plt.yscale('linear')
        plt.xlabel('åååå-måned-dag')
        plt.ylabel('Akkumuleret graddage', labelpad=0)
        plt.grid(True)
        plt.show()

    '''
    Calculates the mean of each station where there are at least 10.000 observations
    '''

    def calculateMean(self):
        self.means = []

        for key in self.stationList.keys():
            values = []
            if len(self.stationList[key]) < 10000:
                continue

            for item in self.stationList[key]:
                values.append(float(item[1]))
            self.means.append([key, statistics.mean(values)])

        meanOfMeans = []

        # Show the highest and lowest values to compare differences
        highest = [0, 0]
        lowest = [0, 100000]
        for mean in self.means:
            if mean[1] > highest[1]:
                highest = mean

            if mean[1] < lowest[1]:
                lowest = mean

            meanOfMeans.append(mean[1])

        return meanOfMeans, highest, lowest

    '''
    Prints values needed to conclude on the hypothesis
    '''

    def hypothesisTestData(self):

        meanOfMeans, highest, lowest = self.calculateMean()

        print("--------------")
        print('General observations for the dataset')
        print('Highest: ', highest)
        print('Lowest: ', lowest)
        print('Quantiles: ', statistics.quantiles(meanOfMeans))
        print('Average for observations: ', statistics.mean(meanOfMeans))

        # Calculates the 95% confident interval
        CInterval = st.t.interval(alpha=0.95, df=len(meanOfMeans) - 1,
                                  loc=statistics.mean(meanOfMeans), scale=st.sem(meanOfMeans))
        print('95% confident interval: ', CInterval)

        print('T-test for 1sample: ', st.ttest_1samp(meanOfMeans,
                                                     self.countryMeans))
        print('Standard deviation for the means of the stations: ', statistics.stdev(meanOfMeans))

        plt.boxplot(meanOfMeans)
        plt.show()

        self.means.append(["Average", statistics.mean(meanOfMeans)])
        self.means.append(["Country", self.countryMeans])

        self.means.sort(key=itemgetter(1))

        x = []
        y = []
        for mean in self.means:
            x.append(mean[0])
            y.append(mean[1])

        plt.xlabel('Average')
        plt.ylabel('StationID', loc='top', labelpad=-2.0)
        plt.barh(x, y)
        plt.show()

        print('Right and left side of the critical value: [', st.t.ppf(0.025, 31), ',',
              st.t.ppf(0.975, 31), ']')

    '''
    Function to calculate the mean for the Country
    This is done by calculating the daily average
    '''

    def countryMean(self):
        means = []
        for key in self.dates.keys():
            numbers = []

            for item in self.dates[key]:
                numbers.append(item[1])

            means.append(statistics.mean(numbers))

        self.countryMeans = statistics.mean(means)

        print('Attributes for Country averages ')
        print('Mean for the country %2f' % self.countryMeans)
        print('Amount of days with observations %d' % len(means))
        print('Standard deviation: %2f' % statistics.stdev(means))
        print('Quantiles: ', statistics.quantiles(means))

        plt.hist(means)
        plt.show()

    '''
    Equalizes he amount of data for each of the stations
    because of uneven amount of data
    '''

    def sameAmountOfData(self):
        size = 10640
        plotData = []
        x = []
        y = []

        for key in self.stationList.keys():
            dataLength = len(self.stationList[key])

            # Checks there is at least 10.000 observations
            if dataLength < 10000:
                continue

            if dataLength != size:
                mean = 0
                for item in self.means:
                    if item[0] == key:
                        mean = item[1]
                        break

                plotData.append(
                    [key, float(self.stationList[key][dataLength - 1][2])
                     + (size - dataLength) * mean])
            else:
                plotData.append([key, self.stationList[key][dataLength - 1][2]])

        # sorts the list from the 2 element
        plotData.sort(key=itemgetter(1))

        for data in plotData:
            x.append(data[0])
            y.append(data[1])

        plt.xlabel('Average')
        plt.ylabel('StationID')
        plt.barh(x, y)
        plt.show()

        plt.boxplot(y)
        plt.show()


if __name__ == "__main__":
    startProgram = AnalyzeDMI()
    startProgram.main()
