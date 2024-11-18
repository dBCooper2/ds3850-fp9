# ds3850-fp9: ChatGPT GUI

This Project creates a GUI using PyQt6 to connect to the OpenAI API and send requests. `app.py` handles the GUI Logic, `test.py` was a program used to test the connection (I kept getting an error where OpenAI was telling me I ran out of usage, despite never communicating with the server), and lastly `ratelimiter.py` is used to limit the number of requests sent to OpenAI, fixing the issue I was having with `app.py`'s connections to the API.

## Running the Program

To run the program, create an API key from [OpenAI's website](<https://openai.com/index/openai-api/>). Then save that key in a special location, and DO NOT SHARE IT!

You can either enter the API key into the program, which will create the environment variable, or you can add it to the program with the following instructions:

### Adding API Key to `.env`

Then you will navigate to your project's directory, and enter the command:

```bash
touch .env
```

This creates the environment file to store the API key. Next, add the key to the file with:

```bash
echo 'OPENAI_API_KEY=paste-your-key-here' > .env
```

This will paste the text in the string into the `.env` file. **IMPORTANT: Make sure your `.env` file will not be included in your git commits!** Check your `.gitignore` file to make sure, you should see

`.gitignore`

```git

# The rest of the GitIgnore...

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# The rest of the GitIgnore...

```

### Installing Packages and Running the Program

Lastly, to run the program create a virtual environment and install the packages:

```bash
python -m venv .venv-name
```

Make sure not to use `.env` as a name!

```bash
source .venv-name/bin/activate

pip install pyqt6 python-dotenv openai
```

Once the packages are installed, run the program with:

```bash
python3 app.py
```

