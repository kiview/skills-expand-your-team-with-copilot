"""
Database configuration and setup for Mergington High School API
Simple in-memory implementation for development/testing
"""

from argon2 import PasswordHasher
import copy

# In-memory storage
activities_data = {}
teachers_data = {}

# Mock collections for compatibility
class MockCollection:
    def __init__(self, data_store):
        self.data_store = data_store
    
    def count_documents(self, query):
        return len(self.data_store)
    
    def insert_one(self, document):
        doc_id = document.pop('_id')
        self.data_store[doc_id] = document
        return None
    
    def find(self, query=None):
        if query is None:
            return [{'_id': k, **v} for k, v in self.data_store.items()]
        # Simple query support for the use case
        results = []
        for doc_id, doc in self.data_store.items():
            match = True
            for key, value in query.items():
                # Handle nested queries like 'schedule_details.days'
                if '.' in key:
                    keys = key.split('.')
                    nested_value = doc
                    try:
                        for nested_key in keys:
                            nested_value = nested_value[nested_key]
                        if isinstance(value, dict) and '$in' in value:
                            if not isinstance(nested_value, list):
                                match = False
                                break
                            # Check if any value in the $in array is present in the nested_value list
                            if not any(item in nested_value for item in value['$in']):
                                match = False
                                break
                        elif isinstance(value, dict) and '$gte' in value:
                            if nested_value < value['$gte']:
                                match = False
                                break
                        elif isinstance(value, dict) and '$lte' in value:
                            if nested_value > value['$lte']:
                                match = False
                                break
                        elif nested_value != value:
                            match = False
                            break
                    except (KeyError, TypeError):
                        match = False
                        break
                elif key not in doc:
                    match = False
                    break
                elif doc[key] != value:
                    match = False
                    break
            if match:
                results.append({'_id': doc_id, **doc})
        return results
    
    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None
    
    def update_one(self, query, update):
        results = self.find(query)
        if results:
            doc_id = results[0]['_id']
            if '$push' in update:
                for key, value in update['$push'].items():
                    if key not in self.data_store[doc_id]:
                        self.data_store[doc_id][key] = []
                    self.data_store[doc_id][key].append(value)
            if '$pull' in update:
                for key, value in update['$pull'].items():
                    if key in self.data_store[doc_id]:
                        try:
                            self.data_store[doc_id][key].remove(value)
                        except ValueError:
                            pass
            return {'modified_count': 1}
        return {'modified_count': 0}

# Mock collections
activities_collection = MockCollection(activities_data)
teachers_collection = MockCollection(teachers_data)

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Dive into epic adventures, romance, mystery, and supernatural worlds! Discover legendary heroes, complex villains, and unforgettable journeys through the captivating art of Japanese manga storytelling.",
        "schedule": "Tuesdays, 7:00 PM - 8:00 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:00"
        },
        "max_participants": 15,
        "participants": []
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

