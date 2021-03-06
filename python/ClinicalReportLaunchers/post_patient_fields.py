"""Populate a report's custom fields.
Usage: post_patient_fields.py 2029 '{"Patient Name": "Eric", "Gender": "Male", "Accession Number": "1234"}'
"""

import os
import requests
from requests.auth import HTTPBasicAuth
import sys
import json
import argparse

# Load environment variables for request authentication parameters
if "OMICIA_API_PASSWORD" not in os.environ:
    sys.exit("OMICIA_API_PASSWORD environment variable missing")

if "OMICIA_API_LOGIN" not in os.environ:
    sys.exit("OMICIA_API_LOGIN environment variable missing")

OMICIA_API_LOGIN = os.environ['OMICIA_API_LOGIN']
OMICIA_API_PASSWORD = os.environ['OMICIA_API_PASSWORD']
OMICIA_API_URL = os.environ.get('OMICIA_API_URL', 'https://api.omicia.com')
auth = HTTPBasicAuth(OMICIA_API_LOGIN, OMICIA_API_PASSWORD)


def add_fields_to_cr(cr_id, patient_fields):
    """Use the Omicia API to fill in custom patient fields for a clinical report
    """
    # Construct request
    url = "{}/reports/{}/patient_fields"
    url = url.format(OMICIA_API_URL, cr_id)
    url_payload = patient_fields

    sys.stdout.write("Adding custom patient fields to report...")
    sys.stdout.write("\n\n")
    sys.stdout.flush()
    result = requests.post(url, auth=auth, data=url_payload, verify=False)
    return result.json()


def main():
    """main function. Upload a specified VCF file to a specified project.
    """
    parser = argparse.ArgumentParser(description='Fill patient info fields for existing clinical reports.')
    parser.add_argument('c', metavar='clinical_report_id', type=int)
    parser.add_argument('f', metavar='patient_fields', type=str)
    args = parser.parse_args()

    cr_id = args.c
    patient_fields = args.f

    json_response = add_fields_to_cr(cr_id, patient_fields)
    sys.stdout.write(json.dumps(json_response, indent=4))

if __name__ == "__main__":
    main()
