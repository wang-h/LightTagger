#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uvicorn
import json
import random
import math
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from src.data import DataLoader
from src.config import get_json
from src.utils import divide_n_package
########################################################
#                     app初始化                         #
########################################################
app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
# 调用jinja2里的模版，帮助渲染前端页面
templates = Jinja2Templates(directory="frontend/templates")

# 挂载配置文件
app.config = get_json("config.json")
tag_id_mapping = {x[0]: i for i, x in enumerate(app.config['tags'])}
# 挂载文本数据
app.examples = DataLoader().read_CoNLL_format_files(
    app.config['data_path'], tag_id_mapping)
sample_num = 5


class TagIDs(BaseModel):
    # put保存tag_ids等方法中请求体样式定义
    sid: int
    tag_ids: List[int] = None


# 对于欢迎页面的渲染处理，将文件信息传回主页面
# async是fastapi的支持异步的声明定义关键字
@app.get('/')
async def index(request: Request):
    data = app.config["project_detail"]
    return templates.TemplateResponse("hello.html", {"request": request, "data": data})

# 为了实现轻量级开箱即用， 对于标注页面调用jinja2的进行渲染处理，将template传回主页面
@app.get('/task/')
async def labeling(request: Request):
    # 每次返回100个句子
    data = {
        "total_package_num": math.ceil(float(len(app.examples))/sample_num)-1,
        "tag_id_mapping": tag_id_mapping,
        "samples": list(divide_n_package(list(range(len(app.examples))), sample_num)),
        "update_api_url": "update",
    }
    return templates.TemplateResponse("task.html", {"request": request, "jdata": data})


# 纯API，将json格式的sentence传回主页面
@app.get('/sentence/{sid}')
async def getSentence(request: Request, sid: int):
    tokens, tag_ids = app.examples[sid]
    data = {
        "sid": sid,
        'tokens': tokens,
        "tag_ids": tag_ids,
        "length": len(tokens)
    }
    return {"data": data}

# 纯API，获取客户端标注结果，处理客户端发来的json并解析，更新标注记录
@app.put('/update/sentence')
async def submit_labeling(request: Request, item: TagIDs):
    # 更新tags
    prev_tag_ids = app.examples[item.sid][1]
    app.examples[item.sid][1] = tuple(item.tag_ids)

    return {
        'status': 'success',
        'prev_tag_ids': prev_tag_ids,
        'new_tag_ids': item.tag_ids
    }


@app.post('/save')
async def save(request: Request):
    path, success = DataLoader.save_CoNLL_format_files(
        app.config['data_path'], app.examples, tag_id_mapping)
    status = 'success' if success else 'fault'
    return {
        'status': status,
        'path': path
    }


@app.get('/help')
async def help(request: Request):
    return templates.TemplateResponse("help.html", {"request": request, "message": '使用帮助'})


if __name__ == "__main__":
    # 重定义jinja2里的模版重用标签，从 "{{, }}" 变为 "[[, ]]"
    templates.env.variable_start_string = '[['
    templates.env.variable_end_string = ']]'
    # 启动程序：
    uvicorn.run(app=app, host="127.0.0.1", port=8080)
    # 或者命令行：
    # uvicorn main:app --reload
