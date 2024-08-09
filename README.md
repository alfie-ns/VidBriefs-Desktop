# VidBriefs-Desktop

1. Get your OpenAI API key: **https://platform.openai.com/api-keys**

---

2. Create environment to hold API key:  run create-env.sh bash script in root directory

---

3. Create .env file and paste in: **OPENAI_API_KEY={api-key}**

   || 'nano .env' then  OPENAI_API_KEY={api-key}

---

4. In the terminal directory for this project, run: **python -m venv venv**

---

5. Now, run: **source venv/bin/activate**

---

6. If previous commands ran correctly, you are now in a dependency-isolated virtual environment, now run **./install-requirements.sh**

---

**./youtube.py** - script to load and talk about Youtube videos
**./tedtalks.py** - script to reccomend and talk about Ted Talks
...
**./categorise.py** - process to organise markdown files into categories

execute Python scripts with using respective script's shebang, e.g. **./youtube.py**
