import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_subtask_time_update():
    # 1. Create a memo with a subtask
    memo_data = {
        "title": "Test Memo Time Save",
        "content": "Testing subtask time save",
        "category": "work",
        "subtasks": [
            {
                "content": "Subtask 1",
                "is_completed": False
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/memos/", json=memo_data)
    assert response.status_code == 200
    memo = response.json()
    memo_id = memo['id']
    subtask_id = memo['subtasks'][0]['id']
    print(f"Created memo {memo_id} with subtask {subtask_id}")
    
    # 2. Update subtask with completed_at
    now_iso = datetime.now().isoformat()
    update_data = {
        "subtasks": [
            {
                "id": subtask_id,
                "content": "Subtask 1",
                "is_completed": True,
                "completed_at": now_iso
            }
        ]
    }
    
    response = requests.put(f"{BASE_URL}/memos/{memo_id}", json=update_data)
    if response.status_code != 200:
        print(f"Update failed: {response.text}")
        exit(1)
        
    updated_memo = response.json()
    updated_subtask = updated_memo['subtasks'][0]
    
    print(f"Updated completed_at: {updated_subtask['completed_at']}")
    
    if updated_subtask['completed_at'] is None:
        print("FAIL: completed_at is None")
    else:
        print("SUCCESS: completed_at saved")
        
    # 3. Update subtask clearing completed_at
    update_data_clear = {
        "subtasks": [
            {
                "id": subtask_id,
                "content": "Subtask 1",
                "is_completed": False,
                "completed_at": None
            }
        ]
    }
    
    response = requests.put(f"{BASE_URL}/memos/{memo_id}", json=update_data_clear)
    updated_memo_clear = response.json()
    updated_subtask_clear = updated_memo_clear['subtasks'][0]
    
    print(f"Cleared completed_at: {updated_subtask_clear['completed_at']}")
    
    if updated_subtask_clear['completed_at'] is None:
        print("SUCCESS: completed_at cleared")
    else:
        print("FAIL: completed_at not cleared")

    # Clean up
    requests.delete(f"{BASE_URL}/memos/{memo_id}")

if __name__ == "__main__":
    test_subtask_time_update()
