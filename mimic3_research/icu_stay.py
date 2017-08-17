import logging
import utils

class IcuStay(object):
    """
    class that reads information from the icu_stay.csv file. a patient might have multiple icu stays
    The hospital and ICU databases are not intrinsically linked and so do not have any concept of an ICU encounter
     identifier.
        Attributes:
            - ICUSTAY_ID: unique to a patient ICU stay
            - DBSOURCE : DBSOURCE contains the original ICU database the data was sourced from.
            - FIRST_CAREUNIT :  the first  ICU type in which the patient was cared for. As an ICUSTAY_ID groups
             all ICU admissions within 24 hours of each other, it is possible for a patient to be transferred from one
             type of ICU to another and have the same ICUSTAY_ID.
            - LAST_CAREUNIT : the last  ICU type in which the patient was cared for.
            - FIRST_WARDID : contain the first ICU unit in which the patient stayed. Note the grouping of
            physical locations in the hospital database is referred to as ward. Though in practice ICUs are not
            referred to as wards, the hospital database technically tracks ICUs as "wards with an ICU cost center".
            As a result, each ICU is associated with a WARDID
            - contain the last ICU unit in which the patient stayed.
            - INTIME: provides the date and time the patient was transferred into the ICU.
            - OUTTIME: provides the date and time the patient was transferred out of the ICU.
            - LOS: is the length of stay for the patient for the given ICU stay, which may include one or more ICU units
            - was_tranferd : boolean indecating if the patient was transfered during his icu stay.

            - time_series : dictionary that each key is a time and the value is a doctionay of events that happend at
            that time.

    """
    def __init__(self, icu_stay_id, db_source, first_care_u, last_care_u, first_ward_id, last_ward_id, in_time,
                 out_time, len_of_stay):
        """Init Patient with all the attributes defined in the patients.csv file."""
        self.icu_stay_id = int(icu_stay_id)
        self.db_source = db_source
        self.first_care_u = first_care_u
        self.last_care_u = last_care_u
        self.first_ward_id = first_ward_id
        self.last_ward_id = last_ward_id
        self.in_time = utils.convert_to_date_time_object(in_time)
        self.out_time = utils.convert_to_date_time_object(out_time)
        self.len_of_stay = len_of_stay
        if self.len_of_stay != '':
            self.len_of_stay = float(len_of_stay)

        self.was_tranferd = ((self.first_ward_id != self.last_ward_id) or (self.first_care_u != self.last_care_u))

        self.time_series = {}

    def add_event(self, event):
        """
        adds an event object to a patient.
        :param event:
        :return:
        """
        event_time = event.chart_time
        if event_time in self.time_series.keys():
            if event.item_id in self.time_series[event_time].keys():
                logging.warning("item_id %d was already inserted in the current time %s", event.item_id, str(event_time))
                # raise ValueError("item_id %d was already inserted in the current time %s", event.item_id,
                #                 str(event_time))

            self.time_series[event_time][event.item_id] = event

        else:
            self.time_series[event_time] = {}
            self.time_series[event_time][event.item_id] = event

        return
