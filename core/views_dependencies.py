from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, Category
import core.datechecker as dc 
from django.core.paginator import Paginator 
from django.db.models import Count
from .forms import AddProductForm
from .serializers import ProductSerializer, CategorySerializer
from django.contrib import messages 
import json
import pandas as pd
from .stats import Context, WeeklyStats
from .utils import record, login_required, getRecordSkeletonContext
from django.utils.decorators import method_decorator
from django.http import HttpRequest
from calendar import Calendar
from django.template.loader import render_to_string
from django.http import JsonResponse
from urllib.parse import urlparse