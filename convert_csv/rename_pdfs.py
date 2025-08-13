import os

folder_path = r'C:\Users\Kwong-Yu Wong\Desktop\ra_code_try\pdfs'

def rename_pdfs(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".PDF"):
            new_name = filename[:-4] + ".pdf"
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))

if __name__ == "__main__":
    rename_pdfs(folder_path)