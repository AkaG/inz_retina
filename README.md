# Retina scan

## Run project

To run project with all django features modify integrations/commands/main.py and run from terminal

```bash
python manage.py main
```

or create your own command

## Creating database

Run this commands:

```bash
python manage.py makemigrations data_module
```

```bash
python manage.py migrate
```

## Loading data

```bash
python manage.py loadDataFromPath [path]
```

## Image preprocessing

Run with default settings

```bash
python manage.py image_preprocessing
```