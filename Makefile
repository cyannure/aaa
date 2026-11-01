.PHONY: setup data lab
setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && python -m ipykernel install --user --name aaa-accidents
data:
	.venv/bin/python src/download_data.py --year 2023
lab:
	.venv/bin/jupyter lab
