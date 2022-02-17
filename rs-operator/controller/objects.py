class FluxConfig:

    def __init__(self, api_response):
        print(api_response["spec"]["applicationIdentifier"])
        print(api_response["spec"]["environmentIdentifier"])
        print(api_response["spec"]["vpcId"])

        self.name = api_response["metadata"]["name"]
        self.namespace = api_response["metadata"]["namespace"]
        self.environmentIdentifier=api_response["spec"]["environmentIdentifier"]
        self.applicationIdentifier=api_response["spec"]["applicationIdentifier"]
        self.vpcId=api_response["spec"]["vpcId"]

    def get_envId(self):
        return self.environmentIdentifier
        
    def get_appId(self):
        return self.applicationIdentifier    
    
    def get_vpcId(self):
        return self.vpcId

    def get_name(self):
        return self.namespace

    def get_namespace(self):
        return self.name
    
    def prittyPrint(self):
        print("RefactorSpaceConfig:"
             "\n\t name:"+self.name + 
             "\n\t namespace:"+self.namespace +
             "\n\t environmentIdentifier:"+self.environmentIdentifier +
             "\n\t applicationIdentifier:"+self.applicationIdentifier +
             "\n\t vpcId:"+self.vpcId+"\n")