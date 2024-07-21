import os

project_directory = os.path.dirname(os.path.abspath(__file__))

# Build the export path relative to the project directory
export_path = os.path.join(project_directory, 'src', 'storage', 'export')

print(export_path)