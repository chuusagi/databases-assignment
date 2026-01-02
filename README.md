dgd -> yr2
home assignment


TASK 1
- python version: 
- plugins used:  
- virtual environment created by executing the folloiwng in VS Code terminal:
        python -m venv .venv
        .venv\Scripts\activate
    (note: was unable to load scripts due to execution of scripts being disabled on system )
    (as such, additionally ran Set-ExecutionPolicy Unrestricted -Scope Process)
- .env file was created and then added to .gitingore file
- installed all dependencies required, namely:
        FastAPI - web framework for building APIs
            -  pip install fastapi
        2. Uvicorn - ASGI server implementation, using uvloop and httptools.
            - pip install uvicorn
        3. Motor - async driver for MongoDB
            - pip install motor
        4. Pydantic - data validation and settings management using Python type annotations
            - pip install pydantic
        5. Python-dotenv - reads key-value pairs from a .env file and can set them as environment variables
            - pip install python-dotenv
        6. Requests - HTTP library for Python
            - pip install requests
    (note: pip freeze was run in order to create requirements.txt. this holds a list of said depenencies)
    (if warning "Form data requires "python-multipart" to be installed" occures)
    (run "pip install python-multipart" in order to install additonal missing dependency)
- file main.py was created in order to store FastAPI code
- API launch using "uvicorn main:app --reload" command in VS Code terminal
    (note: API will be accessible in the browser at http://127.0.0.1:8000/docs)

