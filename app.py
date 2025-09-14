from flask import Flask
from config import Config
from extensions import db  # db buradan geliyor

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # db'yi app ile bağla

import models  # modeller en sonda import edilmeli

@app.route("/")
def hello():
    return "Kopernik Pizza is running 🍕"

if __name__ == "__main__":
    app.run(debug=True)
