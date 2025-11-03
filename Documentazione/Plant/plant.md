# **PLANT – Descrizione dei flussi e delle API**

## **Architettura generale**

L’architettura del sistema prevede chiamate tra diversi microservizi, secondo il seguente schema:

```
Client
↓ (REST API – chiamata al BS)
PlantAPI (borepurposingmgmt)
↓ (chiamata interna BS)
PlantService (borepurposingmgmt)
↓ (chiamata al MS)
PlantControllerReadWrite (meRepurposingReg)
↓
Database
```

---

Il modulo **Plant API** espone tre endpoint REST che permettono di:

1. Recuperare i dettagli di un singolo **Plant** tramite il suo identificativo univoco.
2. Effettuare una ricerca di un **Plant** in base a parametri di filtro.
3. Aggiornare le informazioni di un **Plant** esistente.

---

## **GET /v1/plants/{id}**

### **Descrizione**

Consente di ottenere i dettagli di un Plant specifico tramite il suo identificativo (`id`).

### **Flusso operativo**

1. Il **Client** effettua una richiesta `GET /v1/plants/{id}`.
2. La **Plant API** riceve la richiesta e la inoltra al **Plant Service** per l’elaborazione.
3. Il **Plant Service** prepara la richiesta remota impostando gli opportuni parametri e inoltra la chiamata verso il microservizio **Plant API (meRepurposingReg)**.
4. Il microservizio interroga il **Database** per recuperare i dati dell’impianto corrispondente.
5. I dati trovati vengono restituiti alla **Plant API**, che li inoltra al client.

### **Risposte possibili**

* **200 OK** → Risorsa trovata; i dettagli sono restituiti in formato JSON.
* **400 Bad Request** → Parametro `id` non valido.
* **404 Not Found** → Nessuna risorsa trovata corrispondente all’identificativo indicato.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con il servizio remoto.

---

## **POST /v1/plants/search**

### **Descrizione**

Consente di cercare uno o più Plant in base a criteri di filtro.

### **Flusso operativo**

1. Il **Client** invia una richiesta `POST /v1/plants/search` con un body JSON conforme al modello `PlantSearchDTORequest`.
2. La **Plant API** inoltra la richiesta al **Plant Service**, che gestisce la logica di instradamento.
3. Il **Plant Service** invia la richiesta di ricerca al microservizio **Plant API (meRepurposingReg)**.
4. Il microservizio esegue la query sul **Database** in base ai filtri ricevuti.
5. I risultati vengono restituiti alla **Plant API**, che li inoltra al client.

### **Risposte possibili**

* **200 OK** → Ricerca completata con successo; la risposta contiene la lista dei Plant trovati.
* **500 Internal Server Error** → Errore generico nella chiamata remota o durante l’elaborazione.

---

## **PATCH /v1/plants/{id}**

### **Descrizione**

Consente di aggiornare le informazioni di un Plant esistente.

### **Flusso operativo**

1. Il **Client** invia una richiesta `PATCH /v1/plants/{id}` contenente il body JSON `PlantUpdateDTORequest` con i campi da aggiornare.
2. La **Plant API** riceve la richiesta e la inoltra al **Plant Service**.
3. Il **Plant Service** invia la richiesta di aggiornamento al microservizio **Plant API (meRepurposingReg)**.
4. Il microservizio esegue l’operazione di aggiornamento sul **Database**.
5. La risposta viene restituita alla **Plant API**, che la inoltra al client.

### **Risposte possibili**

* **204 No Content** → Aggiornamento eseguito con successo; nessun contenuto restituito.
* **400 Bad Request** → Parametri o corpo della richiesta non validi.
* **404 Not Found** → Risorsa non trovata.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con il servizio remoto.
