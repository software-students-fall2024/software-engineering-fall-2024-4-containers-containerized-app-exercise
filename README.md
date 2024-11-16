![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.


Way to access ML file now:

```bash
#create virtual environment
python -m venv myenv

#activate it 
(windows):
myenv\Scripts\activate
(mac):
source myenv/bin/activate

# activcate mongodb database
docer-compose up

# install dependencies
cd machine-learning-client
pip install -r requirements.txt

# run main or test_real
python main.py
python test_real.py
```
you can access the database at http://localhost:8080/
username: admin, password: pass

the emotion result can be see in database