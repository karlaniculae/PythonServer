Nume:Niculae Karla
Grupă: 333CC

# Tema 1 TODO
#### Este recomandat să folosiți diacritice. Se poate opta și pentru realizarea în limba engleză. 
Tema TODO
Organizare
	1	Am folosit o coada în care sa îmi tin joburile, joburile sunt obiecte care au requestu adică întrebarea, tipul de endpoint de la care a venit și job_id-ul. După aceea m-am dus în fiecare endpoint din ruta și am luat requestul, am construit jobul și l-am adăugat. Doar ca atunci când îl adaug verific și cu condition, îl setez ca sa îmi notifice threadurile ca un job mi s-a adăugat în coada. Am o funcție care îmi Adaugă joburile în coada, pe care am făcut-o în job_queue.py. După aceea în funcție de ce endpoint aveam, de exemplu pt cele cu POST, am un if în care sa văd dacă cumva am dat shutdown sa nu mi se mai adauge noi joburi. În get_results verii dacă am deja un fișier de temp file pentru jobul id respectiv, asta înseamnă ca statusul jobului este în running, dacă este un fiiser de forma job_id_numar.json înseamnă ca este done și pot sa întorc rezultatul, dacă nu găsesc niciun fișier creat înseamnă ca este invalid. În graceful_shutdown îmi setez un flag pe true, ceea ce înseamnă ca se da semnalul de shutdown. Și așa îmi notific prin condition sa se trezească toate trhreadurile apoi, ca sa nu cumva sa fie pe wait din condition de dinainte. În file Task_runner verific dacă este pe fals shutdown-ul ca threadurike sa poată sa ia joburile și sa le facă. Am folosit câte o funcție pentru fiecare calcul pe care il aveam de făcut.
	2	In endpointii (state_mean,states_mean,..) am luat job_id-ul fact din contorul dat in init, si asa il pun in obiectul meu job si il dau mai departe. Si inform status succes, failed in function de rezultat.
	3	În Task_runner am threaduri care se ocupa de joburi, dacă cumva coada nu e goală și s-adat semnalul de shutdown atunci înseamnă ca trebuie sa golesc joburile rămase. Iar înainte de asta în caz ca nu e shutdown, prelucrez normal joburile le iau din coada și le folosesc funcțiile.
	4	De asemenea tot acolo pun threadurile pe wait dacă nu am primit încă notify_all, și de abia după se prelucrează. Și acolo creez  fișiere temp pentru joburile scoase din coada, pt ca asta înseamnă ca sunt în runngin și dacă am fișier .temp înseamnă ca încă job respectiv e în running, dupa calcul suprascriu numele fierului cu numele corect de forma job_id_numar și asta înseamnă ca jobul este gata.
	5	În num_jobs am calculat nr de fisierele .temp pentru ca înseamnă ca atâtea joburi mai sunt în coada running.
	6	Am mai creat și logarea, folosindu-ma de documentația din oct, în init_py am configurat, și în router.py am creat ceea ce vreau sa scriu eu în loguri in functie de endpointul in care ma aflu.
	7	În api/jobs în funcție de numele fișierului din directori results, o sa spun dacă jobul este în running sau este done.
	8	 
Obligatoriu:
Exemplu states_mean cu logarile si creare de job:
        webserver.logger.info("States_mean status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter-1, y, type_of_question,  None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in states_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})
Exemplu creare temp file și suprascriere temp file cu rezultat și nume corect:
if not os.path.exists('results'):
                    os.makedirs('results')
                result_file_path = f"./results/job_id_{job.job_id}.temp"
                with open(result_file_path, 'w') as temp_file:
                    pass
                result = (Calculate(job.job_id, job.request_question, job.type_of_question,
                                    self.data_ingestor,job.state).process_question())
                temp_file_path = f"./results/job_id_{job.job_id}.temp"
                result_file_path = f"./results/job_id_{job.job_id}.json"
                with open(temp_file_path, 'w') as temp_file:
                    temp_file.write(json.dumps(result))
	•	Consideri că tema este utilă?
	•	Da mi s-a părut o tema chiar foarte interesanta, și un proiect pe care doresc sa îl pun pe GitHub.
	•	Consideri implementarea naivă, eficientă, se putea mai bine?
	•	Implementarea este foarte eficienta.
Implementare
	•	De specificat dacă întregul enunț al temei e implementat
	•	Aproape întreg enunțul este implementat, tot ce nu am  făcut sunt Unitesturile.
	•	Dificultăți întâmpinate
	•	Endpointul cu get_shutdown a fost mai dificil, dar am reușit sa îl fac.
	•	Lucruri interesante descoperite pe parcurs
	•	Mi s-a părut foarte interesanta crearea locurilor, eu am văzut ce sunt știam ce sunt, dar niciodată nu am creat unele.
Resurse utilizate
	•	Resurse utilizate - toate resursele publice de pe internet/cărți/code snippets, chiar dacă sunt laboratoare de ASC
	•	toate linkurile din tema
	•	https://www.geeksforgeeks.org/inter-thread-communication-with-condition-method-in-python/
	•	https://www.geeksforgeeks.org/multithreading-python-set-1/
	•	https://www.datacamp.com/tutorial/pandas-read-csv#
	•	https://www.w3schools.com/python/pandas/pandas_csv.asp
	•	https://www.geeksforgeeks.org/json-dump-in-python/
	•	https://stackoverflow.com/questions/69524576/how-to-extract-specific-data-from-csv-file-and-store-it-in-variable-using-pytho
	•	https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/

