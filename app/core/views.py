"""
Core views
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(req):
    """return successful response"""
    return Response({"healthy": True})
