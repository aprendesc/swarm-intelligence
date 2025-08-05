#source C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/<PROJECT_FOLDER>/.venv/Scripts/activate.bat

sleep 0.2
cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/eigenlib
git add .
git commit -m "cluster submit"
git push
sleep 0.2
databricks repos update --repo-id 40158810694901 --branch main

cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/<PROJECT_FOLDER>
git add .
git commit -m "cluster submit"
git push
sleep 0.2
cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/<PROJECT_FOLDER>
databricks repos update --repo-id <DB_REPO_ID> --branch main
sleep 0.2