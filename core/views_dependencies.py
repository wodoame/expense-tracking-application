from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, Category
import core.datechecker as dc 
from django.core.paginator import Paginator 
from django.db.models import Count
from .forms import *
from .serializers import * 
from django.contrib import messages 
import json
import pandas as pd
from .stats import * 
from .utils import *
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpRequest
from calendar import Calendar
from django.template.loader import render_to_string
from django.http import JsonResponse
from urllib.parse import urlparse, unquote
from django.core.cache import cache
from .placeholder_views import AllExpenditures
import re
from .user_settings_schemas import * 
from api.utils import indexEventEmitter
from api.views import Search as APISearch
