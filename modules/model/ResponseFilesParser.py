import os
from modules.model.FileSyntaxCorrector import FileSyntaxCorrector  # Import the FileSyntaxCorrector

class ResponseFilesParser:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.syntax_corrector = FileSyntaxCorrector()  # Instantiate the FileSyntaxCorrector

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
                # Fix the file content after decoding using the FileSyntaxCorrector
                file_content = self.syntax_corrector.fix_after_decoding(file_content)

                # Update the file on disk with the new content
                self.update_file_on_disk(relative_path, file_content)

    def extract_filenames_from_response(self, response):
        """
        Extracts potential filenames from the response by finding patterns like **filename**.
        It assumes filenames are enclosed in double asterisks (**) and can later be filtered.
        """
        extracted_files = []
        start_index = 0

        while True:
            # Find the next occurrence of **
            start_marker = response.find("**", start_index)
            if start_marker == -1:
                break  # No more ** found, exit the loop

            # Find the closing ** for the file name
            end_marker = response.find("**", start_marker + 2)
            if end_marker == -1:
                break  # No closing **, exit the loop

            # Extract the potential filename
            potential_filename = response[start_marker + 2:end_marker].strip()

            # Add it to the list of extracted files
            if potential_filename:  # Ensure we don't add empty strings
                extracted_files.append(potential_filename)

            # Move the start index forward to search for the next filename
            start_index = end_marker + 2

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
