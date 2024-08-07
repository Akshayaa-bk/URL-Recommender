from DbConnection import Base, engine, Session, URL
from email_sender import send_email  
from sqlalchemy import or_

class Recommender:
    def __init__(self):
        # Initialize database connection and create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        self.Session = Session

    def get_keywords_from_last_saved_url(self):
        # Retrieve the keywords of the last saved URL
        session = self.Session()
        keywords = session.query(URL.keywords).order_by(URL.url_savetime.desc()).first()
        session.close()
        # Split the keywords into a list, or return an empty list if no keywords are found
        return keywords[0].split(', ') if keywords else []

    
    
    def get_urls_by_keywords(self, keywords):
        # Retrieve URLs from the database where at least one keyword matches
        session = self.Session()

        # Constructing OR conditions for each keyword from the last saved URL
        keyword_filters = [URL.keywords.like(f'%{keyword}%') for keyword in keywords]

        # Querying distinct URLs where at least one keyword matches
        query = session.query(URL.url, URL.url_savetime).filter(or_(*keyword_filters)).order_by(URL.url_savetime.desc()).limit(5).all()

        session.close()
        return query

    def recommend_urls(self):
        # Generate URL recommendations based on the keywords from the last saved URL
        keywords = self.get_keywords_from_last_saved_url()
        return self.get_urls_by_keywords(', '.join(keywords))

    def send_recommendation_email(self, receiver_email):
        # Send an email with the recommended URLs to the given email address
        recommendations = self.recommend_urls()
        if recommendations:
            subject = "Daily Recommendations"
            body = "Recommended URLs:\n"
            for url, savetime in recommendations:
                body += f"{url} \n"
            send_email(receiver_email, subject, body)
        else:
            print("No recommendations found.")
    
    def close_connection(self):
        # Close the database connection
        self.Session().close()
