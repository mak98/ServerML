from prediction import predict_image
import torch
import os
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class Models:
    """
    Model Handler for server. 
    Input: Takes path of the directory where models will be stored.
    """
    def __init__(self,path):
        self.models={}
        self.path=path
        for a in list(os.listdir(path)):#Load all models already uploaded.
            self.models[a]=torch.load(path+a,map_location=device)
    def getModel(self):
        return list(self.models.keys())
    def loadModel(self,mname,mpath):
        self.models[mname]=torch.load(mpath,map_location=device)
    def predict(self,mName,data):
        return predict_image(self.models[mName],data)#called from predictions.py
    def DropModel(self,mname):
        del self.models[mname]
        os.remove(self.path+mname)