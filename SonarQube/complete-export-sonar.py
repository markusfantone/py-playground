import csv
import requests
import datetime
import os

def get_sonarqube_data(api_url, headers):
    str_now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    base_path = 'c:/base-path-here'
    if not os.path.exists(f'{base_path}/{str_now}'):
        os.makedirs(f'{base_path}/{str_now}')

    csv_file = f'{base_path}/{str_now}/sonar_issues_{str_now}.csv'
    csv_fileRepos = f'{base_path}/{str_now}/sonar_repos_{str_now}.csv'
    csv_fileVersions = f'{base_path}/{str_now}/sonar_versions_{str_now}.csv'

    issues = []
    repos = []
    versions = []
    projectsResponse = requests.get(api_url + '/api/components/search_projects', headers=headers, params={'ps': 500, 'filter':'tags = production'})

    if projectsResponse.status_code == 200:
        projectsData = projectsResponse.json()
        project_keys = [{'key':component['key'], 'name':component["name"]} for component in projectsData['components'] 
                        if component['qualifier'] == 'TRK']

        for prj in project_keys:
            branches = []
            branchesResponse = requests.get(api_url + '/api/project_branches/list', headers=headers, params={'project': prj['key']})
            if branchesResponse.status_code == 200:
                branchesData = branchesResponse.json()
                branches = [{'name': branch['name'], 'isDefaultBranch': branch['isMain']} for branch in branchesData['branches'] 
                            if branch['name'] == 'main' or branch['name'] == 'develop']

                for branch in branches:
                    repos.append({'project': prj['name'], 'branch': branch['name'], 'isDefaultBranch': branch['isDefaultBranch']})
                    responsePrjStatus = requests.get(api_url + '/api/project_analyses/search', headers=headers, 
                                                     params={'project': prj['key'], 'branch': branch['name'], 'ps': 100, 'p': 1})
                    if responsePrjStatus.status_code == 200:
                        dataPrjStatus = responsePrjStatus.json()
                        for analysis in dataPrjStatus['analyses']:
                            if 'events' in analysis and any(event['category'] == 'VERSION' for event in analysis['events']):            
                                date = analysis['date']
                                projectVersion = analysis['projectVersion']
                                versions.append({'project': prj['name'], 
                                                 'branch': branch['name'], 
                                                 'lastVersionDate': date, 
                                                 'lastVersion': projectVersion})
                                break

                    print(f"Starting to retrieve data from SonarQube API for prj/branch: {prj['name']}/{branch['name']}")

                    responseIssues = requests.get(api_url + '/api/issues/search', 
                                                  params={'types': 'BUG,VULNERABILITY,CODE_SMELL', 
                                                          'resolved': 'false', 
                                                          'additionalFields': '_all', 
                                                          'branch':branch['name'], 
                                                          'componentKeys': prj["key"]}, headers=headers)
                    
                    if responseIssues.status_code == 200:
                        data = responseIssues.json()

                        for issue in data['issues']:
                            group = issue['component']
                            type = issue['type']
                            severity = issue['severity']
                            project = prj["name"]
                            message = issue['message']
                            issues.append({'group': group, 
                                           'type': type, 
                                           'severity': severity, 
                                           'project': project, 
                                           'message': message, 
                                           'branch': branch['name'], 
                                           'isDefaultBranch': branch['isDefaultBranch']})
                    else:
                        print(f"Failed to retrieve issues from SonarQube API for prj: {prj}")
                        print(f"Status code: {responseIssues.status_code}")
                        print(f"Response: {responseIssues.text}")

                    responseHotspots = requests.get(api_url + '/api/hotspots/search', 
                                                    params={'projectKey': prj["key"], 
                                                            'status': 'TO_REVIEW', 
                                                            'onlyMine': 'false', 
                                                            'branch': branch['name'], 
                                                            'inNewCodePeriod':'false'}, headers=headers)
                    if responseHotspots.status_code == 200:
                        dataHotspot = responseHotspots.json()
                        for hotspot in dataHotspot['hotspots']:
                            group = hotspot['component']
                            type = 'HOTSPOT'
                            severity = hotspot['vulnerabilityProbability']
                            project = prj["name"]
                            message = hotspot['message']
                            issues.append({'group': group, 
                                           'type': type, 
                                           'severity': severity, 
                                           'project': project, 
                                           'message': message, 
                                           'branch': branch['name'], 
                                           'isDefaultBranch': branch['isDefaultBranch']})
                        
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')

            writer.writerow(['Project','Branch', 'isDefaultBranch', 'Type', 'Severity',  'File', 'Message', 'Date'])

            for issue in issues:
                writer.writerow([
                    issue['project'], 
                    issue['branch'], 
                    issue['isDefaultBranch'], 
                    issue['type'], 
                    issue['severity'], 
                    issue['group'].split(':')[-1], 
                    issue['message'].replace('<', '_<_').replace('>', '_>_'), 
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                ])
        
        with open(csv_fileRepos, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['Project','Branch', 'isDefaultBranch'])
            for repo in repos:
                writer.writerow([repo['project'], repo['branch'], repo['isDefaultBranch']])

        with open(csv_fileVersions, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['Project','Branch', 'lastVersionDate', 'lastVersion'])
            for version in versions:
                writer.writerow([version['project'], version['branch'], version['lastVersionDate'], version['lastVersion']])
            
        print(f"Data exported to {csv_file}")
        print(f"Data exported to {csv_fileRepos}")
        print(f"Data exported to {csv_fileVersions}")


api_url = 'your-base-sonarqube-api-url'
headers = {'cookie': 'XSRF-TOKEN=xxx; JWT-SESSION=xxx'}
get_sonarqube_data(api_url, headers)
