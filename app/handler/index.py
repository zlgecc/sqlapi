# coding: utf-8
from sanic import Blueprint
router = Blueprint("index")

@router.route("/", methods=['GET'])
async def index(request):
    return 'welcome to use'

