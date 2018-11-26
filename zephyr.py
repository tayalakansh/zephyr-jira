import json
import jwt
import time
import hashlib
import requests


def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


# USER
USER = 'admin'

# ACCESS KEY from navigation >> Tests >> API Keys
ACCESS_KEY = ''

# ACCESS KEY from navigation >> Tests >> API Keys
SECRET_KEY = ''

# JWT EXPIRE how long token been to be active? 3600 == 1 hour
JWT_EXPIRE = 3600

# BASE URL for Zephyr for Jira Cloud
BASE_URL = 'https://prod-api.zephyr4jiracloud.com/connect'

# CYCLE NAME FROM ZEPHYR
CYCLE_NAME = "API_REGRESSION"

PROJECT_ID = 10000

VERSION_ID = 10000


def post_result():

    # RELATIVE PATH for token generation and make request to api
    RELATIVE_PATH = '/public/rest/api/1.0/cycles/search?versionId={}&projectId={}'.format(VERSION_ID, PROJECT_ID)

    # CANONICAL PATH (Http Method & Relative Path & Query String)

    CANONICAL_PATH = 'GET&/public/rest/api/1.0/cycles/search&'+'projectId='+str(PROJECT_ID)+'&versionId=' + str(VERSION_ID)

    # TOKEN HEADER: to generate jwt token
    payload_token = {
                'sub': USER,
                'qsh': hashlib.sha256(CANONICAL_PATH.encode('utf-8')).hexdigest(),
                'iss': ACCESS_KEY,
                'exp': int(time.time())+JWT_EXPIRE,
                'iat': int(time.time())
            }

    # GENERATE TOKEN
    token = jwt.encode(payload_token, SECRET_KEY, algorithm='HS256').strip().decode('utf-8')

    # REQUEST HEADER: to authenticate and authorize api
    headers = {
                'Authorization': 'JWT '+token,
                'Content-Type': 'text/plain',
                'zapiAccessKey': ACCESS_KEY
            }

    # FIND CYCLE ID
    raw_result = requests.get(BASE_URL + RELATIVE_PATH, headers=headers)

    if is_json(raw_result.text):

        # JSON RESPONSE: convert response to JSON
        json_result = json.loads(raw_result.text)

        for json_val in json_result:
          if json_val['name'] == CYCLE_NAME:
              cycle_id = json_val['id']

    else:
        print(raw_result.text)

    # GET LIST OF ALL TESTS IN A CYCLE

    RELATIVE_PATH = '/public/rest/api/1.0/executions/search/cycle/{}?versionId={}&projectId={}'.format(cycle_id, VERSION_ID, PROJECT_ID)

    CANONICAL_PATH = 'GET&/public/rest/api/1.0/executions/search/cycle/'+cycle_id+'&'+'projectId='+str(PROJECT_ID)+'&versionId=' + str(VERSION_ID)

    # TOKEN HEADER: to generate jwt token
    payload_token2 = {
                'sub': USER,
                'qsh': hashlib.sha256(CANONICAL_PATH.encode('utf-8')).hexdigest(),
                'iss': ACCESS_KEY,
                'exp': int(time.time())+JWT_EXPIRE,
                'iat': int(time.time())
            }

    # GENERATE TOKEN
    token2 = jwt.encode(payload_token2, SECRET_KEY, algorithm='HS256').strip().decode('utf-8')

    # REQUEST HEADER: to authenticate and authorize api
    headers2 = {
                'Authorization': 'JWT '+token2,
                'Content-Type': 'text/plain',
                'zapiAccessKey': ACCESS_KEY
            }
    result2 = requests.get(BASE_URL + RELATIVE_PATH, headers=headers2)

    test_details = {}
    test_cases_available = []
    if is_json(result2.text):
        # JSON RESPONSE: convert response to JSON
        json_result2 = json.loads(result2.text)
        for json_val in json_result2['searchObjectList']:
            test_details['issueId'] = json_val['execution']['issueId']
            test_details['executionId'] = json_val['execution']['id']
            test_cases_available.append(test_details.copy())
            # PRINT RESPONSE: pretty print with 4 indent
    else:
        print(result2.text)

    # PICKING UP EXECUTION ID AND ISSUE ID OF ANY ONE TEST
    execution_id = test_cases_available[0]['executionId']
    issue_id = test_cases_available[0]['issueId']

    # UPDATE TEST RESULT
    RELATIVE_PATH = '/public/rest/api/1.0/execution/{}?issueId={}&projectId=10000'.format(execution_id, issue_id)

    CANONICAL_PATH = 'PUT&/public/rest/api/1.0/execution/' + execution_id + '&' + 'issueId=' + str(issue_id) + '&projectId=' + str(PROJECT_ID)

    # TOKEN HEADER: to generate jwt token
    payload_token2 = {
                'sub': USER,
                'qsh': hashlib.sha256(CANONICAL_PATH.encode('utf-8')).hexdigest(),
                'iss': ACCESS_KEY,
                'exp': int(time.time())+JWT_EXPIRE,
                'iat': int(time.time())
            }

    # GENERATE TOKEN
    token2 = jwt.encode(payload_token2, SECRET_KEY, algorithm='HS256').strip().decode('utf-8')

    # REQUEST HEADER: to authenticate and authorize api
    headers2 = {
                'Authorization': 'JWT '+token2,
                'Content-Type': 'application/json',
                'zapiAccessKey': ACCESS_KEY
            }
    payload = {
      "cycleId": cycle_id,
      "id": execution_id,
      "issueId": issue_id,
      "projectId": PROJECT_ID,
      "status": {
        "id": "1"
      },
      "versionId": VERSION_ID
    }
    result2 = requests.put(BASE_URL + RELATIVE_PATH, headers=headers2, json=payload)
    print result2
    print result2.text


if __name__ == "__main__":
    post_result()
