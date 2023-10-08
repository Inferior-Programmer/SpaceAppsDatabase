from supabase import create_client, Client


url = "https://dqkskqmmfrbthhuiiypm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxa3NrcW1tZnJidGhodWlpeXBtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NjYxMzQxMiwiZXhwIjoyMDEyMTg5NDEyfQ.hwunPB7CHVP_ujSIpXbeOPjr5-FqKanXw8uPAic-Jy4"




class TableEditor:

    def __init__(self):
        url = "https://dqkskqmmfrbthhuiiypm.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxa3NrcW1tZnJidGhodWlpeXBtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NjYxMzQxMiwiZXhwIjoyMDEyMTg5NDEyfQ.hwunPB7CHVP_ujSIpXbeOPjr5-FqKanXw8uPAic-Jy4"
        self.supabase = create_client(url, key)

    def fetchTable(self,tableName, select, eq = None, eqVal = None):
        response = self.supabase.table(tableName).select(select)
        if eq is not None and eqVal is not None:
            response = response.eq(eq, eqVal)
        
        response = response.execute()
        return response.data
    def fetchTableAdvanced(self, tableName, select, opName = None, eqs = None, eqVals = None):
        response = self.supabase.table(tableName).select(select)
        print(opName, eqs, eqVals)
        if eqs is not None and eqVals is not None and opName is not None:
            assert len(opName) == len(eqs)
            assert len(eqs) == len(eqVals)
            for i in range(len(eqVals)):
                if(eqVals[i] == None):
                    response = getattr(response, opName[i])(eqs[i])
                else:
                    response = getattr(response, opName[i])(eqs[i], eqVals[i])
        response = response.execute() 
        return response.data


    def insertData(self, tableName, data):
        data = self.supabase.table(tableName).insert(data).execute()
        return data.data
    def updateData(self, tableName, data):
        data = self.supabase.table(tableName).upsert(data).execute()
        return data.data
    def insertNewUser(self, users, isCollaborator, personalInformation):
        data = self.insertData( "UsersTable", {"id": users, "hidePersonalInformation":[False, False,False, False,False], 'personalInformation': personalInformation})
        return 1
    
    def updateUserInformation(self, users, hiddenInformation, information):
        diict = {"id": users, "hidePersonalInformation": hiddenInformation, "personalInformation": information}
        self.updateData("UsersTable", diict)
        return 1

    def addJobPosting(self,creatorId, collaboratorSkills, projectDescription, currAmountOfCollaborators, maxAmountOfCollaborators):
        diict = {"creatorId": creatorId, "collaboratorSkills": collaboratorSkills, "projectDescription": projectDescription, "currAmountOfCollaborators": currAmountOfCollaborators, "maxAmountOfCollaborators": maxAmountOfCollaborators, "finished": False}
        self.insertData("JobPostings", diict)
        return 1 

    
    def updatePending(self, ids, collaboratorId, status):
        try:
            mahData = tb.fetchTableAdvanced("CollaboratorRequest", "*", ["eq", "gt"], ["projectId", "collaboratorId"], [1,-2])
            if  (len(mahData) == 0 and mahData[0]['status'] != 1 ): 
                return -1
            mahData = mahData[0]
            mahData['projectId'] = ids 
            mahData['collaboratorId'] = collaboratorId
            mahData['status'] = status 
            print(mahData)
            self.updateData("CollaboratorRequest", mahData)
            return 1
        except: 
            return -1
        

        


    def finishProject(self, ids):
        try:
            mahData = self.fetchTable("JobPostings", "*", eq = "id", eqVal = ids)[0] 
            mahData["finished"] = True
            self.updateData("JobPostings", mahData)
        except:
            return -1
    
        

if __name__ == '__main__':
    tb = TableEditor()
    #tb.updateUserInformation(-1, [True, True, True, False, False], ["Localized", "Weather", "Systems", "Org", "No"])
    #tb.addJobPosting(-1, ["Neal Neal"], "elmaw", 0, 5)
    tb.updatePending(1, -1,2)
    
