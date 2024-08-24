# VidBriefs-Desktop Virtual Environment Setup

## 1. Obtain OpenAI API Key

Get your OpenAI API key from: https://platform.openai.com/api-keys

## 2-bash. Create Environment for API Key

Run the following bash script in the scripts/ directory:

```
./scripts/create-env.sh
```

## 2. Add API Key to Environment

Create a `.env` file and add your API key:

Alternatively, use nano:

```
nano .env
```

Then add: `OPENAI_API_KEY=your-api-key-here`

```
OPENAI_API_KEY=your-api-key-here
```

## 3. Create Virtual Environment

In the repository's root directory, run:

```
python -m venv venv
```

## 4. Activate Virtual Environment

Activate the virtual environment with the following command:

```
source venv/bin/activate
```

## 5. Install Dependencies

Once in the virtual environment, run:

```
./install-requirements.sh
```

**Or if you don't have bash** do the following:

```
pip install -r requirements.txt
```

## Available Scripts

- `./youtube.py`: Script to load and discuss YouTube videos
- `./tedtalks.py`: Script to recommend and discuss TED Talks
- `./sight.py`: Don't really know yet
- `./nexus.py`: Web-Browsing-Enhanced Chat Assistant
- `./categorise.py`: Process to organize markdown files into categories

Execute Python scripts using their respective shebang, e.g.:

```
./youtube.py
```

**Or run the run-desktop.sh script in the home/root directory:**

```


