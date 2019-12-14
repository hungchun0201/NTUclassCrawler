import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
def main():
    class_info = []

    for page in range(1,2):
        for week in range(1,7):
            doc = requests.get('http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new?Type=1&page={}&SYearDDL=1082&BuildingDDL=9&Week={}&Capacity=1&SelectButton=%E6%9F%A5%E8%A9%A2'.format(page, week))
            doc.encoding = 'UTF-8'
            doc = doc.text
            soup = BeautifulSoup(doc, 'html.parser') 
            for sub_table in [table.find_all(['table','tbody']) for table in soup.find_all(id="tooltip")]:
                sub_table = sub_table[0].text
                sub_table= re.sub(r"[ \t\r\f\v]+","",sub_table)
                test = sub_table.split('\n')     # split string with \n
                test = [x for x in test if x]    #remove '' element in list
                first_str = test[0].split("：")[0]
                if(first_str != '課程識別碼'):
                    continue
                if(len(test)!=12):
                    test.insert(3,"00")
                
                Test = list(filter(lambda dict:dict["Course title"]==test[5] and dict["Instructor"]==test[7],class_info))
                if(len(Test)>0):
                    continue

                dict = {
                    "Curriculum Identity Number":test[1],
                    "Class":test[3],
                    "Course title":test[5],
                    "Instructor":test[7],
                    "Schedule Classroom":test[9],
                    "time":test[11],
                }
                class_info.append(dict)
            time.sleep(2)
        
    select_df = pd.DataFrame(class_info)
    print(select_df)
    select_df.to_excel('class.xls')
if __name__ == '__main__':
    main()


