import csv
import requests

def get_sonarqube_data(api_url, params, headers):
    response = requests.get(api_url + '/api/issues/search', params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()

        project_names = [component['name'] for component in data['components'] if component['qualifier'] == 'TRK']
        print(f"Project names: {project_names}")

        issues = []
        for issue in data['issues']:
            group = issue['component']
            type = issue['type']
            severity = issue['severity']
            project = issue['project']
            issues.append({'group': group, 'type': type, 'severity': severity, 'project': project})

        csv_file = 'c:/base-path-here/sonar_data.csv'

        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['Project','Type', 'Severity',  'File'])

            for issue in issues:
                writer.writerow([issue['project'].split('_')[1], issue['type'], issue['severity'], issue['group'].split(':')[1]])
            
        print(f"Data exported to {csv_file}")
            
    else:
        print("Failed to retrieve data from SonarQube API")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

api_url = 'your-base-sonarqube-api-url'  # Add your SonarQube URL here
params = {'types': 'BUG,VULNERABILITY', 'resolved': 'false', 'additionalFields': '_all'}
headers = {'cookie': 'XSRF-TOKEN=xxx; JWT-SESSION=xxx'}

get_sonarqube_data(api_url, params, headers)