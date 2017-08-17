import logging
import utils


class Patient(object):
    """Patient data type - this file implemets the Patient class which represents all the details of a patient in
    the icu
        Attributes:
            id: An integer unique id of a patient
            gender: M/F - Male or female
            dob: DOB is the date of birth of the given patient. Patients who are older than 89 years old at any time
                in the database have had their date of birth shifted to obscure their age and comply with HIPAA.
                The shift process was as follows: the patient's age at their first admission was determined.
                The date of birth was then set to exactly 300 years before their first admission
            dod: DOD is the date of death for the given patient
            dod_hosp: DOD_HOSP is the date of death as recorded in the hospital database
            dod_ssn: DOD_SSN is the date of death from the social security database

            Note that DOD merged together DOD_HOSP and DOD_SSN, giving priority to DOD_HOSP if both were recorded.

            expire_flag: EXPIRE_FLAG is a binary flag which indicates whether the patient died, i.e. whether DOD is null
             or not. These deaths include both deaths within the hospital (DOD_HOSP) and deaths identified by matching
             the patient to the social security master death index (DOD_SSN).
        """

    def __init__(self, subject_id, gender, dob, dod, dod_hosp, dod_ssn, expire_flag):
        """Init Patient with all the attributes defined in the patients.csv file."""
        self.id = int(subject_id)
        self.gender = gender
        self.dob = utils.convert_to_date_time_object(dob)
        self.dod = utils.convert_to_date_time_object(dod)
        self.dod_hosp = utils.convert_to_date_time_object(dod_hosp)
        self.dod_ssn = utils.convert_to_date_time_object(dod_ssn)
        self.expire_flag = expire_flag

        self.hospital_visits = {}
        self.num_of_hospital_visits = 0
        self.total_num_of_icu_stays = 0

    def add_hospital_visit(self, hosp_visit):
        """
        Adds an hospital visit to the paitent visits.
        :param hosp_visit : an hospital_visit object
        :return : void
        """

        if hosp_visit.death_time != '' and self.dod_hosp == '':
            logging.warning('visit info states the patient died in hospital while patient info doesnt. '
                            'patient id: %d, hadm id: %d', self.id, hosp_visit.hadm_id)

        if hosp_visit.hadm_id in self.hospital_visits.keys():
            logging.error('hadm_id already exists in patient. patient %d, hadm_id %d', self.id, hosp_visit.hadm_id)
            raise ValueError('hadm_id already exists in patient. patient %d, hadm_id %d', self.id, hosp_visit.hadm_id)

        self.hospital_visits[hosp_visit.hadm_id] = hosp_visit
        self.num_of_hospital_visits += 1

    def add_icu_stay(self, admission_id, icu_stay):
        """
        adds an icu stay to one of the admissions of the patient.
        :param admission_id:
        :param icu_stay:
        :return:
        """
        if admission_id not in self.hospital_visits.keys():
            logging.error('hadm_id does not exists in patient. patient %d, hadm_id %d', self.id, admission_id)
            raise ValueError('hadm_id does not exists in patient. patient %d, hadm_id %d' % (self.id, admission_id))

        self.hospital_visits[admission_id].add_icu_stay(icu_stay)
        self.total_num_of_icu_stays += 1

    def add_event(self, admission_id, icu_stay_id, event):
        """
        Adds an event to the patient
        :param admission_id:
        :param icu_stay_id:
        :param event:
        :return:
        """
        if admission_id not in self.hospital_visits.keys():
            logging.error('hadm_id does not exists in patient. patient %d, hadm_id %d', self.id, admission_id)
            raise ValueError('hadm_id does not exists in patient. patient %d, hadm_id %d' % (self.id, admission_id))

        self.hospital_visits[admission_id].add_event(event, icu_stay_id)


