import os
import re

class ResponseFilesParser:
    def __init__(self, project_dir, chosen_files):
        self.project_dir = project_dir
        self.chosen_files = chosen_files

    def parse_response_and_update_files_on_disk(self, response):
        """
        Parses the response to find modified files and updates them on disk.
        Assumes file contents in the response are provided within code blocks.
        """
        print("Parsing response to update files...")
        
        # Extract the filenames from the response
        filenames_in_response = self.extract_filenames_from_response(response)

        if not filenames_in_response:
            print("No filenames found in the response. Skipping update.")
            return

        # Iterate over the filenames and extract corresponding content from the response
        for relative_path in filenames_in_response:
            # Extract the content for each file from the response
            file_content = self.extract_content_for_file(response, relative_path)

            if file_content:
                # Replace the [BACKTICK] marker with actual backticks
                file_content = file_content.replace("[BACKTICK]", "`")
                
                # Update the file on disk with the new content
                self.update_file_on_disk(relative_path, file_content)

    def extract_filenames_from_response(self, response):
        """
        Tries to extract filenames from the response. Assumes filenames are listed in the response,
        and they match the filenames in the chosen_files list.
        """
        extracted_files = []
        
        # We'll check if the filenames in chosen_files appear in the response, possibly wrapped in **
        for relative_path in self.chosen_files:
            # Escape the file path to handle special regex characters and allow for ** wrapping
            pattern = rf"\*\*{re.escape(relative_path)}\*\*"
            if re.search(pattern, response):
                extracted_files.append(relative_path)
        
        return extracted_files

    def extract_content_for_file(self, response, relative_path):
        """
        Extracts the new content for a given file from the response text.
        Assumes the content for each file is enclosed within triple backticks (```) after the filename,
        which can be wrapped in **.
        """
        # Try to find the file name enclosed in ** in the response
        file_marker = f"**{relative_path}**"

        start_index = response.find(file_marker)
        if start_index == -1:
            print(f"Could not find the file marker for: {relative_path}")
            return None

        # After finding the file marker, look for the content inside the next triple backticks
        start_content_index = response.find("```", start_index)
        if start_content_index == -1:
            print(f"Could not find the start of the content block for file: {relative_path}")
            return None

        # Find the closing triple backticks after the start_content_index
        end_content_index = response.find("```", start_content_index + 3)
        if end_content_index == -1:
            print(f"Could not find the end of the content block for file: {relative_path}")
            return None

        # Extract the content between the triple backticks
        file_content = response[start_content_index + 3:end_content_index].strip()

        return file_content

    def update_file_on_disk(self, relative_path, new_content):
        """
        Updates the file on disk with the new content.
        """
        try:
            file_path = os.path.join(self.project_dir, relative_path)
            with open(file_path, 'w') as file:
                file.write(new_content)
            print(f"File updated: {file_path}")
        except Exception as e:
            print(f"Error updating file {file_path}: {str(e)}")
