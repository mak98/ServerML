import requests

url = "http://localhost:8000/predict/resnet.pt"#endpoint for model
#Sample image path
image_file = open("/home/mayank/ASU/egr598 cav/dataset/val/Toyota Prius/18.jpg", "rb")

# set the file data
file_data = {"image": image_file}

response = requests.post(url, files={"file": image_file})

# print the response
print(response.json())