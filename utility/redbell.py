#Functiuon for Date Conversion
from datetime import datetime, timedelta
from dateutil import parser
import logging


def date_conversion(data):
    try:
        if data=='' or data=='00/00/0000':
            formatted_date=''
        # Parse the date using dateutil.parser
        else:
            date_obj = parser.parse(data, fuzzy=True)
            # Format the date as "%m/%d/%Y"
            formatted_date = date_obj.strftime("%m/%d/%Y")
        logging.info("date after Date Conversion:{}".format(formatted_date))
    except Exception as e:
        logging.info("Exception in Date Conversion:{}".format(e))
        formatted_date=''
    return formatted_date

#Function for Yestarday date Conversion
def yesterday_date_conversion():  
    try:
        today = datetime.now()
        # Calculate yesterday's date 
        yesterday = today - timedelta(days=1)
        # Print yesterday's date
        yesterday_date=yesterday.strftime('%m/%d/%Y')
        logging.info("date after yesterday_date Conversion:{}".format((yesterday_date)))
    except Exception as e:
        logging.info("Exception in yesterday date conversion :{}".format((e)))
        yesterday_date=''
    return yesterday_date
