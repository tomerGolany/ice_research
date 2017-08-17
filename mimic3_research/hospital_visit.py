import logging
import utils


class HospitalVisit:
    """Info of a single hospital visit is saved in this object. a patient object might have multiple visits in the
    hospital

        Attributes:
            - HADM_ID: represents a single patient's admission to the hospital. ranges from 1000000 - 1999999.
            - ADMITTIME: provides the date and time the patient was admitted to the hospital.
            - DISCHTIME: provides the date and time the patient was discharged from the hospital.
            - DEATHTIME: provides the time of in-hospital death for the patient.
            Note that DEATHTIME is only present if the patient died in-hospital, and is almost always the same as the
             patients DISCHTIME

            - ADMISSION_TYPE: describes the type of the admission: 'ELECTIVE', 'URGENT', 'NEWBORN' or 'EMERGENCY'.
            Emergency/urgent indicate unplanned medical care, and are often collapsed into a single category in studies.
             Elective indicates a previously planned hospital admission. Newborn indicates that the HADM_ID pertains to
            the patient's birth

            - ADMISSION_LOCATION: provides information about the previous location of the patient prior to arriving at
            the hospital. There are 9 possible values:

                        EMERGENCY ROOM ADMIT
                        TRANSFER FROM HOSP/EXTRAM
                        TRANSFER FROM OTHER HEALT
                        CLINIC REFERRAL/PREMATURE
                        ** INFO NOT AVAILABLE **
                        TRANSFER FROM SKILLED NUR
                        TRSF WITHIN THIS FACILITY
                        HMO REFERRAL/SICK
                        PHYS REFERRAL/NORMAL DELI

            - INSURANCE:
            - LANGUAGE:
            - RELIGION:
            - MARITAL_STATUS:
            - ETHNICITY:

            - EDREGTIME: Time that the patient was registered the emergency department
            - EDOUTTIME: Time that the patient was discharged the emergency department
            - DIAGNOSIS: The DIAGNOSIS column provides a preliminary, free text diagnosis for the patient on hospital
            admission. The diagnosis is usually assigned by the admitting clinician and does not use a systematic
            ontology. As of MIMIC-III v1.0 there were 15,693 distinct diagnoses for 58,976 admissions.
            The diagnoses can be very informative (e.g. chronic kidney failure) or quite vague (e.g. weakness).
            Final diagnoses for hospital admissions are coded and can be found in the DIAGNOSES_ICD table.

            -icu_stays : dict of all icu stays during patients admission.

    """

    def __init__(self, hadm_id, admittime, dischtime, death_time, admission_type, admission_location, insurance,
                 language, religion, martial_status, etnhicity, ed_reg_time, ed_out_time, diagnosis):
        """Init hospital_visit with all the attributes defined in the admissions.csv file."""
        '''
        if int(hadm_id) < 1000000 or int(hadm_id) > 1999999:
            logging.error('hadm_id %d not in range.', hadm_id)
            raise ValueError('HADM_ID not in a valid range', hadm_id)
        '''
        self.hadm_id = int(hadm_id)
        self.admittime = utils.convert_to_date_time_object(admittime)
        self.dischtime = utils.convert_to_date_time_object(dischtime)
        self.death_time = utils.convert_to_date_time_object(death_time)

        if death_time != '' and death_time != dischtime:
            logging.warning("Death time and disch time are not the same for hadm_id: %d", self.hadm_id)

        if admission_type not in ['ELECTIVE', 'URGENT', 'NEWBORN', 'EMERGENCY']:
            logging.error('admission_type invalid value %s', admission_type)
            raise ValueError('admission_type invalid value %s', admission_type)

        self.admission_type = admission_type

        if admission_location not in ['EMERGENCY ROOM ADMIT', 'TRANSFER FROM HOSP/EXTRAM', 'TRANSFER FROM OTHER HEALT',
                                      'CLINIC REFERRAL/PREMATURE', '** INFO NOT AVAILABLE **',
                                      'TRANSFER FROM SKILLED NUR', 'TRSF WITHIN THIS FACILITY', 'HMO REFERRAL/SICK',
                                      'PHYS REFERRAL/NORMAL DELI']:
            logging.error('admission_location invalid value %s', admission_location)
            raise ValueError('admission_location invalid value %s', admission_location)

        self.admission_location = admission_location

        if insurance not in ['Private', 'Medicare', 'Medicaid', 'Government', 'Self Pay'] :
            logging.error('insurance %s invalid.', insurance)
            raise ValueError('insurance invalid value %s', insurance)

        self.insurance = insurance
        self.language = language
        self.religion = religion
        self.martial_status = martial_status
        self.etnhicity = etnhicity
        self.ed_reg_time = utils.convert_to_date_time_object(ed_reg_time)
        self.ed_out_time = utils.convert_to_date_time_object(ed_out_time)
        self.diagnosis = diagnosis

        self.icu_stays = {}
        self.num_of_icu_stays = 0

    def add_icu_stay(self, icu_stay):
        """
        Add an icu_stay to an admission.
        :param icu_stay:
        :return:
        """
        if icu_stay.icu_stay_id in self.icu_stays.keys():
            logging.error('icu_stay_id already exists in this admission. adm %d, icu_stay %d', self.hadm_id,
                          icu_stay.icu_stay_id)
            raise ValueError('icu_stay_id already exists in this admission. adm %d, icu_stay %d', self.hadm_id,
                          icu_stay.icu_stay_id)

        self.icu_stays[icu_stay.icu_stay_id] = icu_stay

    def add_event(self, event, icu_stay_id):
        """
        adds an event to an icu stay.
        :param event: the event to be added
        :param icu_stay_id : id of the icu stay
        :return:
        """
        if icu_stay_id not in self.icu_stays.keys():
            logging.warning("event from icu stay id %d  doesn't belong to any of the icu stays in this admission %d",
                            icu_stay_id, self.hadm_id)
            return

        self.icu_stays[icu_stay_id].add_event(event)

