import os.path
import pandas as pd
import os
import argparse


class App():

    def __init__(self):
        self.parser()
        self.run_args()

    def parser(self):

        parser = argparse.ArgumentParser(prog='python3 run_app.py', description='''

This program utilizes the work from Hung-Chun Lin as it helps users crawl data from "classroom management system (上課教室看板)" and then deploy the data with Streamlit.
                
The information may be out-of-date after a while, so users may have to re-run the program to ensure you're keeping up with the latest information.

Make sure you've installed all the requirements needed before deployment. Use `pip install -r requirements` if you haven't already.

The data are all from http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new.

A mirror of the site is already avaible at https://share.streamlit.io/icheft/ntuclasscrawler/app.py.
''', epilog="© Brian L. Chen", formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            "--semester", help="Select the semester you want to query", default="1101")

        parser.add_argument(
            "--toCSV", help="Export csv file", action="store_true")

        parser.add_argument(
            "-d", "--deploy", help="Deploy your site locally", action="store_true")

        parser.add_argument(
            "-f", "--force", help="Override current course.xlsx file", action="store_true")

        self.args = parser.parse_args()

    def run_args(self):
        if not os.path.isfile('course.xlsx'):
            print('course.xlsx not found. Now crawling data...')
            os.system(
                f'python3 crawl.py -b % --save course.xlsx --semester {self.args.semester}')
        else:
            if self.args.force:
                os.system(
                    f'python3 crawl.py -b % --save course.xlsx --semester {self.args.semester}')
            else:
                print(f'course.xlsx file already exists')

        if self.args.toCSV:
            pd.read_excel('course.xlsx', index_col=0,
                          engine='openpyxl').to_csv('course.csv')
            print(f'course.csv file generated successfully')

        if self.args.deploy:
            print('Ready to deploy...')
            if not os.path.isfile('course.csv') or self.args.force:
                pd.read_excel('course.xlsx', index_col=0,
                              engine='openpyxl').to_csv('course.csv')
                print(f'course.csv file generated successfully')

            os.system(f'streamlit run app.py -- -l')


if __name__ == '__main__':
    app = App()
