from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep as Sleep
import argparse
import ast
import tkinter as tk
from tkinter.ttk import Combobox, Scrollbar, Frame, Label
import threading
import sys


class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


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

        self.week_dict = {
            "全部": "all",
            "只搜尋星期一": 1,
            "只搜尋星期二": 2,
            "只搜尋星期三": 3,
            "只搜尋星期四": 4,
            "只搜尋星期五": 5
        }

        self.parser()
        self.getNecessaryInfo()
        self.windows()

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

        ''', epilog="Designed by Hung-Chun,Lin.", formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            "--semester", help="Select the semester you want to query", default="1101")

        parser.add_argument(
            "--delay-time", help="Set the delay time between each request", type=float, default=0, dest="delay")

        parser.add_argument(
            "-p", "--page", help="Assign the maximum page of each day.", type=int)

        parser.add_argument(
            "-s", "--save", help='''Store the result. You can specify your filename.
Please use .xls or .xlsx as filename extension.''', const="result.xls", action="store", nargs="?")

#         parser.add_argument(
#             "-s", "--save", help='''Store the result. You can specify your filename.
# Please use .xls or .xlsx as filename extension.''', const="result.csv", action="store", nargs="?")

        parser.add_argument(
            "-b", help='''Specify the building you want to query.
If the building belongs to a college(ex:College of Electrical Engineering and Computer Science),
use the code of that college(ex:9),or simply type the name of the building(ex:博雅).
The percentage sign means search for all buildings.''', default=9, dest="building",
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "A",
                     "B", "共同", "普通", "新生", "綜合", "博雅", "%"]
        )
        parser.add_argument(
            "--search-opt", dest="searchOpt", help='''
Comma separated values to specifiy search options e.g. "Title=積體電路,Classroom=電二"
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

    def getNecessaryInfo(self):
        doc = get(
            'https://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new')
        doc.encoding = 'UTF-8'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        # ---------------------------- Find semester list ---------------------------- #
        semester_select = soup.find(id="SYearDDL")
        semester_list = [
            option.text for option in semester_select.find_all('option')]
        self.semester_list = semester_list
        # print(semester_list)

        # ---------------------------- Find Building dict ---------------------------- #
        building_select = soup.find(id="BuildingDDL")
        building_dict = {option.text: option['value']
                         for option in building_select.find_all('option')}
        self.building_dict = building_dict
        # print(building_dict)

    def transformTime(self, time):
        day = time[1]
        periods = time[4:]
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
        doc = get(
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

        print(self.args)

        class_info = []
        for week in range(1, 6):
            if(self.args.target_week != "all" and week != self.args.target_week):
                continue
            for page in range(1, self.args.page+1):
                doc = get(
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
                soup = BeautifulSoup(doc, 'lxml')
                script = soup.select("#ContentPlaceHolder1 > script")[0]
                # All course data in this page can be found in varaible timeDT
                map_search = re.search('timeDT\s*=\s*(.*?}])\s*;', str(script))
                # Convert to array from string
                course_info = ast.literal_eval(map_search[1])
                for classroom in course_info:
                    if(len(classroom.keys()) == 2):
                        continue
                    Sessions = list(classroom.keys())
                    Sessions.remove("Item")
                    Sessions.remove("Msg")
                    for session in Sessions:
                        course = classroom[session]["Info"][0]
                        # Add class number.
                        # some class is instructed by only one prof,so there is no class number.
                        if(course['cr_clas'] == ''):
                            course['cr_clas'] = "00"
                        else:
                            # bad course
                            continue

                        dict = {
                            # Curriculum Identity Number
                            "Id": course['cr_cono'],
                            "Class": course['cr_clas'],
                            "Title": course['cr_cnam'],  # Course title
                            "Instructor": course['cr_tenam'],
                            "Classroom": course['cr_no'],  # Schedule Classroom
                            "Time": course['cr_time'],
                        }
                        dict["Time"] = self.transformTime(dict["Time"])

                        if(not self.checkSearchOpts(dict)):
                            continue

                        # check whether is the same class
                        endloop = False

                        for old_dict in class_info:
                            if(old_dict["Id"] == dict["Id"] and old_dict["Class"] == dict["Class"]):
                                endloop = True
                                if(dict["Time"] in old_dict["Time"]):
                                    break
                                else:
                                    old_dict["Time"] = old_dict["Time"] + \
                                        ' '+dict["Time"]
                                    break
                        if(endloop):
                            continue

                        class_info.append(dict)
                self.message_label.configure(
                    text="========== Got {} courses information, until Page {} and Day {} ==========".format(len(class_info), page, week))
                self.window.update_idletasks()
                # print("========== Got", len(
                # class_info), "courses information, until Page", page, "and Day", week, "==========")
                Sleep(self.args.delay)

        select_df = pd.DataFrame(class_info)
        if(not select_df.empty):
            select_df["Id"] = select_df["Id"].map(lambda x: '%-8s' % x)
            select_df["Class"] = select_df["Class"].map(lambda x: '%-2s' % x)
            select_df["Title"] = select_df["Title"].map(
                lambda x: x.ljust(13, chr(12288)))
            select_df["Instructor"] = select_df["Instructor"].map(
                lambda x: x.ljust(4, chr(12288)))
            select_df["Classroom"] = select_df["Classroom"].map(
                lambda x: '{0:{1}<6}'.format(x, chr(12288)))
            select_df["Time"] = select_df["Time"].map(
                lambda x: '{0:{1}<8}'.format(x, chr(12288)))
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option('expand_frame_repr', False)
        self.result_labelframe.delete(1.0, "end")
        self.result_labelframe.insert(1.0, select_df)
        print(select_df)
        if(self.args.save):
            try:
                select_df.to_excel(self.args.save)
            except:
                print("Error! \nWarning:You probably did not install openpyxl first, type \"pip install openpyxl\" to install the package.")
                return

    def windows(self):
        def define_layout(obj, cols=1, rows=1):
            def method(trg, col, row):

                for c in range(cols):
                    trg.columnconfigure(c, weight=1)
                for r in range(rows):
                    trg.rowconfigure(r, weight=1)

            if type(obj) == list:
                [method(trg, cols, rows) for trg in obj]
            else:
                trg = obj
                method(trg, cols, rows)

        def start_to_crawl():
            self.args.semester = comboboxSemester.get()
            self.args.building = self.building_dict[comboboxBuilding.get()]
            self.args.target_week = self.week_dict[comboboxWeek.get()]
            self.getMaximumPage()
            if comboboxSaveOrNot.get() == "是":
                filename = entryFileName.get()
                if(filename.split(".")[-1] != "xlsx"):
                    message_label.configure(text="錯誤的檔案名稱，請以xlsx為副檔名")
                    return
                else:
                    message_label.configure(text="")
                    window.update_idletasks()
                    self.args.save = entryFileName.get()
            else:
                self.args.save = None
            # print(threading.current_thread())
            # print(threading.enumerate())
            thread_with_trace(target=self.crawl).start()
            # threading.Thread(target=self.crawl).start()

        window = tk.Tk()
        window.title('台大偷跑課表整理小工具')
        window.configure(background='white')
        align_mode = 'nswe'
        pad = 5

        select_width = 20
        select_height = 30
        button_width = select_width
        button_height = select_height/5
        result_width = select_width*4
        result_height = (select_height+button_height)*10/11
        message_width = result_width
        message_height = (select_height+button_height)/11

        div1 = tk.Frame(window,  width=message_width, height=message_height)
        div2 = tk.Frame(window,  width=result_width, height=result_height)
        div3 = tk.Frame(window,  width=select_width, height=select_height)
        div4 = tk.Frame(window,  width=button_width, height=button_height)

        div1.grid(column=0, row=0, padx=pad, pady=pad, sticky=align_mode)
        div2.grid(column=0, row=1, padx=pad, pady=pad, sticky=align_mode)
        div3.grid(column=1, row=0, padx=pad, pady=pad, sticky=align_mode)
        div4.grid(column=1, row=1, padx=pad, pady=pad, sticky=align_mode)

        window.update_idletasks()

        # ----------------------------------- div1 ----------------------------------- #
        result_labelframe = tk.LabelFrame(div1, text='查詢結果')
        txt1 = tk.Text(result_labelframe)
        sl1 = Scrollbar(result_labelframe)
        sl1['command'] = txt1.yview

        sl1.grid(row=0, column=1, sticky=align_mode)
        txt1.grid(row=0, column=0, sticky=align_mode)
        result_labelframe.grid(row=0, column=0, sticky=align_mode)
        result_labelframe.columnconfigure(0,weight=1)
        result_labelframe.rowconfigure(0,weight=1)
        self.result_labelframe = txt1

        # ----------------------------------- div2 ----------------------------------- #
        message_label = tk.Label(div2, bg='yellow')
        message_label['height'] = int(message_height)
        message_label['width'] = int(message_width)
        message_label.grid(column=0, row=0, sticky=align_mode)
        self.message_label = message_label

        # ----------------------------------- div3 ----------------------------------- #

        textSemester = tk.Label(div3, text="選擇學期")
        textSemester.grid(column=0, row=0, sticky=align_mode)

        comboboxSemester = Combobox(div3,
                                    values=self.semester_list,
                                    state="readonly")
        comboboxSemester.grid(column=0, row=1, sticky=align_mode)
        comboboxSemester.current(0)
        # comboboxSemester.bind("",set_args(self.args.semester,comboboxSemester.get()))

        textBuilding = tk.Label(div3, text="選擇建物/學院")
        textBuilding.grid(column=0, row=2, sticky=align_mode)

        comboboxBuilding = Combobox(div3,
                                    values=list(self.building_dict.keys()),
                                    state="readonly")
        comboboxBuilding.grid(column=0, row=3, sticky=align_mode)
        comboboxBuilding.current(0)

        textWeek = tk.Label(div3, text="選擇搜尋星期的日子")
        textWeek.grid(column=0, row=4, sticky=align_mode)

        comboboxWeek = Combobox(div3,
                                values=list(self.week_dict.keys()),
                                state="readonly")
        comboboxWeek.grid(column=0, row=5, sticky=align_mode)
        comboboxWeek.current(0)

        textSaveOrNot = tk.Label(div3, text="是否存檔為xlsx檔(建議存檔)")
        textSaveOrNot.grid(column=0, row=6, sticky=align_mode)

        comboboxSaveOrNot = Combobox(div3,
                                     values=["是", "否"],
                                     state="readonly")
        comboboxSaveOrNot.grid(column=0, row=7, sticky=align_mode)
        comboboxSaveOrNot.current(0)

        textFileName = tk.Label(div3, text="檔名(須以.xlsx結尾，若不須存檔免填)")
        textFileName.grid(column=0, row=8, sticky=align_mode)

        entryFileName = tk.Entry(div3)
        entryFileName.insert(0, "result.xlsx")
        entryFileName.grid(column=0, row=9, sticky=align_mode)

        # ----------------------------------- div4 ----------------------------------- #

        button = tk.Button(div4, text='開始搜尋 GO!', bg='green', fg='white')
        button.grid(column=0, row=0, sticky=align_mode)
        button['command'] = start_to_crawl

        # ------------------------------ Flexible layout ----------------------------- #

        window.columnconfigure(0, weight=4)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(0, weight=5)
        window.rowconfigure(1, weight=1)

        define_layout(div1)
        define_layout(div2)
        define_layout(div3, rows=10)
        define_layout(div4)

        self.window = window

        window.mainloop()


if __name__ == '__main__':
    crawler = Crawler()
