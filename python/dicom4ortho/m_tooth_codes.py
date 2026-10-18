''' Tooth code related objects.

The code meaning is an LO (Long String) VR (Value Representiation, aka data
type) in DICOM which has a limit of 64 character.

This should come directly from CID-4018 and CID-4019. How to pull? Do i need to scrape the HTML?

'''

SCT_TOOTH_CODES = {
    '11': ['245575001', '11 Entire permanent maxillary right central incisor tooth'],
    '12': ['245574002', '12 Entire permanent maxillary right lateral incisor tooth'],
    '13': ['245572003', '13 Entire permanent maxillary right canine tooth'],
    '14': ['245571005', '14 Entire permanent maxillary right first premolar tooth'],
    '15': ['245570006', '15 Entire permanent maxillary right second premolar tooth'],
    '16': ['245568002', '16 Entire permanent maxillary right first molar tooth'],
    '17': ['245567007', '17 Entire permanent maxillary right second molar tooth'],
    '18': ['245566003', '18 Entire permanent maxillary right third molar tooth'],
    '21': ['245587008', '21 Entire permanent maxillary left central incisor tooth'],
    '22': ['245586004', '22 Entire permanent maxillary left lateral incisor tooth'],
    '23': ['245584001', '23 Entire permanent maxillary left canine tooth'],
    '24': ['245583007', '24 Entire permanent maxillary left first premolar tooth'],
    '25': ['245582002', '25 Entire permanent maxillary left second premolar tooth'],
    '26': ['245579007', '26 Entire permanent maxillary left first molar tooth'],
    '27': ['245578004', '27 Entire permanent maxillary left second molar tooth'],
    '28': ['245577009', '28 Entire permanent maxillary left third molar tooth'],
    '31': ['245611006', '31 Entire permanent mandibular left central incisor tooth'],
    '32': ['245610007', '32 Entire permanent mandibular left lateral incisor tooth'],
    '33': ['245608005', '33 Entire permanent mandibular left canine tooth'],
    '34': ['245607000', '34 Entire permanent mandibular left first premolar tooth'],
    '35': ['245606009', '35 Entire permanent mandibular left second premolar tooth'],
    '36': ['245604007', '36 Entire permanent mandibular left first molar tooth'],
    '37': ['245603001', '37 Entire permanent mandibular left second molar tooth'],
    '38': ['245602006', '38 Entire permanent mandibular left third molar tooth'],
    '41': ['245600003', '41 Entire permanent mandibular right central incisor tooth'],
    '42': ['245599001', '42 Entire permanent mandibular right lateral incisor tooth'],
    '43': ['245597004', '43 Entire permanent mandibular right canine tooth'],
    '44': ['245596008', '44 Entire permanent mandibular right first premolar tooth'],
    '45': ['245595007', '45 Entire permanent mandibular right second premolar tooth'],
    '46': ['245592005', '46 Entire permanent mandibular right first molar tooth'],
    '47': ['245591003', '47 Entire permanent mandibular right second molar tooth'],
    '48': ['245590002', '48 Entire permanent mandibular right third molar tooth'],
    '51': ['245620002', '51 Entire deciduous maxillary right central incisor tooth'],
    '52': ['245619008', '52 Entire deciduous maxillary right lateral incisor tooth'],
    '53': ['245617005', '53 Entire deciduous maxillary right canine tooth'],
    '54': ['245616001', '54 Entire deciduous maxillary right first molar tooth'],
    '55': ['245615002', '55 Entire deciduous maxillary right second molar tooth'],
    '61': ['245627004', '61 Entire deciduous maxillary left central incisor tooth'],
    '62': ['245626008', '62 Entire deciduous maxillary left lateral incisor tooth'],
    '63': ['245624006', '63 Entire deciduous maxillary left canine tooth'],
    '64': ['245623000', '64 Entire deciduous maxillary left first molar tooth'],
    '65': ['245622005', '65 Entire deciduous maxillary left second molar tooth'],
    '71': ['245642001', '71 Entire deciduous mandibular left central incisor tooth'],
    '72': ['245641008', '72 Entire deciduous mandibular left lateral incisor tooth'],
    '73': ['245639007', '73 Entire deciduous mandibular left canine tooth'],
    '74': ['245638004', '74 Entire deciduous mandibular left first molar tooth'],
    '75': ['245637009', '75 Entire deciduous mandibular left second molar tooth'],
    '81': ['245635001', '81 Entire deciduous mandibular right central incisor tooth'],
    '82': ['245634002', '82 Entire deciduous mandibular right lateral incisor tooth'],
    '83': ['245632003', '83 Entire deciduous mandibular right canine tooth'],
    '84': ['245631005', '84 Entire deciduous mandibular right first molar tooth'],
    '85': ['245630006', '85 Entire deciduous mandibular right second molar tooth'],
}


def is_valid_tooth_number(tooth):
    ''' Check if string is a valid ISO tooth number
    '''

    # True if tooth exists as key in dict above, false otherwise.
    return tooth in SCT_TOOTH_CODES.keys()
