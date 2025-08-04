#!/usr/bin/env python3
"""
Test script to verify bot functionality
"""
import asyncio
import logging
from datetime import datetime, timedelta

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_database():
    """Test database functions"""
    print("🧪 Testing database functions...")
    
    try:
        import database
        
        # Initialize database
        await database.init_db()
        print("✅ Database initialized successfully")
        
        # Test user functions
        test_user_id = 123456789
        await database.add_or_update_user(test_user_id, 'fa')
        print("✅ User added successfully")
        
        # Test premium functions
        is_premium = await database.is_user_premium(test_user_id)
        print(f"✅ Premium status check: {is_premium}")
        
        # Test post count functions
        can_send, remaining = await database.can_user_send_post(test_user_id)
        print(f"✅ Post limit check: can_send={can_send}, remaining={remaining}")
        
        print("✅ All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

async def test_texts():
    """Test text functions"""
    print("🧪 Testing text functions...")
    
    try:
        from texts import get_text
        
        # Test Persian texts
        fa_text = get_text('welcome', 'fa')
        print(f"✅ Persian text: {fa_text}")
        
        # Test English texts
        en_text = get_text('welcome', 'en')
        print(f"✅ English text: {en_text}")
        
        # Test premium texts
        premium_text = get_text('premium_management_menu', 'fa')
        print(f"✅ Premium menu text: {premium_text}")
        
        print("✅ All text tests passed!")
        
    except Exception as e:
        print(f"❌ Text test failed: {e}")
        return False
    
    return True

async def test_keyboards():
    """Test keyboard functions"""
    print("🧪 Testing keyboard functions...")
    
    try:
        from keyboards import (
            get_main_menu_keyboard, 
            get_premium_management_keyboard,
            get_premium_duration_keyboard
        )
        
        # Test main menu keyboard
        main_kb = get_main_menu_keyboard('fa')
        print("✅ Main menu keyboard created")
        
        # Test premium management keyboard
        premium_kb = get_premium_management_keyboard('fa')
        print("✅ Premium management keyboard created")
        
        # Test duration keyboard
        duration_kb = get_premium_duration_keyboard('fa')
        print("✅ Duration keyboard created")
        
        print("✅ All keyboard tests passed!")
        
    except Exception as e:
        print(f"❌ Keyboard test failed: {e}")
        return False
    
    return True

async def test_config():
    """Test configuration"""
    print("🧪 Testing configuration...")
    
    try:
        from config import FREE_USER_POST_LIMIT, DEVELOPER_ID
        
        print(f"✅ Free user post limit: {FREE_USER_POST_LIMIT}")
        print(f"✅ Developer ID: {DEVELOPER_ID}")
        
        if FREE_USER_POST_LIMIT == 10:
            print("✅ Post limit is correctly set to 10")
        else:
            print(f"⚠️ Post limit is {FREE_USER_POST_LIMIT}, expected 10")
        
        print("✅ Configuration test passed!")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting bot functionality tests...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Texts", test_texts),
        ("Keyboards", test_keyboards),
        ("Database", test_database),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} tests...")
        print('='*50)
        
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} tests: PASSED")
            else:
                print(f"❌ {test_name} tests: FAILED")
        except Exception as e:
            print(f"❌ {test_name} tests: FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print('='*50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())