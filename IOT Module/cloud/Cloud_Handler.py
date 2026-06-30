import cloudinary
import cloudinary.uploader
class Cloud_Handler:
    def __init__(self):
        cloudinary.config( 
          cloud_name = "dsu4nnsrd", 
          api_key = "284865597693164", 
          api_secret = "1o8AxBWSvIJCv4F9gIz3v67HTuw",
          secure = True
        )

    def upload_frame(self, local_path):

        response = cloudinary.uploader.upload(local_path, folder="Early_Autism_Detection")
        return response['secure_url']
        return None