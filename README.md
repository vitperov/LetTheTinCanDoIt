# LetTheTinCanDoIt
![LetTheTinCanDoIt](resources/tinCan_big.png)

**LetTheTinCanDoIt** is a time-saving tool designed to streamline interactions with GPT models during development. It simplifies the process of sending multiple project files to a GPT-based assistant (such as OpenAI's models) and automatically updating the files on your local disk based on the model's response. This ensures that developers can focus on more valuable tasks while LetTheTinCanDoIt handles file inclusion, modification, and updates.

## Key Features

- **Efficient File Handling:** Select multiple project files and send them directly to GPT for analysis or modification.
- **Automatic File Updates:** Parse the response from GPT and automatically update the corresponding files on your disk, removing the need to manually copy and paste changes.
- **Saves Time:** By automating the file transfer and update process, LetTheTinCanDoIt helps developers save valuable time, allowing them to focus on core tasks.
- **Customizable Requests:** Include custom instructions or roles in the request to guide GPT in the desired direction.

## Why LetTheTinCanDoIt?

When working on complex projects, you often need to interact with multiple files and send them to GPT for suggestions or modifications. Doing this manually takes a significant amount of time, which could be better spent on other development tasks. LetTheTinCanDoIt eliminates this overhead by including the chosen files in your request and handling the update process automatically. This ensures a smoother, more efficient workflow for developers.

## Installation

To install and use **LetTheTinCanDoIt**, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/vitperov/LetTheTinCanDoIt.git
    cd LetTheTinCanDoIt
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Add your OpenAI API key:

   - Create a `settings/key.json` file and add your API key in the following format:

    ```json
    {
      "api_key": "your-openai-api-key"
    }
    ```

## Usage

1. Run the application:

    ```bash
    python gpt.py
    ```

2. Select the files you want to include in your request using the **FilesPanel**.
3. Input your prompt and specify a role or instructions in the **RoleSelector**.
4. Send the request to GPT. LetTheTinCanDoIt will include the chosen files and generate a response.
5. LetTheTinCanDoIt will parse the response and automatically update the corresponding files on your disk with the changes suggested by GPT.

## Contributing

Contributions are welcome! If you'd like to contribute to LetTheTinCanDoIt, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
