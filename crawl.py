import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import argparse
from collections import OrderedDict


class Crawler():

    def __init__(self):
        self.periodDict = {
            "7:10": "0",
            "8:10": "1",
            "9:10": "2",
            "10:20": "3",
            "11:20": "4",
            "12:20": "5",
            "13:20": "6",
            "14:20": "7",
            "15:30": "8",
            "16:30": "9",
            "17:30": "10",
            "18:25": "A",
            "19:20": "B",
            "20:15": "C",
            "21:10": "D",
        }
        OrderedDict(sorted(self.periodDict.items(), key=lambda t: t[0]))
        self.parser()

    def parser(self):
        parser = argparse.ArgumentParser(prog='python3 crawl.py', description='''

        This is a program that can crawl data of classes in next semester from
        "classroom management system(上課教室看板)". With this program, you can arrange your classes before they come out at NTU online. While the information is not quite
        complete on the website, it is still a useful and helpful tool if you want to
        organize the curriculum for next semester in advance. The reference link is
        http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new.

        ''', epilog="Designed by Hung-Chun,Lin.")

        parser.add_argument(
            "--semester", help="Select the semester you want to query", default="1082")

        parser.add_argument(
            "--delay-time", help="Set the delay time between each request", type=float, default=0.5, dest="delay")

        parser.add_argument(
            "--tor", help="(NOT IMPLETEMENTED)Try to use tor proxy to prevent from blocking IP by the website", action="store_true")

        parser.add_argument(
            "-p", "--page", help="Assign the maximum page", type=int)

        parser.add_argument(
            "-s", "--save", help="Store the result. You can specify your filename.\
            Please use .xls or .xlsx as filename extension.", const="result.xls", action="store", nargs="?")

        parser.add_argument(
            "--building", help="Specify the building you want to query. \
            If the building belongs to a college(ex:College of Electrical Engineering and Computer Science), \
            use the code of that college(ex:9),or simply type the name of the building(ex:博雅).", default=9,
            choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, "A",
                     "B", "共同", "普通", "新生", "綜合", "博雅", "%"]
        )

        args = parser.parse_args()
        if(args.tor):
            pass
        self.args = args

    def transformTime(self, time):
        day = time[1]
        periods = time[3:]
        periods = periods.split('~')

        if(periods[0] == periods[1]):  # only one session
            return day+self.periodDict[periods[0]]
        else:  # more than one session
            return_str = ""
            addToStr = False
            for session in self.periodDict:
                if(session == periods[0]):
                    addToStr = True
                    return_str += self.periodDict[session]
                elif(session == periods[1]):
                    return_str += (","+self.periodDict[session])
                    break
                elif(addToStr == True):
                    return_str += (","+self.periodDict[session])

            return day+return_str

    def getMaximumPage(self):
        doc = requests.get(
            'http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new?Type=1&page={}&SYearDDL={}&BuildingDDL={}&Week={}&Capacity=1&SelectButton=%E6%9F%A5%E8%A9%A2'
            .format(1, self.args.semester, self.args.building, 1))
        doc.encoding = 'UTF-8'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        table = soup.find(id="ClassTimeGV")
        last_row = table.find_all("tr")[-1].find("td")
        # print(last_row.findChildren())
        self.args.page = len(last_row.findChildren())

    def crawl(self):

        class_info = []
        if(not self.args.page):
            self.getMaximumPage()

        for week in range(1, 7):
            for page in range(1, self.args.page+1):
                doc = requests.get(
                    'http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new?Type=1&page={}&SYearDDL={}&BuildingDDL={}&Week={}&Capacity=1&SelectButton=%E6%9F%A5%E8%A9%A2'
                    .format(page, self.args.semester, self.args.building, week))
                doc.encoding = 'UTF-8'
                doc = doc.text
                soup = BeautifulSoup(doc, 'html.parser')
                for sub_table in [table.find_all(['table', 'tbody']) for table in soup.find_all(id="tooltip")]:
                    try:
                        sub_table = sub_table[0].text
                        sub_table = re.sub(r"[ \t\r\f\v]+", "", sub_table)
                        newCourse = sub_table.split(
                            '\n')     # split string with \n       
                        newCourse = [x for x in newCourse if x]# remove '' element in list
                        first_str = newCourse[0].split("：")[0]

                        if(first_str != '課程識別碼'):
                            continue

                        # Add class number.
                        # some class is instructed by only one prof,so there is no class number.
                        if(len(newCourse) == 11):
                            newCourse.insert(3, "00")
                        elif(len(newCourse) < 11):
                            # bad course
                            continue

                        newCourse[11] = self.transformTime(newCourse[11])

                        # check whether is the same class
                        endloop = False
                        for dict in class_info:
                            if(dict["Course title"] == newCourse[5] and dict["Instructor"] == newCourse[7]):
                                endloop = True
                                if(newCourse[11] in dict["time"]):
                                    break
                                else:
                                    dict["time"] = dict["time"] + \
                                        ' '+newCourse[11]
                                    break
                        if(endloop):
                            continue

                        dict = {
                            "Curriculum Identity Number": newCourse[1],
                            "Class": newCourse[3],
                            "Course title": newCourse[5],
                            "Instructor": newCourse[7],
                            "Schedule Classroom": newCourse[9],
                            "time": newCourse[11],
                        }
                        class_info.append(dict)
                    except:
                        continue
                print("========== Got {} courses information, until Page {} and Day {} ==========".format(
                    len(class_info), page, week))
                time.sleep(self.args.delay)

        select_df = pd.DataFrame(class_info)
        print(select_df)
        if(self.args.save):
            try:
                select_df.to_excel(self.args.save)
            except:
                return


if __name__ == '__main__':
    crawler = Crawler()
    crawler.crawl()
