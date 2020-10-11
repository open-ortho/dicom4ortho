''' A module with all tooth code related objects.
'''

SCT_TOOTH_CODES = {
    '11' : ['22120004','Structure of maxillary right central incisor tooth (body structure)'],
    '12' : ['11712009','Structure of maxillary right lateral incisor tooth (body structure)'],
    '13' : ['80647007','Structure of maxillary right canine tooth (body structure)'],
    '14' : ['57826002','Structure of maxillary right first premolar tooth (body structure)'],
    '15' : ['36492000','Structure of maxillary right second premolar tooth (body structure)'],
    '16' : ['5140004','Structure of maxillary right first molar tooth (body structure)'],
    '17' : ['7121006','Structure of maxillary right second molar tooth (body structure)'],
    '18' : ['68085002','Structure of permanent maxillary right third molar tooth (body structure)'],
    '21' : ['31982000','Structure of maxillary left central incisor tooth (body structure)'],
    '22' : ['25748002','Structure of maxillary left lateral incisor tooth (body structure)'],
    '23' : ['72876007','Structure of maxillary left canine tooth (body structure)'],
    '24' : ['61897005','Structure of maxillary left first premolar tooth (body structure)'],
    '25' : ['23226009','Structure of maxillary left second premolar tooth (body structure)'],
    '26' : ['23427002','Structure of maxillary left first molar tooth (body structure)'],
    '27' : ['66303006','Structure of maxillary left second molar tooth (body structure)'],
    '28' : ['87704003','Structure of permanent maxillary left third molar tooth (body structure)'],
    '31' : ['113278005','Structure of mandibular left central incisor tooth (body structure)'],
    '32' : ['77130001','Structure of mandibular left lateral incisor tooth (body structure)'],
    '33' : ['39844006','Structure of mandibular left canine tooth (body structure)'],
    '34' : ['2400006','Structure of mandibular left first premolar tooth (body structure)'],
    '35' : ['24573005','Structure of mandibular left second premolar tooth (body structure)'],
    '36' : ['89625000','Structure of mandibular left first molar tooth (body structure)'],
    '37' : ['48402004','Structure of mandibular left second molar tooth (body structure)'],
    '38' : ['74344005','Structure of mandibular left third molar tooth (body structure)'],
    '41' : ['15422005','Structure of mandibular right central incisor tooth (body structure)'],
    '42' : ['82628004','Structure of mandibular right lateral incisor tooth (body structure)'],
    '43' : ['47055002','Structure of mandibular right canine tooth (body structure)'],
    '44' : ['80140008','Structure of mandibular right first premolar tooth (body structure)'],
    '45' : ['8873007','Structure of mandibular right second premolar tooth (body structure)'],
    '46' : ['28480000','Structure of mandibular right first molar tooth (body structure)'],
    '47' : ['40005008','Structure of mandibular right second molar tooth (body structure)'],
    '48' : ['38994002','Structure of mandibular right third molar tooth (body structure)'],
    '51' : ['88824007','Structure of deciduous maxillary right central incisor tooth (body structure)'],
    '52' : ['65624003','Structure of deciduous maxillary right lateral incisor tooth (body structure)'],
    '53' : ['30618001','Structure of deciduous maxillary right canine tooth (body structure)'],
    '54' : ['17505006','Structure of deciduous maxillary right first molar tooth (body structure)'],
    '55' : ['27855007','Structure of deciduous maxillary right second molar tooth (body structure)'],
    '61' : ['51678005','Structure of deciduous maxillary left central incisor tooth (body structure)'],
    '62' : ['43622005','Structure of deciduous maxillary left lateral incisor tooth (body structure)'],
    '63' : ['73937000','Structure of deciduous maxillary left canine tooth (body structure)'],
    '64' : ['45234009','Structure of deciduous maxillary left first molar tooth (body structure)'],
    '65' : ['51943008','Structure of deciduous maxillary left second molar tooth (body structure)'],
    '71' : ['89552004','Structure of deciduous mandibular left central incisor tooth (body structure)'],
    '72' : ['14770005','Structure of deciduous mandibular left lateral incisor tooth (body structure)'],
    '73' : ['43281008','Structure of deciduous mandibular left canine tooth (body structure)'],
    '74' : ['38896004','Structure of deciduous mandibular left first molar tooth (body structure)'],
    '75' : ['49330006','Structure of deciduous mandibular left second molar tooth (body structure)'],
    '81' : ['67834006','Structure of deciduous mandibular right central incisor tooth (body structure)'],
    '82' : ['22445006','Structure of deciduous mandibular right lateral incisor tooth (body structure)'],
    '83' : ['6062009','Structure of deciduous mandibular right canine tooth (body structure)'],
    '84' : ['58646007','Structure of deciduous mandibular right first molar tooth (body structure)'],
    '85' : ['61868007','Structure of deciduous mandibular right second molar tooth (body structure)'],
}

def is_valid_tooth_number(tooth):
    ''' Check if string is a valid ISO tooth number
    '''

    # True if tooth exists as key in dict above, false otherwise.
    return tooth in SCT_TOOTH_CODES.keys()
