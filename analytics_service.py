from sqlalchemy.orm import Session
from database import Job, Application, Outreach
from datetime import datetime

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def log_job_found(self, job_data: dict):
        # Check if exists
        exists = self.db.query(Job).filter_by(platform_job_id=job_data['id']).first()
        if not exists:
            new_job = Job(
                platform_job_id=job_data['id'],
                title=job_data['title'],
                company=job_data['company'],
                url=job_data['url'],
                status="found"
            )
            self.db.add(new_job)
            self.db.commit()
            print(f"Logged new job: {job_data['title']}")

    def get_conversion_rate(self) -> float:
        total = self.db.query(Job).count()
        applied = self.db.query(Job).filter(Job.status == "applied").count()
        if total == 0:
            return 0.0
        return (applied / total) * 100

    def generate_report(self):
        rate = self.get_conversion_rate()
        print(f"--- Analytics Report ---")
        print(f"Total Jobs Found: {self.db.query(Job).count()}")
        print(f"Applied: {self.db.query(Job).filter(Job.status == 'applied').count()}")
        print(f"Conversion Rate: {rate:.2f}%")

if __name__ == "__main__":
    # Test
    from database import init_db
    db = init_db()
    analytics = AnalyticsService(db)
    analytics.generate_report()
