# For running frontend 

- navigate to client folder 
``` cd client ```
```  npm i ```

- create .env.local with reference to .env.example
- log into google cloud console
- Start a project and get your key as json
- place the key.json at the root of client
- Upadte the backend url to your local backend endpoint (search http and replace)

``` npm run dev ```

- frontend will start at localhost


# Website flow

## Navigation Table

| Endpoint    | Description           | Navigation Options         | Navigated To |
|-------------|-----------------------|----------------------------|--------------|
| `/`         | Landing page          | Try now button             | `/chat`      |
| `/chat`     | New Chat window       | Sidebar: replay history    | `/replay`    |
|             |                       | Sidebar: upload PDFs       | `/upload`    |
| `/replay`   | Replay history        | Sidebar: upload PDFs       | `/upload`    |
| `/upload`   | Upload PDFs           |                            |              |


### /chat 

- Chat with the model.
- press play button to see the decision tree simulation
- Press Save Chat to save all the chat history for future replays 

### /replay

- Press play to sun the simulation of the latest saved chat history with the side by side decision tree

### /upload 

- upload pdfs you want to provide as data source 

