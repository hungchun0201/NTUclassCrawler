# NTU Class Crawler

## Introduction

This is a program that can crawl data of classes in next semester from
"classroom manage system(上課教室看板)". By utilizing this program, you can plan
your curriculum early than NTU online. While the information is not quite
complete on the website, it is still a useful and helpful tool if you want to
organize the curriculum in next semester. The reference link is
http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new.

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
  --tor                 (NOT IMPLETEMENTED)Try to use tor proxy to prevent
                        from blocking IP by the website
  -p PAGE, --page PAGE  Assign the maximum page
  -s [SAVE], --save [SAVE]
                        Store the result. You can specify your filename.
                        Please use .xls or .xlsx as filename extension.
  --building {0,1,2,3,4,5,6,7,8,9,A,B,共同,普通,新生,綜合,博雅,%}
                        Specify the building you want to query. If the
                        building belongs to a college(ex:College of Electrical
                        Engineering and Computer Science), use the code of
                        that college(ex:9),or simply type the name of the
                        building(ex:博雅).
```
You can view all message by typing
```
python3 crawl.py -h
```