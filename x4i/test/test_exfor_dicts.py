import unittest
from x4i import exfor_dicts


class TestX4Dicts(unittest.TestCase):

    def setUp(self):
        self.d = exfor_dicts.X4DictionaryServer()

    def test_index(self):
        self.assertEqual(self.d.getDictionaryIndex("Particles"), 33)
        self.assertEqual(self.d.getDictionaryIndex("ConferencesAndBooks"), 7)

    def test_index(self):    
        self.assertEqual(self.d.getDictionaryName(7), "ConferencesAndBooks")
        self.assertEqual(self.d.getDictionaryName(33), "Particles")

    def test_getitem(self):
        self.assertEqual(self.d['Institutes']['KAP'], ['Knolls Atomic Power Laboratory, Schenectady, NY', 'USA'])
        self.assertEqual(self.d['Particles']['K'], ['Kaons,unspecified'])
        self.assertEqual(self.d['Compounds']['14-SI-CMP'], ['Silicon compound'])
        self.assertEqual(self.d["ConferencesAndBooks"]['69STUDSVIK'], ['Neutron Capture Gamma-Ray Spectroscopy,Studsvik,1969'])
        self.assertEqual(self.d['Process']['PAI'], ['Pair production'])
        self.assertEqual(self.d['Quantities'][',SIG'], ['Cross section'])
    
    def test_new_vs_old(self):
        #print(exfor_dicts.ALL_DICTIONARIES[str(self.d.getDictionaryIndex("Facility")).zfill(3)])
        self.assertEqual(self.d['Facility']['FRS'], ['Fragment separator'])
        self.assertEqual(exfor_dicts.ALL_DICTIONARIES[str(self.d.getDictionaryIndex("Facility")).zfill(3)]['FRS']['expansion'], 
                         'Fragment separator')
        self.assertEqual(exfor_dicts.get_dict_entry('Facilities', 'FRS')["expansion"], 'Fragment separator')
        self.assertEqual(exfor_dicts.get_dict_entry('Particles', 'K')["expansion"], 'Kaons,unspecified')
        self.assertEqual(exfor_dicts.get_dict_entry('Institutes', '1USAKAP')["expansion"], 
                         'Knolls Atomic Power Laboratory, Schenectady, NY')
        self.assertEqual(exfor_dicts.get_dict_entry('Conferences', '69STUDSVIK')["expansion"], 'Neutron Capture Gamma-Ray Spectroscopy,Studsvik,1969')
        self.assertEqual(exfor_dicts.get_dict_entry('Processes (REACTION SF 3)', 'PAI')["expansion"], 'Pair production')
        self.assertEqual(exfor_dicts.get_dict_entry('Quantities (REACTION SF 5-8)', ',SIG')["expansion"], 'Cross section')

    def test_particle_like_contents(self):
        """
        (33, "Particles")
        (9, "Compounds"), #209
        """
        self.assertEqual(list(self.d.getDictionary(self.d.getDictionaryIndex("Particles")).keys()), 
            ['0', 'A', 'AR', 'AN', 'AP', 'B', 'B+', 'B-', 'D', 'DG', 'DN', 'E', 'EC', 'ER', 'ETA', 
             'FF', 'G', 'HCP', 'HE2', 'HE3', 'HE6', 'HF', 'ICE', 'K', 'KN', 'KP', 'LCP', 'LF', 'N', 
             'P', 'PI', 'PI0', 'PIN', 'PIP', 'PN', 'RCL', 'RSD', 'SF', 'T', 'XR']) 
        self.assertEqual(list(self.d.getDictionary(self.d.getDictionaryIndex("Compounds")).keys()), 
            ['1-D-D2O', '1-D-DXX', '1-H-ARM', '1-H-BNZ', '1-H-BUT', '1-H-CMP', '1-H-CXX', '1-H-D2O', 
             '1-H-DXX', '1-H-ETH', '1-H-MTH', '1-H-PFN', '1-H-PHL', '1-H-PLE', '1-H-PRO', '1-H-TXX', 
             '1-H-WTR', '1-T-TXX', '2-HE-CMP', '3-LI-CMP', '4-BE-CMP', '4-BE-OXI', '5-B-CMP', '5-B-OXI', 
             '6-C-CMP', '7-N-AIR', '7-N-AMM', '7-N-CMP', '8-O-CMP', '9-F-CMP', '11-NA-CMP', '12-MG-CMP', 
             '12-MG-OXI', '13-AL-CMP', '13-AL-OXI', '14-SI-CMP', '14-SI-OXI', '15-P-CMP', '16-S-CMP', 
             '17-CL-CMP', '19-K-CMP', '20-CA-CMP', '20-CA-OXI', '22-TI-CMP', '22-TI-HYD', '22-TI-OXI', 
             '23-V-CMP', '24-CR-CMP', '24-CR-OXI', '25-MN-CMP', '26-FE-CMP', '26-FE-OXI', '27-CO-CMP', 
             '27-CO-OXI', '28-NI-CMP', '29-CU-CMP', '30-ZN-CMP', '31-GA-CMP', '32-GE-CMP', '32-GE-OXI', 
             '33-AS-CMP', '33-AS-OXI', '34-SE-CMP', '35-BR-CMP', '37-RB-CMP', '38-SR-CMP', '38-SR-OXI', 
             '39-Y-CMP', '40-ZR-ALY', '40-ZR-CMP', '40-ZR-HYD', '40-ZR-OXI', '41-NB-CMP', '44-RU-CMP', 
             '44-RU-OXI', '45-RH-CMP', '46-PD-CMP', '47-AG-CMP', '48-CD-CMP', '48-CD-OXI', '49-IN-CMP', 
             '50-SN-CMP', '50-SN-OXI', '51-SB-CMP', '52-TE-CMP', '52-TE-OXI', '53-I-CMP', '55-CS-CMP', 
             '56-BA-CMP', '57-LA-CMP', '57-LA-OXI', '58-CE-CMP', '58-CE-OXI', '59-PR-CMP', '59-PR-OXI', 
             '60-ND-CMP', '62-SM-CMP', '63-EU-CMP', '63-EU-OXI', '64-GD-OXI', '65-TB-CMP', '65-TB-OXI', 
             '66-DY-CMP', '66-DY-OXI', '67-HO-CMP', '67-HO-OXI', '68-ER-CMP', '68-ER-OXI', '69-TM-OXI', 
             '70-YB-CMP', '71-LU-OXI', '72-HF-CMP', '73-TA-CMP', '73-TA-OXI', '74-W-CMP', '74-W-OXI', 
             '75-RE-CMP', '78-PT-CMP', '79-AU-CMP', '80-HG-CMP', '80-HG-OXI', '81-TL-CMP', '81-TL-OXI', 
             '82-PB-CMP', '83-BI-CMP', '83-BI-OXI', '90-TH-CMP', '90-TH-OXI', '92-U-CMP', '92-U-OXI', '94-PU-CMP']) 

    def test_reaction_like_contents(self):
        """
        (30, "Process"),
        (36, "Quantities"), #113
        """
        pass 

    def test_institute_contents(self):
        """(3, "Institutes"),"""
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("Institutes"))), 1019)

    def test_facility_like_contents(self):
        """
        (18, "Facility"),
        (19, "IncidentSource"),
        """
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("Facility"))), 32)
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("IncidentSource"))), 41)

    def test_reference_like_contents(self):
        """
        (4, "ReferenceTypes"),    
        (5, "Journals"),
        (7, "ConferencesAndBooks"),
        """
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("ReferenceTypes"))), 14)
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("Journals"))), 428)
        self.assertEqual(len(self.d.getDictionary(self.d.getDictionaryIndex("ConferencesAndBooks"))), 474)

    def test_dataheadings_contents(self):
        """(24, "DataHeadings"),"""
        pass

    def test_datatype_contents(self):
        """(35, "DataType"),"""
        pass
            

