import csv
import os
import matplotlib.pyplot as plt
import statistics
import scipy.stats as st


class ReadFile:
    def __init__(self):

        if (os.path.exists('cleanedCVS.csv')):
            self.fileName = "cleanedCVS.csv"
        else:
            self.fileName = "GRADDAGE_TAL.csv"

        self.file = None
        self.rows = []
        self.header = []
        self.stationList = {}
        self.dates = {}

    def main(self):
        self.openFile()
        self.cleanFile()
        self.createNewCVS()
        self.plot()
        self.countryMean()
        self.calculateMean()

    def openFile(self):
        self.file = open(self.fileName, 'r')
        type(self.file)

        csvreader = csv.reader(self.file)
        self.header = next(csvreader)

        for row in csvreader:
            self.rows.append(row)

        self.file.close()

    def cleanFile(self):

        for row in list(self.rows):
            if row[2] == '0' or float(row[2]) > 25:
                self.rows.remove(row)

            keys = self.stationList.keys()

            if keys.__contains__(row[0]):
                self.stationList[row[0]].append([row[5], row[2], row[3]])
            else:
                self.stationList[row[0]] = [[row[5], row[2], row[3]]]

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

    def createNewCVS(self):
        with open('cleanedCVS.csv', 'w', encoding='UTF8') as newCVS:
            writer = csv.writer(newCVS)

            writer.writerow(self.header)
            writer.writerows(self.rows)

            print('file created')
            newCVS.close()

    def plot(self):

        keys = self.stationList.keys()

        for key in keys:
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
        plt.xlabel('Dato')
        plt.ylabel('Akkumuleret graddage')
        plt.grid(True)
        plt.show()

    def calculateMean(self):
        keys = self.stationList.keys()
        means = []

        for key in keys:
            values = []
            if len(self.stationList[key]) < 10000:
                continue

            for item in self.stationList[key]:
                values.append(float(item[1]))
            means.append([key, statistics.mean(values)])

        meanOfMeans = []

        highest = [0, 0]
        lowest = [0, 100000]
        for mean in means:
            if mean[1] > highest[1]:
                highest = mean

            if mean[1] < lowest[1]:
                lowest = mean

            meanOfMeans.append(mean[1])

        print("--------------")
        print(highest)
        print(lowest)
        print(statistics.quantiles(meanOfMeans))
        print([statistics.mean(meanOfMeans)])

        b = st.t.interval(alpha=0.95, df=len(meanOfMeans) - 1,
                          loc=statistics.mean(meanOfMeans), scale=st.sem(meanOfMeans))
        print(b)

        print(st.normaltest(meanOfMeans))
        print(st.ttest_1samp(meanOfMeans, 0.0))
        print(statistics.stdev(meanOfMeans))

        plt.boxplot(meanOfMeans)
        plt.show()

        x = []
        y = []
        for mean in means:
            x.append(mean[0])
            y.append(mean[1])

        y.append(statistics.mean(meanOfMeans))
        x.append("gennemsnit")

        plt.barh(x, y)
        plt.show()

        # plt.boxplot(meanOfMeans)
        # plt.show()

    def countryMean(self):

        means = []
        for key in self.dates.keys():
            numbers = []

            for item in self.dates[key]:
                numbers.append(item[1])

            means.append(statistics.mean(numbers))

        print(statistics.mean(means))

        plt.hist(means)
        plt.show()


if __name__ == "__main__":
    startProgram = ReadFile()
    startProgram.main()
