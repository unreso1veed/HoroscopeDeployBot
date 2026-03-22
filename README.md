Thorough api request for horoscopedeploy.ru which returns deploy horoscope for a current day and a whole month
-------------
Based on https://deployhoroscope.ru

Before starting a program install libraries: 

import argparse
import csv
import datetime
import sys
from pathlib import Path

import requests

Program creating .csv file with the data from deploy horoscope. 
