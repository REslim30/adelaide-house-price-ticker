FROM public.ecr.aws/lambda/python:3.7

# Install special amazon linux chrome driver
RUN curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
RUN unzip chromedriver.zip && cp chromedriver /usr/local/bin/chromedriver && chmod +x /usr/local/bin/chromedriver

# Install special amazon linux headless chrome
RUN curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
RUN unzip headless-chromium.zip && cp headless-chromium /usr/bin/headless-chromium && chmod +x /usr/bin/headless-chromium

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy all python files
COPY *.py adelaide_suburbs.geojson ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.main" ]