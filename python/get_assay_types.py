"""Get all assay_types in a workspace.
"""

import os
import requests
from requests.auth import HTTPBasicAuth
import sys

# Load environment variables for request authentication parameters
if "OMICIA_API_PASSWORD" not in os.environ:
    sys.exit("OMICIA_API_PASSWORD environment variable missing")

if "OMICIA_API_LOGIN" not in os.environ:
    sys.exit("OMICIA_API_LOGIN environment variable missing")

OMICIA_API_LOGIN = os.environ['OMICIA_API_LOGIN']
OMICIA_API_PASSWORD = os.environ['OMICIA_API_PASSWORD']
OMICIA_API_URL = os.environ.get('OMICIA_API_URL', 'https://api.omicia.com')
auth = HTTPBasicAuth(OMICIA_API_LOGIN, OMICIA_API_PASSWORD)


def get_assay_type(assay_type_id):
    """Fetch all the assay_types associated with the api user's workspace
    """

    # Construct request
    url = "{}/assay_types/{}".format(OMICIA_API_URL, assay_type_id)

    # Get request and return json object of an assay type
    result = requests.get(url, auth=auth)
    return result.json()


def get_assay_types():
    """Fetch all the assay_types associated with the api user's workspace
    """

    # Construct request
    url = "{}/assay_types".format(OMICIA_API_URL)

    # Get request and return json object of assay types
    result = requests.get(url, auth=auth)
    return result.json()


def main(argv):
    """main function, get all assay_types in a project.
    """

    if len(argv) > 1:
        sys.exit("Usage: python get_assay_types.py {optional assay_type id}")

    if len(argv) == 1:
        assay_type_id = sys.argv[1]
        assay_type = get_assay_type(assay_type_id)
        sys.stdout.write('id: {}\n'
                         'workspace_id: {}\n'
                         'description: {}\n'
                         'quality_control_fields: {}\n'
                         .format(assay_type.get('wso_id', 'Missing'),
                                 assay_type.get('workspace_id', 'Missing'),
                                 assay_type.get('description', 'Missing'),
                                 assay_type.get('quality_control_fields', 'Missing')))
    else:
        json_response = get_assay_types()
        try:
            for assay_type in json_response['objects']:
                sys.stdout.write('id: {}\n'
                                 'workspace_id: {}\n'
                                 'description: {}\n'
                                 'quality_control_fields: {}\n'
                                 .format(assay_type.get('wso_id', 'Missing'),
                                         assay_type.get('workspace_id', 'Missing'),
                                         assay_type.get('description', 'Missing'),
                                         assay_type.get('quality_control_fields', 'Missing')))
                sys.stdout.write('\n')
        except KeyError:
            if json_response['description']:
                sys.stdout.write("Error: {}\n".format(json_response['description']))
            else:
                sys.stdout.write('Something went wrong ...')

if __name__ == "__main__":
    main(sys.argv[1:])