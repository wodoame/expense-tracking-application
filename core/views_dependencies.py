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
from .utils import record
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpRequest

