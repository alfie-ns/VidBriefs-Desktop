# VidBriefs-Desktop Virtual Environment Setup

## 1. Obtain OpenAI API Key

Get your OpenAI API key from: https://platform.openai.com/api-keys

## 2. Create Environment for API Key

Run the following bash script in the scripts/ directory:

```
scripts/create-env.sh
```

## 3. Add API Key to Environment

Create a `.env` file and add your API key:

```
OPENAI_API_KEY=your-api-key-here
```

Alternatively, use nano:

```
nano .env
```

Then add: `OPENAI_API_KEY=your-api-key-here`

## 4. Create Virtual Environment

In the project's root directory, run:

```
python -m venv venv
```

## 5. Activate Virtual Environment

Activate the virtual environment:

```
source venv/bin/activate
```

## 6. Install Dependencies

Once in the virtual environment, run:

```
./install-requirements.sh
```

## Available Scripts

- `./youtube.py`: Script to load and discuss YouTube videos
- `./tedtalks.py`: Script to recommend and discuss TED Talks
- `./categorise.py`: Process to organize markdown files into categories

Execute Python scripts using their respective shebang, e.g.:

```
./youtube.py
```
