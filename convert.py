import base64
with open("image_272151.jpg", "rb") as image_file:
    print(base64.b64encode(image_file.read()).decode('utf-8'))