# NTU Class Crawler

## Introduction

This is a program that can crawl data of classes in next semester from
"classroom management system(上課教室看板)". With this program, you can schedule/arrange your classes before they come out at NTU online. While the information is not quite
complete on the website, it is still a useful and helpful tool if you want to
organize the curriculum for next semester. The reference link is
http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new.

## Environment
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.7-green.svg"></a> and the following libraries are required.


> <img src="https://img.shields.io/badge/python-requests %7C beautifulSoup4 %7C pandas %7C collections %7C argparse-blue">



## Usage

```
python3 crawl.py
```
## Optional Arguments
```
optional arguments:
  -h, --help            show this help message and exit
  --semester SEMESTER   Select the semester you want to query
  --delay-time DELAY    Set the delay time between each request
  --tor                 (NOT IMPLEMENTED)Try to use tor proxy to prevent
                        from blocking IP by the website
  -p PAGE, --page PAGE  Assign the maximum page
  -s [SAVE], --save [SAVE]
                        Store the result. You can specify your filename.
                        Please use .xls or .xlsx as filename extension.
  --building {1,2,3,4,5,6,7,8,9,A,B,共同,普通,新生,綜合,博雅,%}
                        Specify the building you want to query. If the
                        building belongs to a college(ex:College of Electrical
                        Engineering and Computer Science), use the code of
                        that college(ex:9),or simply type the name of the
                        building(ex:博雅).
```
You can view all help message by typing
```
python3 crawl.py -h
```