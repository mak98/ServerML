from prediction import predict_image
import torch
import os
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class Models:
    def __init__(self,path):
        self.models={}
        self.path=path
        for a in list(os.listdir(path)):
            self.models[a]=torch.load(path+a,map_location=device)
    def getModel(self):
        return list(self.models.keys())
    def loadModel(self,mname,mpath):
        self.models[mname]=torch.load(mpath,map_location=device)
    def predict(self,mName,data):
        return predict_image(self.models[mName],data)
    def DropModel(self,mname):
        del self.models[mname]
        os.remove(self.path+mname)