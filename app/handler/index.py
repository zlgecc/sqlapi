# coding: utf-8
from sanic import Blueprint
from app.handler.base import success, error, hash_md5, encode_token
from sanic import response

router = Blueprint("index")

@router.route("/", methods=['GET'])
async def index(request):
    return 'welcome to use'
    with open('./index.html', 'r') as file:
        html = file.read()
        return response.html(html)
    
