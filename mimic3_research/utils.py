from datetime import datetime


def convert_to_date_time_object(data_string):
    """
    converts a string to a datetime object.
    expceted string formats:
            - day/month/year 0:00:00 . for example : 13/03/2075  0:00:00
            - year-month-day 00:00:00 . for example : 1864-11-16 00:00:00
    :param data_string:
    :return:
    """
    if data_string == '':
        return data_string
    else:
        try:
            date_object = datetime.strptime(data_string, '%d/%m/%Y %H:%M:%S')
            return date_object
        except ValueError as e:
            if str(e) != "time data '" + data_string + "' does not match format '%d/%m/%Y %H:%M:%S'":
                print str(e)
                raise e
        date_object = datetime.strptime(data_string, '%Y-%m-%d %H:%M:%S')
    return date_object


if __name__ == "__main__":
    d1 = convert_to_date_time_object('30/08/2108  15:00:00')
    d2 = convert_to_date_time_object('12/11/2188  9:25:47')
    print d2
    d3 = convert_to_date_time_object('1879-08-01 00:00:00')
    print d3
