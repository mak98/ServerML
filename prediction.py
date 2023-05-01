import torch
from torchvision import transforms, models
from torch.autograd import Variable
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

test_transforms = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
])

def predict_image(model, image):
    image_tensor = test_transforms(image).float()
    image_tensor = image_tensor.unsqueeze_(0)
    input = Variable(image_tensor)
    input = input.to(device)
    output = model(input)
    index = int(output.data.cpu().numpy().argmax())
    print(9)
    return index,output.data.cpu().tolist()

# model = torch.load('static/uploads/resnet.pt',map_location=device)
# model.eval()

# img_path = 
# print(predict_image(model, img_path))