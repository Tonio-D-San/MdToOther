# **PROJECT – Descrizione dei flussi e delle API**

## **Architettura generale**

L’architettura del sistema prevede chiamate tra diversi microservizi, secondo il seguente schema:

```
Client
↓ (REST API – chiamata al BS)
ProjectTaskAPI (borepurposingmgmt)
↓ (chiamata interna BS)
ProjectTaskService (borepurposingmgmt)
↓ (chiamata al MS)
ProjectTaskControllerReadWrite (meRepurposingReg)
↓
Database
```

---

Il modulo **ProjectTask API** espone quattro endpoint REST che permettono di:

1. Recuperare la lista di **Tasks** tramite l' identificativo univoco del Project a cui sono associati.
2. Creare un nuovo **Task** associato ad un progetto specifico.
3. Aggiornare in modalità massiva gli stessi campi dei **Tasks**, associati ad un Project.
4. Aggiornare in modalità multipla campi diversi dei **Tasks** indicati, associati ad un Project.

---

## **GET /v1/projects/{projectId}**

### **Descrizione**

Consente di ottenere i dettagli di un **Project** specifico tramite il suo identificativo univoco `projectId`.

### **Flusso operativo**

1. Il **Client** effettua una richiesta `GET /v1/projects/{projectId}` al microservizio **BS (borepurposingmgmt)**.
2. Il **ProjectTask BS** riceve la richiesta, elabora i parametri e inoltra la chiamata al microservizio **MS (meRepurposingReg)**.
3. Il **ProjectTask MS** interroga il **Database** per ricercare il progetto corrispondente all’identificativo fornito.
4. Il record `ProjectDetailDTOResponse` viene restituito dal **MS** al **BS**, che a sua volta lo inoltra al **Client** in formato JSON.

### **Risposte possibili**

* **200 OK** → Risorsa trovata; i dettagli sono restituiti in formato JSON.
* **400 Bad Request** → Parametro `projectId` non valido.
* **404 Not Found** → Nessun progetto trovato con l’identificativo indicato.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con il servizio remoto.

---

## **POST /v1/projects/search**

### **Descrizione**

Permette di effettuare una ricerca di uno o più **Project** in base ai parametri forniti nel body della richiesta.

### **Flusso operativo**

1. Il **Client** invia una richiesta `POST /v1/projects/search` con un body JSON conforme al modello `ProjectSearchDTORequest` al microservizio **BS (borepurposingmgmt)**.
2. Il **ProjectTask BS** inoltra la richiesta al **MS (meRepurposingReg)**, che esegue la query sul **Database** applicando eventuali filtri e paginazione.
3. I risultati vengono restituiti dal **MS** al **BS** in un body conforme al modello `WrapperProjectDTOResponse`.
4. Il **BS** inoltra la risposta finale al **Client**.

### **Risposte possibili**

* **200 OK** → Ricerca completata con successo; la risposta contiene la lista dei progetti trovati.
* **500 Internal Server Error** → Errore generico nella chiamata remota o durante l’elaborazione.

---

## **POST /v1/projects**

### **Descrizione**

Consente di creare un nuovo **Project** all’interno del sistema.

### **Flusso operativo**

1. Una volta creato il progetto, il **BS** avvia il processo interno `CREATE_PROJECT_WORKSPACE`, responsabile di creare e collegare il *workspace documentale* al progetto.
2. Il **BS** invoca una route interna `SEARCH_PROJECT_BY_ID`, che effettua una chiamata `GET {meRepurposingRegEndPoint}/v1/projects/{id}` verso il **MS**.
3. Il **ProjectTask MS** interroga il **Database** per ottenere i dettagli completi del progetto.
4. Il **MS** restituisce una risposta `200 OK` contenente `ProjectDetailDTOResponse {id, nodeId, name, plant, ...}`. In caso di errore vengono gestite risposte `400 / 404 / 500`.
5. Se il progetto non ha ancora un `nodeId` valido, il **BS** comunica con il microservizio **DocumentNode MS (meEcDocument)**.
6. Il **BS** invia una richiesta `POST /v1/business-workspaces` per creare il *workspace documentale* associato al progetto.
7. Il **DocumentNode MS** crea il nodo nel **Database documentale** e restituisce una risposta `201 CREATED` contenente `IdentifierDTOResponse {id}`.
8. Successivamente, il **BS** effettua una richiesta `GET /v1/documents/nodes/{id}` verso il **DocumentNode MS** per recuperare i dettagli del nodo appena creato.
9. Se la chiamata ha esito positivo (`200 OK`), il campo `NODE_ID_PROPERTY` viene impostato con il valore `nodeId`.
10. In caso di errore (`404 / 500`), viene impostato un valore di fallback `OT_ERROR`.
11. Una volta recuperato il `nodeId`, il **BS** invoca una route interna `UPDATE_PROJECT_BY_ID_PROXY`, che effettua la chiamata `PATCH {meRepurposingRegEndPoint}/v1/projects/{projectId}`.
12. Il body della richiesta è un oggetto `ProjectUpdateDTORequest { nodeId, name, onHold, ... }`.
13. Il **ProjectTask MS** aggiorna il record `Project` nel **Database**, valorizzando il campo `nodeId` con quello appena ottenuto dal sistema documentale.
14. Il **MS** restituisce un esito `204 NO CONTENT` o, in caso di errore, un codice `400 / 404 / 500`.

### **Risposte possibili**

* **201 Created** → Creazione avvenuta con successo; la risposta contiene l’identificativo del nuovo progetto.
* **400 Bad Request** → Parametri non validi.
* **404 Not Found** → Risorsa o riferimento associato non trovato (es. plantId non valido).
* **500 Internal Server Error** → Errore durante la creazione o nella comunicazione con i microservizi.

---

## **PATCH /v1/projects/{projectId}**

### **Descrizione**

Consente di aggiornare le informazioni di un **Project** esistente tramite il suo identificativo univoco `projectId`.

### **Flusso operativo**

1. Il **Client** effettua una richiesta `PATCH /v1/projects/{projectId}` contenente un body JSON conforme al modello `ProjectUpdateDTORequest`.
2. Il **ProjectTask BS** riceve la richiesta e inoltra la chiamata al microservizio **MS (meRepurposingReg)**, che aggiorna i dati nel **Database**.
3. Al termine, il **BS** avvia un flusso asincrono per la gestione del nodo documento associato al progetto, tramite il microservizio **DocumentNode MS (meEcDocument)**.
4. Il processo asincrono prevede:

   * **Aggiornamento dei metadati** del nodo documento.
   * **Ridenominazione del nodo**, se il nome del progetto è variato.
   * **Spostamento del nodo**, se la posizione nel repository documentale deve essere aggiornata.
5. Al completamento delle operazioni, viene restituita la risposta al **Client**.

### **Risposte possibili**

* **204 No Content** → Aggiornamento eseguito con successo.
* **400 Bad Request** → Parametri o corpo della richiesta non validi.
* **404 Not Found** → Risorsa non trovata.
* **409 Conflict** → Conflitto sui dati (es. aggiornamento concorrente).
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione con i servizi remoti.

---

## **PATCH /v1/projects/multi**

### **Descrizione**

Consente di aggiornare più **Project** in un’unica operazione (*batch update*), tramite un body contenente una lista di progetti e relativi campi da aggiornare.

### **Flusso operativo**

1. Il **Client** invia una richiesta `PATCH /v1/projects/multi` con un body JSON conforme al modello `WrapperProjectUpdateDTORequest` al microservizio **BS (borepurposingmgmt)**.
2. Il **ProjectTask BS** inoltra la chiamata al **MS (meRepurposingReg)**, che esegue l’aggiornamento in batch sul **Database**.
3. L’esito dell’operazione viene restituito dal **MS** al **BS**, che inoltra la risposta al **Client**.

### **Risposte possibili**

* **204 No Content** → Aggiornamento completato correttamente.
* **400 Bad Request** → Formato del body o dati non validi.
* **404 Not Found** → Uno o più progetti non trovati.
* **409 Conflict** → Conflitto durante l’aggiornamento di uno o più record.
* **500 Internal Server Error** → Errore durante l’elaborazione o nella comunicazione tra microservizi.

---