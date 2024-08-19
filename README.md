# Telegram Dictionary Bot

This is a Telegram bot that provides word definitions, spell checking, and pronunciation. The bot can be used in both inline mode and direct chat, making it versatile for various use cases.

## Features

- **Word Definitions**: Get detailed definitions for words using the Free Dictionary API.
- **Pronunciation**: Access pronunciation audio for words directly within the bot.
- **Spell Checking**: Automatically corrects misspelled words before searching for definitions.
- **Inline Mode**: Search for word definitions directly in any Telegram chat using inline queries.
- **Direct Chat Mode**: Interact with the bot directly to get word definitions and pronunciation.

## Requirements

- Python 3.7+
- Telegram Bot Token (You can get one by creating a bot on [BotFather](https://core.telegram.org/bots#botfather))

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/telegram-dictionary-bot.git
    cd telegram-dictionary-bot
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables:

    - Create a `.env` file in the root directory of the project.
    - Add your Telegram Bot token and the Free Dictionary API URL:

    ```plaintext
    TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    DICTIONARY_API_URL=https://api.dictionaryapi.dev/api/v2/entries/en/
    ```

## Usage

1. Run the bot:

    ```bash
    python bot.py
    ```

2. Open Telegram and start a chat with your bot.

### Commands

- `/start`: Start a conversation with the bot.
- Inline Mode: Use the bot's inline mode to search for words in any chat by typing `@InWordyBot <word>`.

### Direct Chat Features

- Simply send a word or phrase to the bot, and it will return definitions with pronunciation options if available.
- The bot will respond with the first definition without a bullet, and subsequent definitions will be bullet-pointed.

## Error Handling

The bot includes error handling for network issues and API errors, ensuring a smooth user experience.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue if you find a bug or have a feature request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
