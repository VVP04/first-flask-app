import json
import sys
import uuid

class UserRepository():
    def __init__(self):
        self.users = json.load(open("./users.json", 'r'))

    def get_content(self):
        return self.users

    def find(self, id):
        try:
            for user in self.users:
                if id == str(user['id']):
                    return user
        except KeyError:
            sys.stderr.write(f'Wrong post id: {id}')
            raise

    def save(self, new_user):
        if not (new_user.get('name') and new_user.get('email')):
            raise Exception(f'Wrong data: {new_user}')  # Changed json.loads to direct use
        
        # Update existing user
        if new_user.get('id'):
            current_user = self.find(new_user['id'])
            if current_user:  # Check if user exists
                index = self.users.index(current_user)  # Find the index
                self.users[index] = new_user  # Replace at found index
            else:
                raise ValueError(f"User with ID {new_user['id']} not found")
        # Add new user
        else:
            new_user['id'] = str(uuid.uuid4())
            self.users.append(new_user)
        
        # Save to file
        with open("./users.json", "w") as f:
            json.dump(self.users, f)
        return new_user['id']