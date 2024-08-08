.. _csv_file_codes:

Codes CSV File Format Documentation
===================================

Introduction
------------

This documentation describes the structure of the CSV file used to manage and catalog various codes within our system. Each field in the CSV file is crucial for understanding the use and context of the codes listed.

File Structure
--------------

The CSV file contains the following columns, each providing specific details about the codes:

.. list-table:: CSV Header Descriptions
   :widths: 20 80
   :header-rows: 1

   * - Header
     - Description
   * - keyword
     - A unique identifier or key associated with each record. This is the key that will be used in :ref:`csv_file_views`.
   * - code
     - The code that defines this term, according to the codeset used.
   * - codeset
     - The codeset that defined the coded (e.g. DCM, SCT, ...)
   * - meaning
     - The official meaning of this code, or what you would like to appear in the DICOM file. Must carry the same meaning.
   * - used for
     - The DICOM tag this code is used for.
   * - notes
     - Additional information or remarks about the code.

Example Records
---------------

Below is an example record in the CSV format:

.. code-block:: none

    TemporalEventType,128741,DCM,Longitudinal Temporal Event Type,AcquisitionContextSequence^LongitudinalTemporalEventType,A pre-defined type of a specific time point in a continuum.

Conclusion
----------

This document serves as a reference for the CSV file format utilized by our system. Understanding each column's function and the information it holds is essential for accurate data management and utilization.
