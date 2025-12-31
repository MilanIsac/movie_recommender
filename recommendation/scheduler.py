from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

def monthly_task():
    print(f'Monthly task executed at {datetime.now()}')
    
    from web_scraping import fetch_movies
    import model
    from main import model_reload
    
    try:
        
        fetch_movies('popular', pages=10, delay=1.2)
        fetch_movies('now_playing', pages=10, delay=1.2)
        fetch_movies('upcoming', pages=10, delay=1.2)
        
        model
        time.sleep(2)
        model_reload()
        
        print('Monthly task completed.')
    
    except Exception as e:
        print('Error occurred during monthly task: ', e)
        

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        func=lambda: threading.Thread(target=monthly_pipeline).start(),
        trigger='interval',
        days=30,
        id='monthly_task',
        replace_existing=True
    )
    
    scheduler.start()
    print('Scheduler started for monthly tasks.')