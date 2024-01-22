def create_app():
    
    from flask import Flask, current_app
    app = Flask(__name__, instance_relative_config=True)
    @app.route("/")
    def home():
        return current_app.send_static_file('index.html')
    @app.route('/favicon.ico')
    def favicon():
        return current_app.send_static_file('favicon.ico')
    
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()
    app.config.from_mapping(dotenv_values())

    from flask_cors import CORS
    CORS(app, origins="*")

    # connect to mongo
    from flaskr.db import db
    db.connectDB() 
    
    # setup email sender
    from flaskr.utils.email_helper import EmailSender
    EmailSender.get_instance().init_app(app)
    
    # json converter
    from flaskr.utils.json_helper import CustomJSONProvider
    app.json = CustomJSONProvider(app)
    
    # error handler
    from flaskr.errors.bad_request import BadRequestError
    from flaskr.errors.not_found import NotFoundError
    from flaskr.errors.unauthenicated import UnauthenticatedError
    from flaskr.errors.forbidden import ForbiddenError
    from pymongo.errors import OperationFailure
    from werkzeug.exceptions import HTTPException
    from flaskr.errorHandlers.my_handler import my_handler
    from flaskr.errorHandlers.pymongo_handler import pymongo_handler
    from flaskr.errorHandlers.default_http_handler import default_http_handler
    from flaskr.errorHandlers.default_handler import default_handler
    app.register_error_handler(BadRequestError, my_handler)
    app.register_error_handler(NotFoundError, my_handler)
    app.register_error_handler(UnauthenticatedError, my_handler)
    app.register_error_handler(ForbiddenError, my_handler)
    app.register_error_handler(OperationFailure, pymongo_handler)
    app.register_error_handler(HTTPException, default_http_handler)
    app.register_error_handler(Exception, default_handler)
    
    # api/v1/auth
    from flaskr.controllers.authController import authBP
    app.register_blueprint(authBP)
    
    # api/v1/plants
    from flaskr.controllers.plantController import plantBP
    app.register_blueprint(plantBP)
    
    # api/v1/predicts
    from flaskr.controllers.predictController import predictBP
    app.register_blueprint(predictBP)
    
    # api/v1/users
    from flaskr.controllers.userController import userBP
    app.register_blueprint(userBP)
    
    from flaskr.utils.predict_helper import PredictClient
    PredictClient(5001).listen()
    
    import cloudinary
    cloudinary.config(
        cloud_name=app.config.get("CLOUD_NAME"),
        api_key=app.config.get("API_KEY"),
        api_secret=app.config.get("API_SECRET"),
        secure=True,
    )

    
    return app