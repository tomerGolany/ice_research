import patient
import hospital_visit
import icu_stay
import event
import csv
import os
import logging
import multiprocessing
import pickle


class ICUDatabase(object):
    """ICUDatabase object contains all the information from the mimic csv files orgiinized nicely and easly
    to gain infro and build feature vectors for learning algorithms.

        Attributes:
            patients: list of all patients in the database.
            num_of_patients : Number of patients in the database.
            mimic3_dir : path to dir of all .csv files

    """
    def __init__(self, mimic3_data_files_path):
        """Init Patient with all the attributes defined in the patients.csv file.
            :param mimic3_data_files_path : path to .csv files.
        """
        self.patients = {}
        self.num_of_patients = 0
        self.total_number_of_hospital_visits = 0
        self.mimic3_dir = mimic3_data_files_path
        self.invalid_rows = []

        # Support for Multiprocessing :
        # self.mgr = multiprocessing.Manager()
        # self.patients = self.mgr.dict()

    def read_patients_table(self):
        """
        reads the PATIENTS.csv file and add patients to the database.
        :return: void
        """
        table_name = 'PATIENTS'
        reader = csv.DictReader(open(os.path.join(self.mimic3_dir, table_name + '.csv'), 'r'))

        for i, row in enumerate(reader):

            if 'SUBJECT_ID' not in row:
                logging.warning("Row %d Doesn't contain the subject id", i)
                continue
            if row['DOD'] == "":
                assert row['DOD_HOSP'] == '' and row['DOD_SSN'] == '' and row['EXPIRE_FLAG'] == '0'

            else:
                assert row['EXPIRE_FLAG'] == '1'
            if 'DOD_HOSP' not in row:
                row['DOD_HOSP'] = None
            if 'DOD_SSN' not in row:
                row['DOD_SSN'] = None

            if int(row['SUBJECT_ID']) in self.patients.keys():
                logging.error("Patient %d already exists.", int(row['SUBJECT_ID']))
                raise ValueError("Patient %d already exists.", int(row['SUBJECT_ID']))

            new_patient = patient.Patient(int(row['SUBJECT_ID']), row['GENDER'], row['DOB'], row['DOD'], row['DOD_HOSP'],
                                          row['DOD_SSN'], row['EXPIRE_FLAG'])
            self.patients[int(row['SUBJECT_ID'])] = new_patient
            self.num_of_patients += 1

            if i % 100 == 0:
                logging.info("Successfully read %d patients from PATIENTS.csv", self.num_of_patients)

        logging.info("DONE reading PATIENTS.csv, total of %d patients are saved in the database", self.num_of_patients)
        return

    def read_hospital_visits_table(self):
        """
        reads the ADMISSIONS.csv file and adds hospital visits details to each paitent.
        :return:
        """
        table_name = 'ADMISSIONS'
        reader = csv.DictReader(open(os.path.join(self.mimic3_dir, table_name + '.csv'), 'r'))
        for i, row in enumerate(reader):
            subject_id = int(row['SUBJECT_ID'])

            if subject_id not in self.patients.keys():
                logging.error("Patient %d doen't exists.", subject_id)
                raise ValueError("Patient %d doen't exists." % subject_id)

            new_hosp_visit = hospital_visit.HospitalVisit(row['HADM_ID'], row['ADMITTIME'], row['DISCHTIME'],
                                                          row['DEATHTIME'], row['ADMISSION_TYPE'],
                                                          row['ADMISSION_LOCATION'], row['INSURANCE'], row['LANGUAGE'],
                                                          row['RELIGION'], row['MARITAL_STATUS'], row['ETHNICITY'],
                                                          row['EDREGTIME'], row['EDOUTTIME'], row['DIAGNOSIS'])

            self.patients[subject_id].add_hospital_visit(new_hosp_visit)
            self.total_number_of_hospital_visits += 1

            if i % 100 == 0:
                logging.info("Successfully read %d visits from ADMISSIONS.csv", i)

        logging.info("DONE reading %d rows in ADMISSIONS.csv, total of %d visits are saved in the database", i,
                     self.total_number_of_hospital_visits)
        return

    def read_icu_stays_table(self):
        """

        :return:
        """
        table_name = 'ICUSTAYS'
        reader = csv.DictReader(open(os.path.join(self.mimic3_dir, table_name + '.csv'), 'r'))
        for i, row in enumerate(reader):
            subject_id = int(row['SUBJECT_ID'])

            if subject_id not in self.patients.keys():
                logging.error("Patient %d doen't exists.", subject_id)
                raise ValueError("Patient %d doen't exists." % subject_id)

            new_icu_stay = icu_stay.IcuStay(row['ICUSTAY_ID'], row['DBSOURCE'], row['FIRST_CAREUNIT'],
                                            row['LAST_CAREUNIT'], row['FIRST_WARDID'], row['LAST_WARDID'],
                                            row['INTIME'], row['OUTTIME'], row['LOS'])

            self.patients[subject_id].add_icu_stay(int(row['HADM_ID']), new_icu_stay)

            if i % 100 == 0:
                logging.info("Successfully read %d icu_stays from ICUSTAYS.csv", i)

        logging.info("DONE reading %d rows from ICUSTAYS.csv, total of visits are saved in the database" % i)
        return

    def read_events_table_by_row(self, table):
        """

        :param table:
        :return:
        """
        reader = csv.DictReader(open(os.path.join(self.mimic3_dir, table + '.csv'), 'r'))
        for i, row in enumerate(reader):
            yield i, row
        '''
        for i in range(0, 330712483):
            yield i, reader, self
        '''
    def read_chart_events_table(self):
        """

        :return:
        """
        table_name = 'CHARTEVENTS'
        for i, row in self.read_events_table_by_row(table_name):
            subject_id = int(row['SUBJECT_ID'])

            if subject_id not in self.patients.keys():
                logging.error("Patient %d doen't exists.", subject_id)
                raise ValueError("Patient %d doen't exists.", subject_id)

            new_chart_event = event.ChartEvent(row['ITEMID'], row['CHARTTIME'], row['VALUE'], row['VALUENUM'],
                                               row['VALUEUOM'], row['STORETIME'],row['CGID'], row['WARNING'],
                                               row['ERROR'], row['RESULTSTATUS'], row['STOPPED'])

            if row['HADM_ID'] == '' or row['ICUSTAY_ID'] == '':
                self.invalid_rows.append(new_chart_event)
                logging.warning("event without icu stay id or without adm id. row %d", i)
                continue

            self.patients[subject_id].add_event(int(row['HADM_ID']), int(row['ICUSTAY_ID']), new_chart_event)

            if i % 100 == 0:
                logging.info("Successfully read %d events from CHARTEVENTS.csv", i)

        logging.info("DONE reading CHARTEVENTS.csv, total of events are saved in the database")
        return

    def read_chart_events_paralell(self):
        """

        :return:
        """
        table_name = 'CHARTEVENTS'
        # reader = csv.DictReader(open(os.path.join(self.mimic3_dir, table_name + '.csv'), 'r'))
        pool = multiprocessing.Pool(4)
        pool.map(add_event_wrapper, [x for x in self.read_events_table_by_row(table_name)])

    def save_db_to_pickle(self):
        """

        :return:
        """
        file_to_store = open('store.pckl', 'wb')
        pickle.dump(self, file_to_store)
        f.close()

    @staticmethod
    def load_db_from_pickle():
        """

        :return:
        """
        file_to_load = open('store.pckl', 'rb')
        db_load = pickle.load(file_to_load)
        f.close()
        return db_load


def add_event(x):
    """
    :param x:
    :param database:
    :return:
    """
    i, reader, database = x
    subject_id = int(reader[i]['SUBJECT_ID'])

    if subject_id not in database.patients.keys():
        logging.error("Patient %d doen't exists.", subject_id)
        raise ValueError("Patient %d doen't exists.", subject_id)

    new_chart_event = event.ChartEvent(reader[i]['ITEMID'], reader[i]['CHARTTIME'], reader[i]['VALUE'],
                                       reader[i]['VALUENUM'],
                                       reader[i]['VALUEUOM'], reader[i]['STORETIME'], reader[i]['CGID'], reader[i]['WARNING'],
                                       reader[i]['ERROR'], reader[i]['RESULTSTATUS'], reader[i]['STOPPED'])

    if reader[i]['HADM_ID'] == '' or reader[i]['ICUSTAY_ID'] == '':
        # database.invalid_rows.append(new_chart_event)
        logging.warning("event without icu stay id or without adm id. row %d", i)
        return

    database.patients[subject_id].add_event(int(reader[i]['HADM_ID']), int(reader[i]['ICUSTAY_ID']), new_chart_event)

    if i % 100 == 0:
        logging.info("Successfully read %d events from CHARTEVENTS.csv", i)


def add_event_wrapper(args):
    return add_event(*args)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    data_files_dir = os.path.join('/', 'Users', 'tomer.golany', 'MIMIC_REPO', 'csv_files')
    demo_files_dir = os.path.join('/', 'Users', 'tomer.golany', 'PycharmProjects', 'MIMIC', 'demo_files')

    db = ICUDatabase(demo_files_dir)
    db.read_patients_table()
    db.read_hospital_visits_table()
    db.read_icu_stays_table()
    db.read_chart_events_table()
    # db.read_chart_events_paralell()

    d1 = { k: v for k, v in db.patients.iteritems() if v.num_of_hospital_visits > 1 }
    d2 = {k: v for k, v in db.patients.iteritems() if v.num_of_hospital_visits < v.total_num_of_icu_stays}

    print "DONE"