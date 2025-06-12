from controllers.feedback import feedback_bp
from controllers.form import form_bp

def initial_routes(app):
    app.register_blueprint(feedback_bp)
    app.register_blueprint(form_bp)