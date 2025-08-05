#source C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/outfit-generator-2-poc/.venv/Scripts/activate.bat

sleep 0.2
cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/eigenlib
git add .
git commit -m "cluster submit"
git push
sleep 0.2
databricks repos update --repo-id 40158810694901 --branch main

cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/swarm-intelligence-project
git add .
git commit -m "cluster submit"
git push
sleep 0.2
cd C:/Users/AlejandroPrendesCabo/Desktop/Proyectos/swarm-intelligence-project
databricks repos update --repo-id 564247559775205 --branch main
sleep 0.2