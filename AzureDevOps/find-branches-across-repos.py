import requests

def search_branches(branch_name):
    # Replace with your Azure DevOps organization URL
    organization_url = "your-organization-url"

    # Replace with your Azure DevOps project name
    project_name = "your-project-name"

    # Replace with your Azure DevOps personal access token
    personal_access_token = "your-personal-access-token"

    # Construct the API endpoint URLs
    repos_url = f"{organization_url}/{project_name}/_apis/git/repositories?api-version=6.0"
    branches_url = f"{organization_url}/{project_name}/_apis/git/repositories/_repositoryId_/refs?filterContains={branch_name}&api-version=6.0"

    # Make the initial request to get all repositories
    response = requests.get(repos_url, auth=("", personal_access_token))
    response.raise_for_status()
    repositories = response.json()["value"]

    # Iterate over each repository and search for branches with the given name
    for repository in repositories:
        repository_id = repository["id"]
        repository_name = repository["name"]

        # Make the request to search for branches in the current repository
        try:
            response = requests.get(branches_url.replace("_repositoryId_", repository_id), auth=("", personal_access_token))
            response.raise_for_status()
            branches = response.json()["value"]
        
            # Print the branches found in the current repository
            for branch in branches:
                branch_name = branch["name"]
                print(f"{repository_name} | {branch_name}")
        except:
            pass

# Call the function with the branch name you want to search for
branch_name = input("Enter the branch name you want to search for: ")
search_branches(branch_name)