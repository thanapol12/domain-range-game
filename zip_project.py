import os
import zipfile

def zip_project(output_filename='game.zip'):
    """Packages all project files into a zip file for easy upload to Google Colab."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(project_dir, output_filename)
    
    # Files to include in the zip
    files_to_zip = [
        'app.py',
        'face_processor.py',
        'questions.py',
        'templates/index.html',
        'static/style.css',
        'static/game.js',
        'app.yaml',
        'requirements.txt',
        'run_on_colab.ipynb'
    ]
    
    print("Packaging files into game.zip...")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_rel in files_to_zip:
                file_abs = os.path.join(project_dir, file_rel)
                if os.path.exists(file_abs):
                    # Write file into zip with relative path
                    zip_file.write(file_abs, arcname=file_rel)
                    print(f"  Added: {file_rel}")
                else:
                    # Try folders
                    if file_rel.endswith('/') or not os.path.isfile(file_abs):
                        # It is a folder, walk it
                        for root, _, filenames in os.walk(file_abs):
                            for filename in filenames:
                                filePath = os.path.join(root, filename)
                                relPath = os.path.relpath(filePath, project_dir)
                                zip_file.write(filePath, arcname=relPath)
                                print(f"  Added: {relPath}")
            
        print(f"Success! game.zip created at {zip_path}")
        return True
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

if __name__ == '__main__':
    zip_project()
