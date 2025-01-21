""" Generate sample data for testing

Execute and writes to file. Then do whatever you need. 
"""
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset
from pynetdicom.sop_class import ModalityWorklistInformationFind
from pydicom.filewriter import FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, PYDICOM_IMPLEMENTATION_UID
import json

def make_sample_MWL(modality, startdate, starttime):
    # Create the main dataset
    ds = Dataset()

    # Specific Character Set for ISO 8859-1 (Latin alphabet No. 1)
    ds.SpecificCharacterSet = 'ISO_IR 100'

    # Sample accession number
    ds.AccessionNumber = "TOPS-123456"

    # Sample patient data
    ds.PatientName = "Doe^John^^Mr"
    ds.PatientID = "123456789"
    ds.PatientBirthDate = "19800101"  # January 1st, 1980
    ds.PatientSex = "M"

    # Study instance UID
    ds.StudyInstanceUID = generate_uid()

    # Requested procedure info
    ds.RequestedProcedureID = "PROC-98765"
    ds.RequestedProcedureComments = "Patient has been experiencing mild chest pain."
    ds.RequestedProcedureDescription = "Chest X-ray"

    # Scheduled Procedure Step Sequence
    ds.ScheduledProcedureStepSequence = [Dataset()]
    sps = ds.ScheduledProcedureStepSequence[0]

    # Modality for the procedure (X-ray in this case)
    sps.Modality = modality

    sps.ScheduledProcedureStepStartDate = startdate
    sps.ScheduledProcedureStepStartTime = starttime

    # Scheduled physician information
    sps.ScheduledPerformingPhysicianName = "Smith^Robert^^Dr"

    # Procedure step details
    sps.ScheduledProcedureStepID = "STEP-001"
    sps.ScheduledProcedureStepDescription = "X-ray of the chest"

    # Location of the procedure (e.g., specific room and chair) max 16 characters
    sps.ScheduledProcedureStepLocation = "Room 101-Chair A"

    sps.ScheduledProtocolCodeSequence = [Dataset()]
    spc = sps.ScheduledProtocolCodeSequence[0]
    spc.CodeValue = "EV19"
    spc.CodingSchemeDesignator = "99OPOR"
    spc.CodeMeaning = "Extraoral, Full Face, Full Smile, Centric Occlusion"

    # Properly add a new Dataset to the list
    ev20 = Dataset()
    ev20.CodeValue = "EV20"
    ev20.CodingSchemeDesignator = "99OPOR"
    ev20.CodeMeaning = "Extraoral, Full Face, Full Smile, Centric Relation"
    sps.ScheduledProtocolCodeSequence.append(ev20)

    # Requesting physician details
    ds.RequestingPhysician = "Brown^Emily^^Dr"

    # SOP Class and Instance UID
    ds.SOPClassUID = ModalityWorklistInformationFind
    ds.SOPInstanceUID = generate_uid()

    # File Meta information (if necessary)
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = generate_uid()
    file_meta.MediaStorageSOPInstanceUID = ds.StudyInstanceUID
    file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian if not ds.is_implicit_VR else ImplicitVRLittleEndian

    ds.file_meta = file_meta

    return ds

def main():
    # Generate three different MWL instances
    mwl_CT = make_sample_MWL(modality='CT', startdate='20241208', starttime='080000')
    mwl_VL = make_sample_MWL(modality='VL', startdate='20241209', starttime='090000')
    mwl_DX = make_sample_MWL(modality='DX', startdate='20241210', starttime='100000')

    # Save them to files
    mwl_CT.save_as('mwl_CT.dcm', write_like_original=False)
    mwl_VL.save_as('mwl_VL.dcm', write_like_original=False)
    mwl_DX.save_as('mwl_DX.dcm', write_like_original=False)

    print(mwl_CT)
    print(mwl_VL)
    print(mwl_DX) 

if __name__ == "__main__":
    main()
