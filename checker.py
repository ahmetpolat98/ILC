import json
import pandas as pd
import parser_code

licenseMatrix = ""

class Node:
    def __init__(self, package,license,uyum):
        self.children = []
        self.package = package
        self.license = license
        self.uyumlu = uyum
    def __print__(self):
        print(self.package,":",self.license)

def RecursiveChecker(dependencies,node,parentlicense):
    lenDependencies = len(list(dependencies.keys()))
    for i in range(lenDependencies):
        package = list(dependencies.keys())[i]
        restDependencies = dependencies[package]
        license = restDependencies["license"]
        uyumlu = IsLicenseConsistent(parentlicense,license) 
        node.children.insert(i,Node(package,license,uyumlu))
        RecursiveChecker( restDependencies["dependencies"],node.children[i],license)
    return
       
    
    
def IsLicenseConsistent(parent,child):
    row = -1
    column = -1
    for i in range(len(licenseMatrix.columns)):
        if(licenseMatrix.columns[i].lower() == child.lower()):
            row = i
    if row == -1 :
        return '?'
    for i in range(len(licenseMatrix.columns)):
        if(licenseMatrix.columns[i].lower() == parent.lower()):
            column = i
    if column == -1 :
        return '?'
    return licenseMatrix[licenseMatrix.columns[column]][row]



def RecursiveJson(a):
    x ={}
    x = {
        "name":a.package,
        "attributes":{
            "license": a.license,
            "color" : a.uyumlu
        }
    }
    y =[]
    for i in range(len(a.children)): 
        y.append(RecursiveJson(a.children[i]))
    if 0 != len(y):
        x['children'] = y
    return x

def ILC( url,devDependency=False):
    global licenseMatrix
    licenseMatrix = pd.read_csv('licenseInconsistency.csv')
    parser = parser_code.Parser(url,devDependency)
    parserResult = parser.parse()
    root = Node("base","base","base")
    print( parserResult[list(parserResult.keys())[0]]['license'] )
    RecursiveChecker(parserResult,root,parserResult[list(parserResult.keys())[0]]['license'])
    jsonOutput = RecursiveJson(root.children[0])
    return jsonOutput
    
# ILC("https://github.com/aws/aws-sdk-js",False)
    
    