from modules.model.FileSyntaxCorrector import FileSyntaxCorrector

class FileContentFormatter:
    """
    Handles formatting of file contents for API requests and response parsing.
    Encapsulates logic for preparing file contents with proper syntax correction and formatting.
    """

    def __init__(self):
        self.syntax_corrector = FileSyntaxCorrector()  # Handles syntax corrections for file contents

    def make_file_content_text(self, project_dir, chosen_files, editor_mode):
        """
        Constructs the formatted text containing file contents for API requests.
        Includes syntax correction and special formatting instructions for editor mode.
        """
        if not chosen_files:
            return ""

        file_contents = []
        header = "Here is my file" if len(chosen_files) == 1 else "Here are my files"
        file_contents.append(header)

        for relative_path in chosen_files:
            file_path = os.path.join(project_dir, relative_path)
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()

                    # Correct the file content syntax using FileSyntaxCorrector
                    content = self.syntax_corrector.prepare_for_encoding(content)

                file_contents.append(f"**{relative_path}**\n```\n{content}\n```\n")

        keep_filenames_request = (
            "Here are the rules of formatting which you MUST follow formatting your response:\n"
			"- Rules how to provide path of modified file:\n"
            "  * Please return the content of each file with its corresponding file path.\n"
            "  * Do not omit the file paths.\n"
            "  * If you are editing file provided by user, do not modify original file path.\n"
            "  * Each file path should be enclosed in double asterisks (**file_path**), followed immediately by the modified content inside a code block.\n"
            "  * Do not use ### before file path.\n"
            "  * Do not use row of '─' before or after file path.\n"
            "  * Do not insert any text, explanations, or comments before, after, or between the file path and the code block.\n"
            " - Rules how to format file content:\n"
            "  * The code block should not contain a language as first string.\n"
            "  * The code block should not contain file path as first string. File path should be provided in the format mentioned above.\n"
            "  * The content inside the code block should be the file content only, with no additional comments, explanations, or markers.\n"
            "  * If any files are modified, provide the entire content of each modified file, including any unmodified sections to allow direct replacement.\n"
            "  * Do not write '# (No changes below this point)' - return entire content of modified file instead.\n"
            "  * Do not write '# (No changes above this point)' - return entire content of modified file instead.\n"
            " - Rules which files include into the response:\n"
            "  * If a file provided by user remains unchanged, do not include it in the response.\n"
            "  * If you modified some provided file, include it's entire content.\n"
            " \n\n"
         )

        formatted_text = "\n".join(file_contents)
        if editor_mode:
            formatted_text += "\n" + keep_filenames_request
            
        return formatted_text
