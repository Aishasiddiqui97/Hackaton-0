#!/usr/bin/env python3
"""
Semi-Autonomous Social Media Manager - Main Orchestrator
Production-ready HITL (Human-in-the-Loop) Architecture
"""

import os
import sys
import time
import json
import asyncio
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Scripts.platform_manager import PlatformManager
from Scripts.session_manager import SessionManager
from Sc