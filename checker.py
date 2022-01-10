import json
import pandas as pd
import parser_code

global licenseMatrix
class Node:
    def __init__(self, package,license,uyum):
        self.children = []
        self.package = package
        self.license = license
        self.uyumlu = uyum

def RecursiveChecker(dependencies,node,parentlicense):
    lenDependencies = len(list(dependencies.keys()))
    for i in range(lenDependencies):
        package = list(dependencies.keys())[i]
        restDependencies = dependencies[package]
        license = restDependencies["license"]
        uyumlu = IsLicenseConsistent(parentlicense,license)
        node.children.insert(i,Node(package,license,uyumlu))
        try :
            RecursiveChecker( restDependencies["dependencies"],node.children[i],license)
        except:
            continue
    return
       
    
    
def IsLicenseConsistent(parent,child):
    row = -1
    column = -1
    for i in range(len(licenseMatrix.columns)):
        if(licenseMatrix.columns[i].lower() == child.lower()):
            row = i
    if row == -1 :
        return "?"
    for i in range(len(licenseMatrix.columns)):
        if(licenseMatrix.columns[i].lower() == parent.lower()):
            column = i
    if column == -1 :
        return "?"
    return licenseMatrix[licenseMatrix.columns[column]][row]



def RecursiveJson(nodeTree):
    JsonPackage ={}
    JsonPackage = {
        "name":nodeTree.package,
        "attributes":{
            "license": nodeTree.license,
            "color" : nodeTree.uyumlu
        }
    }
    children =[]
    for i in range(len(nodeTree.children)): 
        children.append(RecursiveJson(nodeTree.children[i]))
    if 0 != len(children):
        JsonPackage["children"] = children
    return JsonPackage

def stringInconsistencies(jsonOutput):
    inconsistencies =[]
    RecursiveVersion(jsonOutput,jsonOutput["name"],inconsistencies)
    return inconsistencies
    
    
def RecursiveVersion(jsonOutput,parentPackage,inconsistencies): 
    if "children" in jsonOutput:
        rest = jsonOutput["children"]
    else :
        return
    for i in range(len(rest)):
        if( (rest[i]["attributes"]["color"]) == "n" ):
            str = rest[i]["name"] + " is inconsistent with " + parentPackage + "!"
            inconsistencies.append(str)
        
        if "children" in rest[i]:
            RecursiveVersion(rest[i],rest[i]["name"],inconsistencies)
    return

      

def ILC( url,devDependency):
    global licenseMatrix
    licenseMatrix = pd.read_csv("licenseInconsistency.csv")
    parser = parser_code.Parser(url,devDependency)
    parserResult = parser.parse()
    root = Node("base","base","base")
    RecursiveChecker(parserResult,root,parserResult[list(parserResult.keys())[0]]["license"])
    jsonOutput = RecursiveJson(root.children[0])
    return jsonOutput

    