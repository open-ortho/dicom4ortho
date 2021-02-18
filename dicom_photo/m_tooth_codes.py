''' Tooth code related objects.

The code meaning is an LO (Long String) VR (Value Representiation, aka data
type) in DICOM which has a limit of 64 character.

'''

SCT_TOOTH_CODES = {
    '11': ['245575001', 'Entire permanent maxillary right central incisor tooth'],
    '12': ['245574002', 'Entire permanent maxillary right lateral incisor tooth'],
    '13': ['245572003', 'Entire permanent maxillary right canine tooth'],
    '14': ['245571005', 'Entire permanent maxillary right first premolar tooth'],
    '15': ['245570006', 'Entire permanent maxillary right second premolar tooth'],
    '16': ['245568002', 'Entire permanent maxillary right first molar tooth'],
    '17': ['245567007', 'Entire permanent maxillary right second molar tooth'],
    '18': ['245566003', 'Entire permanent maxillary right third molar tooth'],
    '21': ['245587008', 'Entire permanent maxillary left central incisor tooth'],
    '22': ['245586004', 'Entire permanent maxillary left lateral incisor tooth'],
    '23': ['245584001', 'Entire permanent maxillary left canine tooth'],
    '24': ['245583007', 'Entire permanent maxillary left first premolar tooth'],
    '25': ['245582002', 'Entire permanent maxillary left second premolar tooth'],
    '26': ['245579007', 'Entire permanent maxillary left first molar tooth'],
    '27': ['245578004', 'Entire permanent maxillary left second molar tooth'],
    '28': ['245577009', 'Entire permanent maxillary left third molar tooth'],
    '31': ['245611006', 'Entire permanent mandibular left central incisor tooth'],
    '32': ['245610007', 'Entire permanent mandibular left lateral incisor tooth'],
    '33': ['245608005', 'Entire permanent mandibular left canine tooth'],
    '34': ['245607000', 'Entire permanent mandibular left first premolar tooth'],
    '35': ['245606009', 'Entire permanent mandibular left second premolar tooth'],
    '36': ['245604007', 'Entire permanent mandibular left first molar tooth'],
    '37': ['245603001', 'Entire permanent mandibular left second molar tooth'],
    '38': ['245602006', 'Entire permanent mandibular left third molar tooth'],
    '41': ['245600003', 'Entire permanent mandibular right central incisor tooth'],
    '42': ['245599001', 'Entire permanent mandibular right lateral incisor tooth'],
    '43': ['245597004', 'Entire permanent mandibular right canine tooth'],
    '44': ['245596008', 'Entire permanent mandibular right first premolar tooth'],
    '45': ['245595007', 'Entire permanent mandibular right second premolar tooth'],
    '46': ['245592005', 'Entire permanent mandibular right first molar tooth'],
    '47': ['245591003', 'Entire permanent mandibular right second molar tooth'],
    '48': ['245590002', 'Entire permanent mandibular right third molar tooth'],
    '51': ['245620002', 'Entire deciduous maxillary right central incisor tooth'],
    '52': ['245619008', 'Entire deciduous maxillary right lateral incisor tooth'],
    '53': ['245617005', 'Entire deciduous maxillary right canine tooth'],
    '54': ['245616001', 'Entire deciduous maxillary right first molar tooth'],
    '55': ['245615002', 'Entire deciduous maxillary right second molar tooth'],
    '61': ['245627004', 'Entire deciduous maxillary left central incisor tooth'],
    '62': ['245626008', 'Entire deciduous maxillary left lateral incisor tooth'],
    '63': ['245624006', 'Entire deciduous maxillary left canine tooth'],
    '64': ['245623000', 'Entire deciduous maxillary left first molar tooth'],
    '65': ['245622005', 'Entire deciduous maxillary left second molar tooth'],
    '71': ['245642001', 'Entire deciduous mandibular left central incisor tooth'],
    '72': ['245641008', 'Entire deciduous mandibular left lateral incisor tooth'],
    '73': ['245639007', 'Entire deciduous mandibular left canine tooth'],
    '74': ['245638004', 'Entire deciduous mandibular left first molar tooth'],
    '75': ['245637009', 'Entire deciduous mandibular left second molar tooth'],
    '81': ['245635001', 'Entire deciduous mandibular right central incisor tooth'],
    '82': ['245634002', 'Entire deciduous mandibular right lateral incisor tooth'],
    '83': ['245632003', 'Entire deciduous mandibular right canine tooth'],
    '84': ['245631005', 'Entire deciduous mandibular right first molar tooth'],
    '85': ['245630006', 'Entire deciduous mandibular right second molar tooth'],
}


def is_valid_tooth_number(tooth):
    ''' Check if string is a valid ISO tooth number
    '''

    # True if tooth exists as key in dict above, false otherwise.
    return tooth in SCT_TOOTH_CODES.keys()
