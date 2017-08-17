import utils
import logging

class Event(object):
    """
    class event is a base class which implements an object which describes a data event of a patient in the icu
    there are 3 type of events:
    1. Chart event
    2. Lab events
    3. Output events
        Attributes:
            - ITEMID: identifier for a single measurement type in the database
            - CHARTTIME: records the time at which an observation was made, and is usually the closest proxy to the time
             the data was actually measured
            - VALUE contains the value measured for the concept identified by the ITEMID.
            - VALUENUM: If the value is numeric, then VALUENUM contains the same data in a numeric format. If this
            data is not numeric, VALUENUM is null. In some cases (e.g. scores like Glasgow Coma Scale,
            Richmond Sedation Agitation Scale and Code Status), VALUENUM contains the score and VALUE contains
            the score and text describing the meaning of the score.
            - VALUEUOM is the unit of measurement for the VALUE, if appropriate




    """
    def __init__(self, item_id, chart_time, value, value_num, value_unit_of_measurement):
        self.item_id = int(item_id)
        self.chart_time = utils.convert_to_date_time_object(chart_time)
        self.value = value
        if Event.is_number_repl_isdigit(value):
            self.value = float(value)
            if value_num == "":
                logging.warning("Value is numeric but valunum in empty. value: %d", value)
                self.value_num = value_num
            else:
                self.value_num = float(value_num)
                assert value_num == value

        self.value_unit = value_unit_of_measurement

    @staticmethod
    def is_number_repl_isdigit(s):
        """ Returns True if string is a number. """
        return s.replace('.', '', 1).isdigit()


class ChartEvent(Event):
    """
    class implents chart evetns: CHARTEVENTS contains all the charted data available for a patient. During their ICU
    stay, the primary repository of a patient's information is their electronic chart. The electronic chart displays
    patients routine vital signs and any additional information relevant to their care: ventilator settings, laboratory
     values, code status, mental status, and so on. As a result, the bulk of information about a patient's stay is
     contained in CHARTEVENTS. Furthermore, even though laboratory values are captured elsewhere (LABEVENTS),
     they are frequently repeated within CHARTEVENTS. This occurs because it is desirable to display the laboratory
     values on the patient's electronic chart, and so the values are copied from the database storing laboratory
     values to the database storing the CHARTEVENTS

        Attributes:
            - All event attributes are derived.
            - STORETIME: records the time at which an observation was manually input or manually validated by a member
            of the clinical staff.
            - CGID: the identifier for the caregiver who validated the given measurement.
            - WARNING: Metavision specific column which specify if a warning for the value was raised
            - ERROR: ERROR are Metavision specific column which specify if an error occurred during the measurement.
            - RESULTSTATUS: CareVue specific column which specify the type of measurement (RESULTSTATUS is 'Manual' or
             'Automatic').
            - STOPPED: whether the measurement was stopped.
    """
    def __init__(self, item_id, chart_time, value, value_num, value_unit_of_measurement, store_time, cgid, warning,
                 error, result_status, stopped):
        Event.__init__(self, item_id, chart_time, value, value_num, value_unit_of_measurement)
        self.store_time = utils.convert_to_date_time_object(store_time)
        self.cgid = cgid
        self.warning = warning
        self.error = error
        self.result_status = result_status
        self.stopped = stopped
