# **COUNTERPART – Descrizione dei flussi e delle API**

## **Architettura generale**

L’architettura del sistema prevede chiamate tra diversi microservizi, secondo il seguente schema:

```
Client
↓ (REST API – chiamata al BS)
CounterpartAPI (borepurposingmgmt)
↓ (chiamata interna BS)
CounterpartService (borepurposingmgmt)
| |
| ↓
| Document Node Service
|
↓ (chiamata al MS)
CounterpartControllerReadWrite (meRepurposingReg)
↓
Database
```

---

Il modulo **Counterpart API** espone sei endpoint REST che permettono di:

1. Recuperare i dettagli di una singola **Counterpart** tramite identificativo univoco.
2. Creare un nuovo **Counterpart** con un flusso esteso che prevede la creazione asincrona dei "document node" correlati.
3. Aggiornare una **Counterpart** esistente.
4. Eliminare una **Counterpart**.
5. Cercare una o più **Counterpart** in base a criteri di filtro.
6. Importare più **Counterpart** da un file Excel.

---

## **GET /v1/counterparts/{id}**

### **Descrizione**

Consente di ottenere i dettagli di un **Counterpart** specifico tramite il suo identificativo (`id`).

### **Flusso operativo**

1. Il **Client** effettua una richiesta `GET /v1/counterparts/{id}`.
2. La **Counterpart API** riceve la richiesta e la inoltra al **Counterpart Service**.
3. Il **Counterpart Service** imposta i parametri della chiamata remota e inoltra la richiesta verso il microservizio **Counterpart API (meRepurposingReg)**.
4. Il microservizio interroga il **Database** per recuperare il Counterpart corrispondente all'identificativo indicato.
5. La risorsa trovata viene restituita in formato JSON alla **Counterpart API**, che la inoltra al client.

### **Risposte possibili**

* **200 OK** → Risorsa trovata; i dettagli di Counterpart vengono restituiti in formato JSON.
* **400 Bad Request** → Parametro `id` non valido.
* **404 Not Found** → Nessuna risorsa trovata per l’identificativo indicato.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con il servizio remoto.

---

## **PATCH /v1/counterparts/{id}**

### **Descrizione**

Consente di aggiornare le informazioni di un **Counterpart** esistente identificato dal suo identificativo univoco (`id`).

### **Flusso operativo**

1. Il **Client** effettua una richiesta `PATCH /v1/counterparts/{id}` contenente il body JSON conforme al modello CounterpartDTORequest con i campi aggiornati.
2. **Counterpart API** inoltra la richiesta al **Counterpart Service** che viene convertita in un wrapper conforme al modello WrapperCounterpartUpdateDTORequest per l'update multiplo.
3. Il **Counterpart Service** prepara la richiesta di aggiornamento e invia la chiamata al microservizio **Counterpart API (meRepurposingReg)**.
4. Il microservizio esegue l’aggiornamento sul **Database** dei record corrispondenti.
5. La risposta viene restituita al **Client** tramite la **Counterpart API**.

### **Risposte possibili**

* **204 No Content** → Aggiornamento completato con successo; nessun contenuto restituito.
* **400 Bad Request** → Parametri o corpo della richiesta non validi.
* **404 Not Found** → Risorsa non trovata per l'identificativo indicato.
* **500 Internal Server Error** → Errore durante l’elaborazione o la comunicazione con il servizio remoto.

---

## **POST /v1/counterparts**

### **Descrizione**

Consente di creare uno o più **Counterpart**. Il flusso di creazione è articolato e prevede anche la creazione asincrona dei _node document_ associati a ciascun Counterpart e il successivo aggiornamento dei record con il riferimento al node dcocument .

### **Flusso operativo**

#### **Richiesta di creazione**

1. Il **Client** invia una richiesta `POST /v1/counterparts` con un body JSON conforme al modello CounterpartDTORequest.
2. **Counterpart API** riceve la richiesta e la inoltra al **Counterpart Service**.
3. Il **Counterpart Service** converte la richiesta in un wrapper multiplo (WrapperCounterpartCreateDTORequest) e la inoltra al microservizio Counterpart API (meRepurposingReg) tramite chiamata POST /v1/counterparts/multi.
4. Il microservizio esegue l’inserimento nel **Database** e restituisce un oggetto CreateMultiDTOResponse contenente gli identificativi ids[] dei Counterpart creati.

#### **Creazione asincrona dei document node e aggiornamento dei Counterpart**

1. In parallelo, il Counterpart Service avvia un flusso asincrono per la creazione dei Document Node associati a ciascun Counterpart. Il servizio recupera la lista degli Id e ricerca i Counterpart tramite la chiamata POST /v1/counterparts/search.
2. Per ogni Counterpart trovato, viene effettuata una chiamata al Document Node Service (POST /v1/documents/nodes) per creare il document node relativo (CreateNodeDTORequest).
3. Il servizio riceve in risposta un NodeDTOResponse con l’identificativo del nodo (nodeId), che viene associato al rispettivo Counterpart.
4. Counterpart Service effettua una chiamata PATCH /v1/counterparts/multi verso il microservizio Counterpart API (meRepurposingReg), passando un WrapperCounterpartUpdateDTORequest con gli ID e i rispettivi nodeId da aggiornare.
5. Il microservizio meRepurposingReg aggiorna i record nel Database.
6. Il Counterpart Service restituisce infine al Client l’esito complessivo dell’operazione.

### **Risposte possibili**

* **201 Created** → Creazione avvenuta con successo; risposta contenente gli identificativi delle nuove risorse.
* **400 Bad Request** → Parametri o corpo della richiesta non validi.
* **404 Not Found** → Risorse correlate non trovate.
* **409 Conflict** → Risorsa già esistente.
* **500 Internal Server Error** → Errore durante la creazione o nella comunicazione con il servizio remoto.

---

## **DELETE /v1/counterparts/{id}**

### **Descrizione**

Consente di eliminare un **Counterpart** esistente tramite il suo identificativo (`id`).

### **Flusso operativo**

1. Il **Client** invia una richiesta `DELETE /v1/counterparts/{id}` indicando l’identificativo del Counterpart da eliminare.
2. **Counterpart API** inoltra la richiesta al **Counterpart Service**.
3. Il **Counterpart Service** imposta la chiamata remota e inoltra la richiesta di eliminazione al microservizio **Counterpart API (meRepurposingReg)**.
4. Il microservizio interroga il **Database** ed elimina la risorsa corrispondente all'indentificativo indicato.
5. La risposta finale viene restituita al **Client**.

### **Risposte possibili**

* **204 No Content** → Eliminazione completata con successo; nessun contenuto restituito.
* **400 Bad Request** → Parametri non validi.
* **404 Not Found** → Risorsa non trovata.
* **409 Conflict** → Impossibile eliminare la risorsa per vincoli o relazioni esistenti.
* **500 Internal Server Error** → Errore durante l’elaborazione o la comunicazione con il servizio remoto.

---

## **POST /v1/counterparts/search**

### **Descrizione**

Permette di cercare una o più **Counterpart** in base a specifici parametri di filtro.

### **Flusso operativo**

1. Il **Client** invia una richiesta `POST /v1/counterparts/search` con un body JSON conforme al modello CounterpartSearchDTORequest contenente i criteri di ricerca.
2. **Counterpart API** riceve e inoltra la richiesta al **Counterpart Service**.
3. Il **Counterpart Service** esegue la ricerca remota tramite il microservizio **Counterpart API (meRepurposingReg)**.
4. Il microservizio effettua interroga il **Database** in base ai filtri forniti.
5. I risultati vengono restituiti al **Client**.

### **Risposte possibili**

* **200 OK** → Ricerca completata con successo; la risposta contiene la lista delle controparti trovate.
* **404 Not found** -> Nessuna risorsa trovata corrispondente ai filtri indicati.
* **500 Internal Server Error** → Errore durante l’elaborazione o la comunicazione con il servizio remoto.

---

## **POST /v1/counterparts/import**

### **Descrizione**

Consente di importare più **Counterpart** a partire da un file Excel contenente i dati.

### **Flusso operativo**

#### **Upload e parsing del file**

1. Il **Client** invia una richiesta `POST /v1/counterparts/import`con il file Excel allegato nel body (multipart/form-data o binario).
2. **Counterpart API** riceve la richiesta e la inoltra al **Counterpart Service**.
3. Il **Counterpart Service** elabora il contenuto del file e costruisce un JSON conforme al modello WrapperCounterpartCreateDTORequest per la richiesta di creazione multipla.

#### **Richiesta di creazione**

1. Il **Counterpart Service** inoltra al microservizio Counterpart API (meRepurposingReg) tramite chiamata POST /v1/counterparts/multi.
2. Il microservizio interroga il **Database** e restituisce una risposta CreateMultiDTOResponse contenente gli identificativi ids[] dei Counterpart creati.

#### **Creazione asincrona dei document node e aggiornamento dei Counterpart**

1. In parallelo, il Counterpart Service avvia un flusso asincrono per la creazione dei Document Node associati a ciascun Counterpart. Il servizio recupera la lista degli Id e ricerca i Counterpart tramite la chiamata POST /v1/counterparts/search.
2. Per ogni Counterpart trovato, viene effettuata una chiamata al Document Node Service (POST /v1/documents/nodes) per creare il document node relativo (CreateNodeDTORequest).
3. Il servizio riceve in risposta un NodeDTOResponse con l’identificativo del nodo (nodeId), che viene associato al rispettivo Counterpart.
4. Counterpart Service effettua una chiamata PATCH /v1/counterparts/multi verso il microservizio Counterpart API (meRepurposingReg), passando un WrapperCounterpartUpdateDTORequest con gli ID e i rispettivi nodeId da aggiornare.
5. Il microservizio meRepurposingReg aggiorna i record nel Database.
6. Il Counterpart Service restituisce infine al Client l’esito complessivo dell’operazione.

### **Risposte possibili**

* **201 Created** → Importazione completata con successo; risposta contenente gli identificativi delle risorse create.
* **400 Bad Request** → File non valido o contenuto errato.
* **409 Conflict** → Alcune risorse risultano già presenti.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con il servizio remoto.

---

## **Riepilogo Endpoint**

| Metodo     | Endpoint                  | Descrizione                                  |
|------------|---------------------------|----------------------------------------------|
| **GET**    | `/v1/counterparts/{id}`   | Recupera i dettagli di un Counterpart.       |
| **PATCH**  | `/v1/counterparts/{id}`   | Aggiorna i dati di un Counterpart esistente. |
| **POST**   | `/v1/counterparts`        | Crea un nuovo Counterpart.                   |
| **DELETE** | `/v1/counterparts/{id}`   | Elimina un Counterpart.                      |
| **POST**   | `/v1/counterparts/search` | Effettua una ricerca dei Counterpart.        |
| **POST**   | `/v1/counterparts/import` | Importa Counterpart da un file Excel.        |

---