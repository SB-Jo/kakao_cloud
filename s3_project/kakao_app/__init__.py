from flask import Flask
import config

def create_app(config=None):
    app = Flask(__name__)

    if app.config["ENV"] == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    if config is not None:
        app.config.update(config)
    
    from kakao_app.routes import main_route
    app.register_blueprint(main_route.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config['ENV'] == 'production':
        app.run()
    else:
        app.run(debug=True)