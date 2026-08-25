from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": "The request is invalid."
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication is required."
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "message": "You do not have permission to perform this action."
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            "error": "Conflict",
            "message": "The resource already exists."
        }), 409

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }), 500