from flask import Flask, jsonify
import os

class KlikeApp:

    def __init__(self):

        self.app = Flask(__name__)

        # Ensure default Admin exists
        if "Admin" not in load_users():
            add_user("Admin", "Admin", "0000")

        self.setup_routes()

    def setup_routes(self):

        @self.app.route('/')
        def home():
            return jsonify({
                "message": "KLIKE v4 Healthcare Face Recognition System Running"
            })

        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "success"
            })

        @self.app.route('/users')
        def users():
            return jsonify(load_users())

        @self.app.route('/patients')
        def patients():
            return jsonify(load_patients())

        @self.app.route('/logs')
        def logs():
            return jsonify(load_logs())

        @self.app.route('/alerts')
        def alerts():
            return jsonify(load_alerts())

    def run(self):

        port = int(os.environ.get("PORT", 10000))

        self.app.run(
            host='0.0.0.0',
            port=port
        )
