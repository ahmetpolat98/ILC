import requests
import json
import base64
import re

#INFO : GitHub api has request rate limitations (per repo, per hour) 

username = ""
token = ""

class Parser:
    def __init__(self,URL,dev_dep = False):
        global username, token
        username, token = self.__get_token()
        self.URL = URL
        self.dev_dep = dev_dep
        self.api_url = self.__get_api_url()
                
    def __get_api_url(self):
        owner = self.URL.split("/")[3]
        repo = self.URL.split("/")[4]
        return "https://api.github.com/repos/"+owner+"/"+repo
    
    def __get_license(self):
        global username, token
        response = requests.get(self.api_url+"/license",auth=(username,token))
        if response.status_code == 200:
            return str(response.json()["license"]["key"])
        else:
            #print("License information cannot found.")
            return "ERROR"
    
    def parse(self):
        json = {}
        dict_ = get_dependencies(self.api_url,self.dev_dep)
        json[self.URL.split("/")[4]] = {"license" : get_license(self.api_url), "dependencies" : dict_}
        return json
    
    def __get_token(self):
        global username, token
        file = open("token.txt","r")
        user_ = file.readline()
        user_ = user_.split("=")[1][:-1]
        token_ = file.readline()
        token_ = token_.split("=")[1]
        file.close()
        return user_ , token_,  
    
def get_api_url(URL):
    owner = URL.split("/")[3]
    repo = URL.split("/")[4]
    return "https://api.github.com/repos/"+owner+"/"+repo 
    
def get_license(api_url):
    global username, token
    #print(api_url)
    response = requests.get(api_url+"/license",auth=(username,token))
    #print(response.status_code)
    if response.status_code == 200:
        return str(response.json()["license"]["key"])
    else:
        print("License information cannot found.")
        return "ERROR"

def get_languages(api_url):
    global username, token
    response = requests.get(api_url + "/languages",auth=(username,token)).json()
    return list(response.keys())
    


def get_repo_from_npm(URL):
    response = requests.get(URL)
    repo_html = (re.findall('aria-labelledby="repository".*target="_blank" rel="noopener noreferrer nofollow">',response.text))[0]
    repo_html = re.findall('href=".*" target', repo_html)[0]
    return (repo_html[6:-8])

def get_repo_from_pip(URL):
    response = requests.get(URL).json()
    list_ = list(response["info"]["project_urls"].values())
    repo_url = [url for url in list_ if "https://github.com" in url]
    if repo_url:
        owner = repo_url[0].split('/')[3]
        repo = repo_url[0].split('/')[4]
        returned = "https://github.com/" + owner + "/" + repo
        return returned # Assumed that all github urls are repo_urls and its variants.
    else:
        raise Exception("ERROR: GITHUB REPO CANNOT FOUND")
        #print("ERROR: GITHUB REPO CANNOT FOUND")
        return "ERROR: GITHUB REPO CANNOT FOUND"


def get_dependencies(api_url,dev_dep=False):
    global username, token
    languages = get_languages(api_url)
    for language in languages:
        if language == "JavaScript": 
            npm_url = "https://www.npmjs.com/package/" # JS only
            response = requests.get(api_url + "/contents/package.json",auth=(username,token)) # for JS projects only
        elif language == "Python":
            pip_url = "https://pypi.org/pypi/" # PYTHON only
            response = requests.get(api_url + "/contents/requirements.txt",auth=(username,token)) # for PYTHON projects only
        else:
            print("WARNING: UNSUPPORTED LANGUAGE: " + language)
            continue
        
        #print(response.status_code)
        if response.status_code == 200:
            dependency_dict = (base64.decodebytes(bytearray(response.json()["content"], 'utf-8')).decode('utf-8'))
            try:
                if language == "JavaScript":
                    temp_dict = json.loads(dependency_dict)["dependencies"]
                    if dev_dep:
                        temp_dict.update(json.loads(dependency_dict)["devDependencies"])
                    dependency_dict = temp_dict
                elif language == "Python":
                    temp = dependency_dict
                    dependency_dict = {}
                    for line in temp.splitlines():
                        line = line.split("=")
                        if line[0][-1] == ">":
                            dependency_dict[line[0][:-1]] = line[-1]
                        else:
                            dependency_dict[line[0]] = line[-1]
            except:
                dependency_dict = {}
            for package in dependency_dict.keys():
                    try:
                        print("Package : " + package)
                        if language == "JavaScript":
                            URL = npm_url + package
                            repo_url = get_repo_from_npm(URL)
                        elif language == "Python": #Actually only option is Python
                            URL = pip_url + package + "/json"
                            repo_url = get_repo_from_pip(URL)
                        api_url = get_api_url(repo_url)
                        dict_ = {}
                        dict_["license"] = get_license(api_url) # Can be 'other'
                        dict_["dependencies"] = get_dependencies(api_url,False) # dev_dep of dev_dep is not checked
                        dependency_dict[package] = dict_
                    except Exception as E:
                        print("Exception: ")
                        print(E)
                        dict_ = {"license": "ERROR", "dependencies" : "ERROR"}
                        dependency_dict[package] = dict_
                        continue
        else:
            dependency_dict = {"ERROR": "ERROR"}
            #print("Dependencies cannot found.")
            
    try:
        #print(dependency_dict)
        return dependency_dict
    except:
        return {}

# URL = "https://github.com/aws/aws-sdk-js" # example, normally it is given from web-app
#URL = "https://github.com/Haytaf17/haytaf17database"
#URL = "https://github.com/aydinbugra/Nutbarn"
#URL = "https://github.com/aydinbugra/test"
# parser = Parser(URL,False)
# print(parser.parse()) # License Checker can use this function to get all dependincies and their license info


# For not found case
#URL = "https://github.com/aydinbugra/Nutbarn"
#URL = "https://github.com/Haytaf17/haytaf17database"
#print(parse(URL))
