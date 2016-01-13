def parse_date( date):
    # parse a date in this format: "JAN 09, 2016"
    date_array = date.split(" ")
    month = date_array[0]
    if month == "JAN":
        month = "01"
    elif month == "FEB":
        month = "02"
    elif month == "MAR":
        month = "03"
    elif month == "APR":
        month = "04"
    elif month == "MAY":
        month = "05"
    elif month == "JUN":
        month = "06"
    elif month == "JUL":
        month = "07"
    elif month == "AUG":
        month = "08"
    elif month == "SEP":
        month = "09"
    elif month == "OCT":
        month = "10"
    elif month == "NOV":
        month = "11"
    elif month == "DEC":
        month = "12"

    day = date_array[1][:2]
    year = date_array[2]
    return year + "-" + month + "-" + day

print(parse_date("NOV 27, 2015"))