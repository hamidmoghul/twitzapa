from flask import Flask, render_template, request
from .twitter_bc import add_or_update_user, vectorize_tweet
from .models_bc import DB, User, Tweet
from .predict_bc import predict_user


def create_app():
    app = Flask(__name__)
    app_title = "Twitoff DS37!!!!!!"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route("/test")
    def test():
        return f"<p>This is a page for {app_title}</p>"

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return """The database has been reset
        <a href='/'>Go to homepage</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """

    @app.route('/populate')
    def populate():
        user1 = User(id=1, username='elonmusk')
        DB.session.add(user1)
        user2 = User(id=2, username='nasa')
        DB.session.add(user2)
        user3 = User(id=3, username='John')
        DB.session.add(user3)
        user4 = User(id=4, username='Nancy')
        DB.session.add(user4)
        user5 = User(id=5, username='Kathy')
        DB.session.add(user5)
        tweet_text1 = 'this is my first tweet'
        tweet_text2 = 'going to the moon!'
        tweet_text3 = 'What would be your favorite videogame if you were a cat?'
        tweet_text4 = 'just hanging out'
        tweet_text5 = 'People love vacations!'
        tweet1 = Tweet(id=1, text=tweet_text1, user=user1,
                       vect=vectorize_tweet(tweet_text1))
        tweet2 = Tweet(id=2, text=tweet_text2, user=user2,
                       vect=vectorize_tweet(tweet_text2))
        tweet3 = Tweet(id=3, text=tweet_text3, user=user3,
                       vect=vectorize_tweet(tweet_text3))
        tweet4 = Tweet(id=4, text=tweet_text4, user=user4,
                       vect=vectorize_tweet(tweet_text4))
        tweet5 = Tweet(id=5, text=tweet_text5, user=user5,
                       vect=vectorize_tweet(tweet_text5))
        DB.session.add(tweet1)
        DB.session.add(tweet2)
        DB.session.add(tweet3)
        DB.session.add(tweet4)
        DB.session.add(tweet5)
        DB.session.commit()
        return """The database has been reset
        <a href='/'>Go to homepage</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """

    @app.route('/update')
    def update():
        users = User.query.all()
        for user in users:
            add_or_update_user(user.username)
        return render_template(
            'base.html',
            title="All users have been updated to include their latest tweets."
        )

    @app.route('/user', methods=['POST'])
    @app.route('/user/<user_name>', methods=['GET'])
    def user(user_name=None, message=''):
        try:
            if request.method == 'POST':
                user_name = request.values['user_name']
                add_or_update_user(user_name)
                message = f'User {user_name} was added succesfully'
            tweets = User.query.filter(User.username == user_name).one().tweets
        except Exception as e:
            message = f'Error occurred: {e}'
            tweets = []

        return render_template(
            'user.html',
            title=user_name,
            tweets=tweets,
            message=message
        )

    @app.route('/compare', methods=['POST'])
    def compare():
        user0 = request.values['user0']
        user1 = request.values['user1']
        hypo_tweet = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compare a user to themselves'
        else:
            prediction = predict_user(user0, user1, hypo_tweet)
            predicted_user = user0 if prediction == 0.0 else user1
            message = f'"{hypo_tweet}" is more likely said by {predicted_user}'

        return render_template(
            'prediction.html',
            title='Prediction',
            message=message
        )

    return app
