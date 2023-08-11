
pyenv install 3.7
pyenv local 3.7

curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
unzip chromedriver.zip
unzip headless-chromium.zip
zip chromdriver-v2.zip chromedriver headless-chromium

python -m pip install -r requirements.txt -t python/lib/python3.7/site-packages
zip -r python -i python.zip

rm -rf dist
mkdir dist
zip ./dist/deployment.zip *.py
aws lambda update-function-code --function-name adelaide-house-price-ticker --zip-file fileb://dist/deployment.zip