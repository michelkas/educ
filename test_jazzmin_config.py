#!/usr/bin/env python
"""
Test script to verify Jazzmin configuration
Validates CSS files and Jazzmin settings
"""

import os
import sys
from pathlib import Path

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from django.core.management import call_command

def check_static_files():
    """Check if all CSS files exist"""
    print("✓ Checking static files...")
    base_path = Path(settings.BASE_DIR) / 'static' / 'assets' / 'css'
    
    required_files = [
        'jazzmin-dark-theme.css',
        'admin-forms-dark.css',
        'jazzmin-animations.css',
    ]
    
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ {filename} NOT FOUND!")
            return False
    
    return True

def check_jazzmin_settings():
    """Check Jazzmin settings configuration"""
    print("\n✓ Checking Jazzmin settings...")
    
    jazzmin_settings = settings.JAZZMIN_SETTINGS
    
    required_settings = {
        'theme': 'darkly',
        'changeform_format': 'vertical_tabs',
        'custom_css': 'assets/css/jazzmin-dark-theme.css',
    }
    
    for key, expected_value in required_settings.items():
        value = jazzmin_settings.get(key)
        if value == expected_value:
            print(f"  ✓ {key} = {value}")
        else:
            print(f"  ✗ {key} = {value} (expected: {expected_value})")
            return False
    
    return True

def check_admin_templates():
    """Check if admin templates exist"""
    print("\n✓ Checking admin templates...")
    
    base_path = Path(settings.BASE_DIR) / 'templates' / 'admin'
    
    required_templates = [
        'base_site.html',
    ]
    
    for template in required_templates:
        template_path = base_path / template
        if template_path.exists():
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} NOT FOUND!")
            return False
    
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("Jazzmin Dark Theme Configuration Validator")
    print("=" * 60)
    
    checks = [
        ("Static Files", check_static_files),
        ("Jazzmin Settings", check_jazzmin_settings),
        ("Admin Templates", check_admin_templates),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! Jazzmin is properly configured.")
        print("\nYou can now access the admin panel at:")
        print("  http://localhost:8000/admin/")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
