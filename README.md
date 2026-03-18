Thorough api request for horoscopedeploy.ru which returns deploy horoscope for a current day
-------------
Based on https://deployhoroscope.ru

Before starting a program install libraries: 

import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

import requests
