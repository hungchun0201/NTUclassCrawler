import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import argparse
# from collections import OrderedDict


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
        self.periodKey = list(self.periodDict.keys())
        # OrderedDict(sorted(self.periodDict.items(), key=lambda t: t[0]))
        self.parser()

    def parser(self):

        def parseOptArgs(str):
            if str == None:
                return {}
            pieces = str.split(',')
            opts = {}
            for p in pieces:
                if '=' in p:
                    key, val = p.split('=')
                else:
                    key, val = p, 1
                opts[key] = val
            return opts

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
        parser.add_argument(
            "--search-opt", dest="searchOpt", help='''Comma separated values to specifiy search options e.g. "Title=積體電路,Classroom=電二"
            The avaliable args include:
                "Id": Curriculum Identity Number
                "Class": The class number. If the course is teached by only one teacher, it is set to 00
                "Title": Course title
                "Instructor": Teacher name
                "Classroom": Schedule Classroom
                "Time": The time of course
            
            For example, if you type "--search-opt Title=積體電路,Classroom=電二", you may get the following result:
                     Id Class        Title Instructor Classroom    Time
            0  943U0010    00       積體電路測試        李建模     電二146  二2,3,4
            1  921U9590    00  電力電子與積體電路控制        陳景然     電二225  二7,8,9
            2  943U0120    00     射頻積體電路設計        陳怡然     電二104  三2,3,4
            3  90140500    00       積體電路設計        盧奕璋     電二229  三7,8,9
            4  942U0120    00     微波積體電路專題        林坤佑     電二101  四7,8,9
            '''
        )

        args = parser.parse_args()
        args.searchOpt = parseOptArgs(args.searchOpt)
        self.args = args

    def transformTime(self, time):
        day = time[1]
        periods = time[3:]
        periods = periods.split('~')

        if(periods[0] == periods[1]):  # only one session
            return day+self.periodDict[periods[0]]
        else:  # more than one session
            return_str = ""
            start = self.periodKey.index(periods[0])
            end = self.periodKey.index(periods[1])+1
            return_str = ','.join(self.periodDict[k]
                                  for k in self.periodKey[start:end])

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

    def checkSearchOpts(self, dict):
        if(not self.args.searchOpt):
            return True
        else:
            for key in self.args.searchOpt:
                if(self.args.searchOpt[key] not in dict[key]):
                    return False
            else:
                print(dict)
                return True


    def crawl(self):

        class_info = []
        if(not self.args.page):
            self.getMaximumPage()

        for week in range(1, 7):
            for page in range(1, self.args.page+1):
                doc = requests.get(
                    'http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new',
                    params={
                        'Type': '1',
                        'page': str(page),
                        'SYearDDL': self.args.semester,
                        'BuildingDDL': self.args.building,
                        'Week': str(week),
                        'Capacity': '1',
                        'SelectButton': '%E6%9F%A5%E8%A9%A2'
                    })
                doc.encoding = 'UTF-8'
                doc = doc.text
                soup = BeautifulSoup(doc, 'html.parser')
                for sub_table in [table.find_all(['table', 'tbody']) for table in soup.find_all(id="tooltip")]:
                    try:
                        sub_table = sub_table[0].text
                        sub_table = re.sub(r"[ \t\r\f\v]+", "", sub_table)
                        newCourse = sub_table.split(
                            '\n')     # split string with \n
                        # remove '' element in list
                        newCourse = [x for x in newCourse if x]
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
                        # print("oo")
                        dict = {
                            "Id": newCourse[1],#Curriculum Identity Number
                            "Class": newCourse[3],
                            "Title": newCourse[5],#Course title
                            "Instructor": newCourse[7],
                            "Classroom": newCourse[9],#Schedule Classroom
                            "Time": newCourse[11],
                        }
                        dict["Time"] = self.transformTime(dict["Time"])

                        if(not self.checkSearchOpts(dict)):
                            continue

                        # check whether is the same class
                        endloop = False

                        for ori_dict in class_info:
                            if(ori_dict["Title"] == newCourse[5] and ori_dict["Instructor"] == newCourse[7]):
                                endloop = True
                                if(dict["Time"] in ori_dict["Time"]):
                                    break
                                else:
                                    ori_dict["Time"] = ori_dict["Time"] + \
                                        ' '+dict["Time"]
                                    break
                        if(endloop):
                            continue

                        
                        class_info.append(dict)
                    except:
                        continue
                print("========== Got", len(class_info), "courses information, until Page", page, "and Day", week ,"==========")
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
