# NTU Class Crawler

## Introduction

This is a program that can crawl data of classes in next semester from
"classroom management system(‰∏äË™≤?ôÂÆ§?ãÊùø)". With this program, you can arrange your classes before they come out at NTU online. While the information is not quite
complete on the website, it is still a useful and helpful tool if you want to
organize the curriculum for next semester in advance. The reference link is
http://gra206.aca.ntu.edu.tw/classrm/index.php/acarm/webcr-use1-new.

## Environment
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.7-green.svg"></a> and the following libraries are required.


> <img src="https://img.shields.io/badge/python-BeautifulSoup4 %7C pandas %7C openpyxl %7C argparse %7C requests-blue">



## Usage

```
python3 crawl.py
```
It is recommended to store the result into excel. To store your result, you can type
```
python3 crawl.py --save [FILENAME].xls
```
## Optional Arguments
```
optional arguments:
  -h, --help            show this help message and exit
  --semester SEMESTER   Select the semester you want to query. The default value is 1092
  --delay-time DELAY    Set the delay time between each request
  --tor                 (NOT IMPLETEMENTED)Try to use tor proxy to prevent from blocking IP by the website
  -p PAGE, --page PAGE  Assign the maximum page
  -s [SAVE], --save [SAVE]
                        Store the result. You can specify your filename.
                        Please use .xls or .xlsx as filename extension.
  -b {1,2,3,4,5,6,7,8,9,A,B,?±Â?,?ÆÈÄ??∞Á?,Á∂úÂ?,?öÈ?,%}
                        Specify the building you want to query.
                        If the building belongs to a college(ex:College of Electrical Engineering and Computer Science),
                        use the code of that college(ex:9),or simply type the name of the building(ex:?öÈ?).
                        The percentage sign means search for all buildings.
  --search-opt SEARCHOPT

                        Comma separated values to specifiy search options e.g. "Title=Á©çÈ??ªË∑Ø,Classroom=?ª‰?"
                        The avaliable args include:
                            "Id": Curriculum Identity Number
                            "Class": The class number. If the course is teached by only one teacher, it is set to 00
                            "Title": Course title
                            "Instructor": Teacher name
                            "Classroom": Schedule Classroom
                            "Time": The time of course

                        For example, if you type "--search-opt Title=Á©çÈ??ªË∑Ø,Classroom=?ª‰?", you may get the following result:
                                    Id Class        Title Instructor Classroom    Time
                        0  943U0010    00       Á©çÈ??ªË∑ØÊ∏¨Ë©¶        ?éÂª∫Ê®?    ?ª‰?146  ‰∫?,3,4
                        1  921U9590    00  ?ªÂ??ªÂ??áÁ?È´îÈõªË∑ØÊéß??       ?≥ÊôØ??    ?ª‰?225  ‰∫?,8,9
                        2  943U0120    00     Â∞ÑÈ†ªÁ©çÈ??ªË∑ØË®≠Ë?        ?≥ÊÄ°ÁÑ∂     ?ª‰?104  ‰∏?,3,4
                        3  90140500    00       Á©çÈ??ªË∑ØË®≠Ë?        ?ßÂ???    ?ª‰?229  ‰∏?,8,9
                        4  942U0120    00     ÂæÆÊ≥¢Á©çÈ??ªË∑ØÂ∞àÈ?        ?óÂù§‰Ω?    ?ª‰?101  ??,8,9


```
You can view all help message by typing
```
python3 crawl.py -h
```
## Examples

If you want to find the class whose name is Ê©üÂô®Â≠∏Á? in EECS and store the result to excel with filename <code>ML.xls</code>, you can use
```
python3 crawl.py --search-opt Title=Ê©üÂô®Â≠∏Á? --save ML.xls -b 9
```
or maybe you just want to find the classes teached in Bioresources and Agriculture college, you can just type
```
python3 crawl.py -b 6
```
## The problem you probably will meet

If you failed to write the data in excel file, try to install openpyxl by typing
```
pip install openpyxl
``` 
Openpyxl is a Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files. Without it, you would be failed to write the data in excel file 


