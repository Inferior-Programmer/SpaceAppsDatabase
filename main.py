from flask import Flask
from flask_graphql import GraphQLView
from collections import namedtuple
from graphene import ObjectType, String, Int, Schema, Field,Boolean, List 
import random
from spaceAppsApp import TableEditor 

app = Flask(__name__)

tb = TableEditor()

class StringList(List):
    @staticmethod
    def serialize(lst):
        return lst


# Define a simple GraphQL type
class User(ObjectType):
    id = Int()
    username = String()
    password = String()
    hidePersonalInformation = List(Boolean) 
    personalInformation = String()
    success = Boolean()
class Job(ObjectType):
    id = Int()
    creatorId = Int() 
    projectName = String()
    projectDescription = String()
    projectSkills = List(String)
    finished = Boolean() 
    maxAmountOfCollaborators = Int() 
    currAmountOfCollaborators = Int()
    success = Boolean()
class CollabRequest(ObjectType):
    id = Int() 
    status = Int() 
    collaboratorId = Int()
    projectId = Int()
    success = Boolean()

    
UserValueObject = namedtuple("User", ["id", "personalInformation", "hidePersonalInformation", "username", "password", "success"])
JobValueObject = namedtuple("Job", ["id", "creatorId", "projectName", "projectDescription", "projectSkills", "finished",  "maxAmountOfCollaborators", "currAmountOfCollaborators", "success"])
CollabRequestObject = namedtuple("CollabRequest", ["id", "status", "collaboratorId", "projectId", "success"])
# Define a query for retrieving user data
class Query(ObjectType):
    login = Field(User, username=String(default_value="-1"), password=String(default_value="-1"))
    signup = Field(User, username=String(default_value="-1"), password=String(default_value="-1"), personalInformation = String(default_value="-1"))
    jobpost = Field(Job, creatorId=Int(default_value=-1),projectName=String(default_value="-1"), projectDescription=String(default_value="-1"), projectSkills = List(String)
                    , maxAmountOfCollaborators=Int(default_value=1), currAmountOfCollaborators=Int(default_value=0))
    jobedit = Field(Job, creatorId=Int(default_value=-1),projectName=String(default_value="-1"), projectDescription=String(default_value="-1"), projectSkills = List(String)
                    , maxAmountOfCollaborators=Int(default_value=1), currAmountOfCollaborators=Int(default_value=0))
    jobsearchrandom = Field(List(Job), numberOfRows = Int(default_value = 10), collaboratorId=Int(default_value=-1))
    requestcollaborator = Field(CollabRequest,collaboratorId = Int(default_value=-1) ,projectId = Int(default_value=-1))
    changecollabstatus = Field(CollabRequest,id = Int(default_value=-1) ,status = Int(default_value=-1))
    collaboratorList = Field(List(CollabRequest), projectId=Int())
    joblist = Field(List(CollabRequest), creatorId=Int())
    def resolve_login(self, info, username, password):
        data = tb.fetchTableAdvanced("UsersTable", "*", opName=['eq','eq'], eqs=["username", "password"], eqVals = [username, password])[0]
        try:
            print(data)
            return UserValueObject(id=data['id'], username=data['username'], password=data['password'], hidePersonalInformation=data['hidePersonalInformation'], personalInformation=(data['personalInformation']).join(","), success=True)
        except:
            return UserValueObject(id=-1, username="-1", password="", hidePersonalInformation=[], personalInformation="",success=False)
    def resolve_signup(self, info, username, password, personalInformation):
        data = tb.fetchTableAdvanced("UsersTable", "*", opName=['eq','eq'], eqs=["username", "password"], eqVals = [username, password])
        try:
            if(len(data)) != 0:
                return UserValueObject(id=-1, username="-1", password="", hidePersonalInformation=[], personalInformation="",success=False)
            newData = {"username": username, "password": password, "personalInformation": personalInformation.split(","), "hidePersonalInformation": [True]*len(personalInformation.split(","))}
            tb.insertData("UsersTable", newData )
            data = tb.fetchTableAdvanced("UsersTable", "*", opName=['eq','eq'], eqs=["username", "password"], eqVals = [username, password])[0]

            return UserValueObject(id=data['id'], username=data['username'], password=data['password'], hidePersonalInformation=data['hidePersonalInformation'], personalInformation=",".join(data['personalInformation']), success=True)
        except:
            return UserValueObject(id=-1, username="-1", password="", hidePersonalInformation=[], personalInformation="",success=False)
    def resolve_jobpost(self, info,creatorId,projectName, projectDescription, projectSkills, maxAmountOfCollaborators, currAmountOfCollaborators):
        try:
            data = tb.fetchTableAdvanced("JobPostings", "*", ['eq','eq'], ["projectName","creatorId"], [projectName, creatorId])
            if(len(data) != 0):
                return JobValueObject(-1, -1, "", "", [""], False, 0,0, False)
            tb.insertData("JobPostings", {'projectName': projectName, 'creatorId': creatorId, 'projectDescription': projectDescription, "collaboratorSkills": projectSkills, "maxAmountOfCollaborators": maxAmountOfCollaborators, "currAmountOfCollaborators": currAmountOfCollaborators, "finished": False})
            data = tb.fetchTableAdvanced("JobPostings", "*", ["eq", "eq"], ["projectName","creatorId"], [projectName, creatorId])[0]
            return JobValueObject(data['id'], data['creatorId'], data['projectName'], data['projectDescription'], data['collaboratorSkills'], data['finished'], data['maxAmountOfCollaborators'], data['currAmountOfCollaborators'], True)
        except: 
            return  JobValueObject(-1, -1, "", "", [""], False, 0,0, False)
        
    def resolve_jobedit(self, info,creatorId,projectName, projectDescription, projectSkills, maxAmountOfCollaborators, currAmountOfCollaborators):
        try:
            data = tb.fetchTableAdvanced("JobPostings", "*", ['eq','eq'], ["projectName","creatorId"], [projectName, creatorId])[0]
            if(len(data) == 0):
                return JobValueObject(-1, -1, "", "", [""], False, 0,0, False)
            data['projectDescription'] = projectDescription
            data['projectSkills'] = projectSkills
            data['maxAmountOfCollaborators'] = min(maxAmountOfCollaborators, data['maxAmountOfCollaborators']) 
            tb.updateData("JobPostings",data)
            return JobValueObject(data['id'], data['creatorId'], data['projectName'], data['projectDescription'], data['collaboratorSkills'], data['finished'], data['maxAmountOfCollaborators'], data['currAmountOfCollaborators'], True)
        except: 
            return  JobValueObject(-1, -1, "", "", [""], False, 0,0, False)
        
    def resolve_jobsearchrandom(self, info, numberOfRows, collaboratorId):
        try: 
            data = tb.fetchTableAdvanced("CollaboratorRequest", "projectId", ['eq','eq'],["collaboratorId", "status"], [collaboratorId, 1])
            newData = [] 
            for i in data:
                newData.append(i['projectId'])
            print(newData)
            data = tb.fetchTable("JobPostings", "*")
            random.shuffle(data)
            data = data[:min(numberOfRows, len(data))]
            newFormat = [] 
            for i in range(len(data)):
                if (data[i]['id'] in newData):
                    continue
                newFormat.append(JobValueObject(data[i]['id'], data[i]['creatorId'], data[i]['projectName'], data[i]['projectDescription'], data[i]['collaboratorSkills'], data[i]['finished'], data[i]['maxAmountOfCollaborators'], data[i]['currAmountOfCollaborators'], True))
            return newFormat
        except: 
            return []
    def resolve_requestcollaborator(self, info, collaboratorId, projectId):
        try: 
            data = {'collaboratorId': collaboratorId, 'projectId': projectId, 'status': 1, }
            tb.insertData("CollaboratorRequest", data)
            data = tb.fetchTableAdvanced("CollaboratorRequest", "*", ["eq", "eq"], ["projectId", "collaboratorId"], [projectId, collaboratorId])[0]
            return CollabRequestObject(data['id'],data['status'], data['collaboratorId'], data['projectId'], True)
        except:
            return CollabRequestObject(-1, -1, -1, -1, False)
    def resolve_changecollabstatus(self, info, id, status):
        try: 
            data = tb.fetchTableAdvanced("CollaboratorRequest", "*", ["eq"], ["id"], [id])[0]
            if(status == 2):
                jobPostingsData = tb.fetchTable("JobPostings", "*", 'id', data['projectId'])[0]
                if(jobPostingsData['maxAmountOfCollaborators'] <= jobPostingsData['currAmountOfCollaborators']):
                    
                    return CollabRequestObject(-1, -1, -1, -1, False)
                else:
                    jobPostingsData['currAmountOfCollaborators'] += 1
                    print(jobPostingsData)
                    tb.updateData("JobPostings", {'id': jobPostingsData['id'],'projectName': jobPostingsData['projectName'], 'creatorId': jobPostingsData['creatorId'], 'projectDescription': jobPostingsData['projectDescription'], "collaboratorSkills": jobPostingsData['collaboratorSkills'], "maxAmountOfCollaborators": jobPostingsData['maxAmountOfCollaborators'], "currAmountOfCollaborators": jobPostingsData['currAmountOfCollaborators'], "finished": False})
                    print(jobPostingsData)
            print("Lmao2")
            data['status'] = status
            tb.updateData("CollaboratorRequest", {'id': data['id'],'status': data['status'], 'collaboratorId': data['collaboratorId'], 'projectId': data['projectId']}) 
            return CollabRequestObject(data['id'],data['status'], data['collaboratorId'], data['projectId'], True)
        except:
            return CollabRequestObject(-1, -1, -1, -1, False)
        
    def resolve_collaboratorList(self, info, projectId):
        try: 
            data = tb.fetchTableAdvanced("CollaboratorRequest", "*", ["eq"], ["projectId"], [projectId])
            return data
        except:
            return []
    def resolve_joblist(self, info, creatorId):
        try: 
            data = tb.fetchTableAdvanced("JobPostings", "*", ["eq"], ["creatorId"], [creatorId])
            return data
        except:
            return []



    #data = tb.detchTableAdvanced("JobPostings", "*", opName=["ilike", "ilike", "ilike"], eqs=["projectName","projectDescription", "projectSkills"])[0]


# Create a GraphQL schema
schema = Schema(query=Query)

# Add a GraphQL view to your Flask app
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == '__main__':
    app.run(debug=True)