"""Create a new panel trio report from an new genome trio. This requires putting all
three family genomes in a folder along with a descriptor file titled 'family_manifest.csv,'
which should have the following format:

filename,label,external_id,sex,format
NA19238.vcf.gz,CG Yoruban Mother,1,female,vcf.gz
NA19239.vcf.gz,CG Yoruban Father,2,male,vcf.gz
NA19240.vcf.gz,CG Yoruban Daughter,3,female,vcf.gz

Optionally, include a file containing patient (proband) information to populate
patient information fields in the clinical report. This file should be a csv
formatted in this way:

Opal Patient Information,value
Patient Last Name,John
Patient First Name,Doe
Patient DOB,1/1/00
Accession ID,JD1
Patient Sex,Male/Female
Patient Ethnicity,Caucasian
Indication for Testing,Disease
Specimen Type,Blood
Date Specimen Collected,9/9/14
Date Specimen Received,9/13/14
Ordering Physician,Paul Billings

If you are having trouble with using either csv file, make sure its
line endings are newlines (\n) and not the deprecated carriage returns (\r)
"""

import argparse
import csv
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import sys

_MANIFEST_FILENAME = 'panel_trio_manifest.csv'

#Load environment variables for request authentication parameters
if "OMICIA_API_PASSWORD" not in os.environ:
    sys.exit("OMICIA_API_PASSWORD environment variable missing")

if "OMICIA_API_LOGIN" not in os.environ:
    sys.exit("OMICIA_API_LOGIN environment variable missing")

OMICIA_API_LOGIN = os.environ['OMICIA_API_LOGIN']
OMICIA_API_PASSWORD = os.environ['OMICIA_API_PASSWORD']
OMICIA_API_URL = os.environ.get('OMICIA_API_URL', 'https://api.omicia.com')
auth = HTTPBasicAuth(OMICIA_API_LOGIN, OMICIA_API_PASSWORD)


# A map between the row numbers and fields from the patient information csv
patient_info_row_map = {
    0: 'Last Name',
    1: 'First Name',
    2: 'Patient DOB',
    3: 'Accession ID',
    4: 'Patient Sex',
    5: 'Patient Ethnicity',
    6: 'Indication for Testing',
    7: 'Specimen Type',
    8: 'Date Specimen Collected',
    9: 'Date Specimen Received',
    10: 'Ordering Physician'
}


def generate_patient_info_json(patient_info_file_name):
    """Given a properly formatted csv file containing the patient information,
    generate and return a JSON object representing its contents.
    """
    patient_info = {}
    with open(patient_info_file_name, 'rU') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip the header
        for i, row in enumerate(reader):
            if i < 11:
                patient_info[patient_info_row_map[i]] = row[1]
    return patient_info


def add_fields_to_cr(cr_id, patient_fields):
    """Use the Omicia API to fill in custom patient fields for a clinical report
    e.g. patient_fields: '{"Patient Name": "Eric", "Gender": "Male", "Accession Number": "1234"}'
    """
    #Construct request
    url = "{}/reports/{}/patient_fields"
    url = url.format(OMICIA_API_URL, cr_id)
    url_payload = json.dumps(patient_fields)

    sys.stdout.write("Adding custom patient fields to report...")
    sys.stdout.write("\n\n")
    sys.stdout.flush()
    result = requests.post(url, auth=auth, data=url_payload)
    return result.json()


def launch_panel_trio_report(panel_id, filter_id, reporting_cutoff, accession_id, project_id):
    """Launch a family report. Return the JSON response.
    """
    # Construct url and request
    url = "{}/reports/".format(OMICIA_API_URL)
    url_payload = {'report_type': "panel_trio",
                   'panel_id': panel_id,
                   'filter_id': filter_id,
                   'mother_genome_id': None,
                   'father_genome_id': None,
                   'proband_genome_id': None,
                   'proband_sex': None,
                   'reporting_cutoff': reporting_cutoff,
                   'accession_id': accession_id,
                   'project_id': project_id
                   }

    sys.stdout.write("Launching panel trio report...\n")
    result = requests.post(url, auth=auth, data=json.dumps(url_payload))

    return result.json()


def main():
    """Main function, creates a panel report.
    """
    parser = argparse.ArgumentParser(description='Launch a panel trio report with no genome.')
    parser.add_argument('panel_id', metavar='panel_id', type=int)
    parser.add_argument('accession_id', metavar='accession_id', type=str)
    parser.add_argument('project_id', metavar='project_id', type=str)
    parser.add_argument('--reporting_cutoff', metavar='reporting_cutoff', type=int)
    parser.add_argument('--filter_id', metavar='filter_id', type=int)
    parser.add_argument('--patient_info_file', metavar='patient_info_file', type=str)
    args = parser.parse_args()

    panel_id = args.panel_id
    filter_id = args.filter_id
    reporting_cutoff = args.reporting_cutoff
    accession_id = args.accession_id
    project_id = args.project_id
    patient_info_file_name = args.patient_info_file

    family_report_json = launch_panel_trio_report(
        panel_id, filter_id,
        reporting_cutoff,
        accession_id,
        project_id)

    # Confirm launched report data
    sys.stdout.write("\n")

    if "clinical_report" not in family_report_json.keys():
        print family_report_json
        sys.exit("Failed to launch. Check report parameters for correctness.")
    clinical_report = family_report_json['clinical_report']

    # If a patient information csv file is provided, use it to generate a
    # representative JSON object and add the patient fields to the report
    if patient_info_file_name:
        clinical_report_id = clinical_report.get('id')
        patient_info = generate_patient_info_json(patient_info_file_name)
        add_fields_to_cr(clinical_report_id, patient_info)

    sys.stdout.write('Launched Panel Trio Report:\n'
                     'id: {}\n'
                     'test_type: {}\n'
                     'accession_id: {}\n'
                     'created_on: {}\n'
                     'created_by: {}\n'
                     'status: {}\n'
                     'filter_id: {}\n'
                     'panel_id: {}\n'
                     'workspace_id: {}\n'
                     'sample_collected_date: {}\n'
                     'sample_received_date: {}\n'
                     'include_cosmic: {}\n'
                     'vaast_report_id: {}\n'
                     'mother_genome_id: {}\n'
                     'father_genome_id: {}\n'
                     'genome_id: {}\n'
                     'status: {}\n'
                     'version: {}\n'
                     .format(clinical_report.get('id', 'Missing'),
                             clinical_report.get('test_type','Missing'),
                             clinical_report.get('accession_id','Missing'),
                             clinical_report.get('created_on','Missing'),
                             clinical_report.get('created_by','Missing'),
                             clinical_report.get('status','Missing'),
                             clinical_report.get('filter_id','Missing'),
                             clinical_report.get('panel_id','Missing'),
                             clinical_report.get('workspace_id','Missing'),
                             clinical_report.get('sample_collected_date','Missing'),
                             clinical_report.get('sample_received_date','Missing'),
                             clinical_report.get('include_cosmic','Missing'),
                             clinical_report.get('vaast_report_id', 'Missing'),
                             clinical_report.get('mother_genome_id', 'Missing'),
                             clinical_report.get('father_genome_id', 'Missing'),
                             clinical_report.get('genome_id', 'Missing'),
                             clinical_report.get('status', 'Missing'),
                             clinical_report.get('version', 'Missing')))

if __name__ == "__main__":
    main()
