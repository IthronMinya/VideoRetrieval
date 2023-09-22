- Requirements: 
    - [Python 3.10+](https://www.python.org/downloads/)
    - [NodeJS](https://nodejs.org/en)


1. Create Python virtual enviroment and install requirements.txt
   - when you restart your workspace you will need to activate it again, just run the second line
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   > after that we activate it and install needed dependencies

3. Get all svelte packages and npm dependencies
```cmd
cd ./frontend
npm install
cd ../
```

4. Build svelte and run fastapi with uvicorn. The prepare statement builds the css from the material design theme
```cmd
cd ./frontend
npm run prepare
npm run build; cd ../
uvicorn main:app --reload
```
5. When developing in Svelte, you can use dev server
```cmd
npm run dev
```

Main Entry is the python main.py into frontend/index.html and all components are created in frontend/src/App.svelte
